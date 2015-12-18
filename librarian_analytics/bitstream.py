import calendar
import datetime
import logging
import struct

from bitarray import bitarray
from pytz import utc


def pack(fmt, raw_data):
    return struct.pack(fmt, raw_data)


def unpack(fmt, raw_bytes):
    expected_size = struct.calcsize(fmt)
    while len(raw_bytes) < expected_size:
        raw_bytes = '\x00' + raw_bytes
    (value,) = struct.unpack(fmt, raw_bytes)
    return value


def hex_to_bytes(hs):
    chunks = [hs[i:i + 2] for i in range(0, len(hs), 2)]
    return ''.join([chr(int(byte, 16)) for byte in chunks])


def bytes_to_hex(s):
    return ''.join(['{:02x}'.format(ord(c)) for c in s])


def from_utc_timestamp(timestamp):
    """Converts the passed-in unix UTC timestamp into a datetime object."""
    dt = datetime.datetime.utcfromtimestamp(float(timestamp))
    return dt.replace(tzinfo=utc)


def to_utc_timestamp(dt):
    """Converts the passed-in datetime object into a unix UTC timestamp."""
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        msg = "Naive datetime object passed. It is assumed that it's in UTC."
        logging.warning(msg)
    return calendar.timegm(dt.timetuple())


class FieldWrapper(object):
    _index = 0

    def __init__(self, cls, args, kwargs):
        # to preserve order of declaration
        self._index = FieldWrapper._index
        FieldWrapper._index += 1
        self.cls = cls
        self.args = args
        self.kwargs = kwargs

    def instantiate(self, name):
        return self.cls(name=name,
                        index=self._index,
                        *self.args,
                        **self.kwargs)


class BitField(object):

    _deserializers = {
        'integer': lambda x: unpack('>i', x),
        'float': lambda x: unpack('>f', x),
        'timestamp': lambda x: from_utc_timestamp(unpack('>i', x)),
        'hex': lambda x: bytes_to_hex(x),
        'string': lambda x: x,
    }
    _serializers = {
        'integer': lambda x: pack('>i', x),
        'float': lambda x: pack('>f', x),
        'timestamp': lambda x: pack('>i', to_utc_timestamp(x)),
        'hex': lambda x: hex_to_bytes(x),
        'string': lambda x: x,
    }

    def __new__(cls, *args, **kwargs):
        if 'name' in kwargs:
            return super(BitField, cls).__new__(cls, *args, **kwargs)
        return FieldWrapper(cls, args, kwargs)

    def __init__(self, name, index, width, data_type):
        self._name = name
        self._index = index
        self._width = width
        self._data_type = data_type

    @property
    def width(self):
        return self._width

    @property
    def data_type(self):
        return self._data_type

    @property
    def name(self):
        return self._name

    def deserialize(self, bits):
        bits.reverse()
        bits.fill()
        bits.reverse()
        raw = bits.tobytes()
        try:
            fn = self._deserializers[self.data_type]
        except KeyError:
            raise ValueError('Unknown data_type: {}'.format(self.data_type))
        else:
            return fn(raw)

    def serialize(self, value):
        b = bitarray()
        try:
            fn = self._serializers[self.data_type]
        except KeyError:
            raise ValueError('Unknown data_type: {}'.format(self.data_type))
        else:
            b.frombytes(fn(value))
            # cut off unused bits
            return b[b.length() - self.width:]


class BitStream(object):
    # Expected to be overridden by client
    start_marker = None
    end_marker = None
    # Internally used attributes
    _pre_processor_prefix = 'preprocess_'
    _post_processor_prefix = 'postprocess_'

    def __init__(self, data):
        self._data = data
        if self.start_marker is None or self.end_marker is None:
            raise TypeError("Both start_marker and end_marker must be defined")
        if len(self.start_marker) != len(self.end_marker):
            raise ValueError("Use markers of equal length.")
        self._fields = self._collect_fields()

    def _collect_fields(self):
        fields = []
        for name in dir(self):
            attr = getattr(self, name)
            if isinstance(attr, FieldWrapper):
                fields.append(attr.instantiate(name))
        return sorted(fields, key=lambda x: x._index)

    def _from_datagram(self, datagram):
        pos = 0
        data = dict()
        for field in self._fields:
            bits = datagram[pos:pos + field.width]
            deserialized = field.deserialize(bits)
            data[field.name] = self._run_processor(self._post_processor_prefix,
                                                   field.name,
                                                   deserialized)
            pos += field.width
        return data

    def _run_processor(self, prefix, field_name, value):
        processor_name = prefix + field_name
        processor = getattr(self, processor_name, None)
        if callable(processor):
            return processor(value)
        return value

    def deserialize(self):
        bitstream = bitarray()
        bitstream.frombytes(self._data)
        end_pattern = bitarray()
        end_pattern.frombytes(self.end_marker)
        pattern_width = end_pattern.length()
        start = pattern_width
        deserialized = []
        for end in bitstream.itersearch(end_pattern):
            found_start = bitstream[start - pattern_width:start].tobytes()
            if found_start != self.start_marker:
                raise ValueError('Start marker does not match.')
            data = self._from_datagram(bitstream[start:end])
            deserialized.append(data)
            start = end + pattern_width * 2
        return deserialized

    def _to_datagram(self, data):
        datagram = bitarray()
        datagram.frombytes(self.start_marker)
        for field in self._fields:
            value = self._run_processor(self._pre_processor_prefix,
                                        field.name,
                                        data[field.name])
            datagram = datagram + field.serialize(value)
        datagram.frombytes(self.end_marker)
        return datagram

    def serialize(self):
        bitstream = bitarray()
        for item in self._data:
            bitstream = bitstream + self._to_datagram(item)
        return bitstream.tobytes()

    @classmethod
    def from_bytes(cls, raw_bytes):
        instance = cls(raw_bytes)
        return instance.deserialize()

    @classmethod
    def to_bytes(cls, raw_data):
        instance = cls(raw_data)
        return instance.serialize()
