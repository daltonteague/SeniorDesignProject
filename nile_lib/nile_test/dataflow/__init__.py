"""
# Dataflow Components Module

## Sources/Sinks

In the dataflow module components can implement two different interfaces,
Sources and Sinks, to describe how they can be used by other components.

The "records" passed into and out of Sinks and Sources
can generally be of arbitrary types.
However some Sinks may make assumptions or have requirements
for what data they can use correctly.

A Sink can have data sent to it, common Sinks include
 * Buffers - which add data to themselves
 * Clients - which send the data to a Server
 * Adapters - which send data to another Sink

A Source can have data read from it, common Sources include
 * CircularBuffers - which can be read from infinitely
 * Buffers - which can have data poped from them

## Workers

If a component needs to be "active" and have its own
behavior that runs it should be a worker.
To define a Worker simply sub-class Worker and
define your run() method with your logic.
"""
from interface import Interface
from locust import events
from gevent.pool import Group


class Source(Interface):
    """
    A Source is something that data can be read from
    """

    def read(self, num=1):
        """
        Read data from a Source

        Arguments
         * num - the maximum number of elements to read

        Returns a list of values read
        """
        pass


class Sink(Interface):
    """
    A Sink is something that data can be written to
    """

    def write(self, records):
        """
        Send data to a Sink

        Arguments:
         * records - an iterable of record values

        Returns True if all values could be written
        Returns False if any value could not be written

        This operation is atomic, either all or none of the records
        are sent

        Write should not fail on values which are never acceptable
        to the Sink, those should be ignored or raise an error.
        Returning false on items which will always be rejected may cause
        a writer to the Sink to loop infinitely.
        """
        pass


# A gevent Group for all dataflow workers
_worker_group = Group()


# A function that kills the worker group
# Should NOT be used by library consumers
def _cleanup():
    print("Nile: Performing Worker Cleanup")
    _worker_group.kill()


def _reset():
    print("Nile: Resetting worker group")
    global _worker_group
    _worker_group.kill()
    _worker_group = Group()


# Binds the _cleanup function to quitting
# This ensures that when locust quits the gevent is cleaned up
events.quitting += _cleanup


class Worker:
    """
    A Worker is a simple wrapper around gevent

    Subclasses must define a run() method to describe
    their behavior.
    This is only called once so repeated behavior must
    use their own loops.

    Using gevent.sleep will not affect other threads
    and can be used to achieve delay behaviors
    """

    def start(self):
        """
        Call to start the Worker in its own gevent
        """
        _worker_group.spawn(self.run)

    def run(self):
        """
        The worker logic
        """
        raise RuntimeError("Unimplemented")
