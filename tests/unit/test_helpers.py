import pytest

try:
    from unittest import mock
except ImportError:
    import mock

from librarian_analytics import helpers as mod


# DATABASE


@mock.patch.object(mod, 'merge_streams')
@mock.patch.object(mod, 'get_stats')
def test_get_stats_bitstream(get_stats, merge_streams):
    get_stats.return_value = [{'id': 1, 'payload': 'foo'},
                              {'id': 2, 'payload': 'bar'}]
    merge_streams.return_value = 'foobar'
    ids, payload = mod.get_stats_bitstream(db=mock.Mock(), limit=None)
    assert list(ids) == [1, 2]
    assert payload == b'foobar'


@mock.patch.object(mod, 'get_stats')
def test_get_stats_bitstream_no_stats(get_stats):
    get_stats.return_value = []
    assert mod.get_stats_bitstream(db=mock.Mock(), limit=None) == ([], b'')
