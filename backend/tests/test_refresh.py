"""refresh scheduler: the nightly-run timing helper and the disable switch."""
import threading

import refresh


def test_seconds_until_within_a_day():
    # The next occurrence of any hour is always between now and 24h ahead.
    for hour in (0, 3, 12, 23):
        s = refresh._seconds_until(hour)
        assert 0 < s <= 24 * 3600


def test_start_scheduler_disabled_is_noop():
    # None means disabled: no daemon thread is started.
    refresh.start_scheduler(None)
    assert not any(t.name == "nightly-refresh" for t in threading.enumerate())
