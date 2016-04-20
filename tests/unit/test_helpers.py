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


# GENERAL


@pytest.mark.parametrize('max,ret', [
    (3, [True, True, True, False, False, False]),
    (4, [True, True, True, True, False, False]),
    (2, [True, True, False, False, False, False]),
    (6, [True, True, True, True, True, True]),
])
def test_counter(max, ret):
    c = mod.counter(max)
    results = []
    for i in range(6):
        results.append(c())
    assert results == ret


def test_counter_zero():
    c = mod.counter(0)
    assert c() is False
    assert c() is False


@pytest.mark.parametrize('size,out', [
    (2, [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]]),
    (3, [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]]),
    (5, [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]]),
    (10, [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]),
    (20, [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]),
    (0, []),
])
def test_batch(size, out):
    source = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert list(mod.batches(source, size)) == out
