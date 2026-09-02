import pytest

from tutor.throttle import Busy, TooManyRequests, Throttle


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


def test_per_user_window_allows_exactly_the_limit_then_raises():
    clock = FakeClock()
    throttle = Throttle(per_user=20, window_s=600, concurrent=100, clock=clock)
    for _ in range(20):
        with throttle.acquire("student"):
            pass
    with pytest.raises(TooManyRequests):
        with throttle.acquire("student"):
            pass


def test_advancing_clock_past_the_window_frees_capacity():
    clock = FakeClock()
    throttle = Throttle(per_user=20, window_s=600, concurrent=100, clock=clock)
    for _ in range(20):
        with throttle.acquire("student"):
            pass
    with pytest.raises(TooManyRequests):
        with throttle.acquire("student"):
            pass
    clock.advance(601)
    with throttle.acquire("student"):
        pass  # window has rolled past the 20 stale entries, so this does not raise


def test_per_user_windows_are_independent():
    clock = FakeClock()
    throttle = Throttle(per_user=1, window_s=600, concurrent=100, clock=clock)
    with throttle.acquire("a"):
        pass
    with throttle.acquire("b"):
        pass  # a different user's own window, unaffected by "a" filling theirs


def test_concurrent_limit_of_one_makes_a_second_acquire_busy():
    clock = FakeClock()
    throttle = Throttle(per_user=100, window_s=600, concurrent=1, clock=clock)
    with throttle.acquire("student"):
        with pytest.raises(Busy):
            with throttle.acquire("other"):
                pass


def test_exit_releases_the_semaphore_for_the_next_acquire():
    clock = FakeClock()
    throttle = Throttle(per_user=100, window_s=600, concurrent=1, clock=clock)
    with throttle.acquire("student"):
        pass
    with throttle.acquire("student"):
        pass  # released when the first `with` exited, so this does not raise Busy


def test_a_busy_rejection_does_not_consume_a_window_slot():
    # per_user=2 leaves window room for a second attempt; concurrent=1 makes that
    # second attempt fail on the semaphore instead. If the window were still counted
    # before the semaphore check, this busy-rejected attempt would wrongly use the
    # user's second (and last) window slot, and the third acquire below - the second
    # request that actually ever went through - would incorrectly raise TooManyRequests.
    clock = FakeClock()
    throttle = Throttle(per_user=2, window_s=600, concurrent=1, clock=clock)
    with throttle.acquire("student"):
        with pytest.raises(Busy):
            with throttle.acquire("student"):
                pass
    with throttle.acquire("student"):
        pass  # only one acquire has ever actually succeeded; this is the second, still within budget
