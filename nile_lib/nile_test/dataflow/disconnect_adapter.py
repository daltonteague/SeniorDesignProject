"""
Adapters are components that act as a transparent connector.

They are Sinks that wrap Sinks

In the case of DisconnectAdapter it is also a Worker,
which means it must be started using the start() method.
This is required so that the scheduling loop can decide
when the next disconnect period will occur.

In the case of TransformAdapter all behavior occurs
within the TransformAdapter.write() method.
It has no concurrent behavior and is not a worker
"""

from interface import implements
from gevent import sleep
from numpy.random import gamma

from . import Sink
from . import Worker


class DisconnectAdapter(Worker, implements(Sink)):
    """
    A DisconnectAdapter wraps a Sink
    When it is connected it passes writes to the wrapped sink
    When it is disconnected it treats writes a blocked

    Each DisconnectAdapter must define how to decide when
    the next disconnect will be and for how long
    """

    def __init__(self, inner):
        """
        Creates a new DisconnectAdapter
        which wraps the provided Sink

        Arguments:
         * inner - the wrapped Sink
        """
        Worker.__init__(self)
        self.inner = inner
        self.connected = True

    def run(self):
        """
        Runs the process that schedules disconnects
        """
        while True:
            time_until, duration = self._next_disconnect()

            # Be connected for time_until seconds
            self.connected = True
            sleep(time_until)
            # Be disconnected for duration seconds
            self.connected = False
            sleep(duration)

    def _next_disconnect(self):
        """
        Returns (time_until, duration)

        Where time_until is the time before the next disconnect
        and duration is the time the disconnect will last
        """
        raise RuntimeError("Unimplemented")

    def write(self, records):
        if self.connected:
            self.inner.write(records)
            return True
        else:
            return False


class DeterministicDisconnectAdapter(DisconnectAdapter):
    """
    A DeterministicDisconnectAdapter (DDA)
    is a DisconnectAdapter that is always connected
    and then disconnected for the same amount of time
    """

    def __init__(self, inner, time_until, duration):
        """
        Creates a DeterministicDisconnectAdapter
        using the given parameters

        Arguments
         * inner - the wrapped Sink
         * time_until - the amount of time it spends connected
            before it becomes disconnected
         * duration - the amount of time it spends disconnected
            before it becomes connected
        """
        DisconnectAdapter.__init__(self, inner)
        self.time_until = time_until
        self.duration = duration

    def _next_disconnect(self):
        return (self.time_until, self.duration)


class GammaDisconnectAdapter(DisconnectAdapter):
    """
    A GammaDisconnectAdapter (GDA)
    is a DisconnectAdapter that samples a Gamma Distribution
    to determine when to be connected and when to be disconnected
    """

    def __init__(self, inner, *,
                 time_until_shape, time_until_scale=1,
                 duration_shape, duration_scale=1):
        """
        Creates a GammaDisconnectAdapter
        using the given parameters

        Arguments
         * inner - the wrapped Sink
         * connect_duration - the amount of time it spends connected
            before it becomes disconnected
         * disconnect_duration - the amount of time it spends disconnected
            before it becomes connected
        """
        DisconnectAdapter.__init__(self, inner)
        self.time_until_shape = time_until_shape
        self.time_until_scale = time_until_scale
        self.duration_shape = duration_shape
        self.duration_scale = duration_scale

    def _next_disconnect(self):
        time_until = gamma(self.time_until_shape, self.time_until_scale)
        duration = gamma(self.duration_shape, self.duration_scale)

        return time_until, duration
