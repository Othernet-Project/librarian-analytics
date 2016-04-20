import types

import pytest

try:
    from unittest import mock
except ImportError:
    import mock

from librarian_analytics import helpers as mod


@pytest.fixture
def populated_database(random_dataset, databases):
    test_data = list(random_dataset())
    databases.load_fixtures('analytics', 'stats', [d.row for d in test_data])
    return test_data, databases


# DATABASE


def test_get_stats(populated_database):
    test_data, databases = populated_database
    stats = mod.get_stats(databases.analytics, limit=None)
    raw_payload = stats[0]['payload']
    payload = bytes(raw_payload)
    assert isinstance(raw_payload, types.BufferType)
    assert len(stats) == len(test_data)
    assert payload in [d.payload for d in test_data]


def test_save_stats(random_datapoint, databases):
    data = {
        'time': random_datapoint.timestamp,
        'payload': random_datapoint.payload
    }
    mod.save_stats(databases.analytics, data)
    stats = mod.get_stats(databases.analytics, limit=None)
    assert len(stats) == 1
    assert bytes(stats[0]['payload']) == random_datapoint.payload


def test_clear_transmitted(populated_database):
    test_data, databases = populated_database
    stats = mod.get_stats(databases.analytics, limit=None)
    # We want to set one item aside to prevent it from being cleared
    first = stats.pop(0)
    ids = [s['id'] for s in stats]
    mod.clear_transmitted(databases.analytics, ids)
    stats = mod.get_stats(databases.analytics, limit=None)
    assert len(stats) == 1
    assert stats[0]['id'] == first['id']


def test_clear_transmitted_with_no_ids(populated_database):
    test_data, databases = populated_database
    mod.clear_transmitted(databases.analytics, [])
    stats = mod.get_stats(databases.analytics, len(test_data))
    assert len(stats) == len(test_data)  # original number of items


def test_get_stats_bitstream(populated_database):
    test_data, databases = populated_database
    unpacked = sum([mod.StatBitStream(d.payload).deserialize()
                    for d in sorted(test_data, key=lambda x: x.timestamp)], [])
    expected_stream = mod.StatBitStream(unpacked).serialize()
    ids, bitstream = mod.get_stats_bitstream(databases.analytics, limit=None)
    assert len(list(ids)) == len(test_data)
    assert bitstream == expected_stream


def test_get_stats_bitstream_empty_database(databases):
    ids, bitstream = mod.get_stats_bitstream(databases.analytics, limit=None)
    assert len(list(ids)) == 0
    assert bitstream == b''


# DEVICE ID


def test_prepare_device_id(random_path, helpers):
    pdid = helpers.undecorate(mod.prepare_device_id)
    with mock.patch.object(mod, 'generate_device_id') as gdid:
        gdid.return_value = 'foo'
        ret = pdid(random_path)
        assert ret == 'foo'


def test_prepare_device_id_only_generates_once(random_path, helpers):
    pdid = helpers.undecorate(mod.prepare_device_id)
    with mock.patch.object(mod, 'generate_device_id') as gdid:
        gdid.return_value = 'foo'
        pdid(random_path)
        pdid(random_path)
        gdid.assert_called_once_with()


# PAYLOAD


def test_get_payload(random_path, populated_database):
    device_id = mod.serialized_device_id(random_path)
    test_data, databases = populated_database
    unpacked = sum([mod.StatBitStream(d.payload).deserialize()
                    for d in sorted(test_data, key=lambda x: x.timestamp)], [])
    expected_stream = mod.StatBitStream(unpacked).serialize()
    ids, payload = mod.get_payload(databases.analytics,
                                   random_path,
                                   limit=None)
    assert len(list(ids)) == len(test_data)
    assert payload == device_id + expected_stream
