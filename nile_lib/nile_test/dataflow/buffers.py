from collections import deque
from interface import implements

from . import Source, Sink


class CircularReadBuffer(implements(Source)):
    """
    A CircularReadBuffer is a read-only Source
    that wraps a sequence of data and has a cursor

    When data is read returns the current cursor value
    and then moves the cursor forward
    """

    def __init__(self, buffer_data):
        """
        Creates a CircularReadBuffer that wraps data

        Arguments:
         * buffer_data - the sequence data being wrapped
        """
        self.buffer_data = buffer_data
        self.cursor = 0

    def read(self, num=1):
        result = []

        if self.buffer_data:
            for i in range(num):
                result.append(self.buffer_data[self.cursor])

                self.cursor += 1
                self.cursor %= len(self.buffer_data)

        return result


OLDEST = 'oldest'
NEWEST = 'newest'

_options = (OLDEST, NEWEST)
_error_msg = f"yield_next and drop_next must be '{OLDEST}' or '{NEWEST}'"


class Buffer(implements(Source, Sink)):
    """
    A Read/Write Buffer that can be extensively configured
    """

    def __init__(self, yield_next=OLDEST, drop_next=OLDEST, capacity=None):
        """
        Creates a Buffer with configurable policies

        Arguments
         * yield_next - determines whether the oldest or newest value
            is returned by the next read().
            Default is OLDEST, which is the FIFO configuration
         * drop_next - determines whether the oldest or newest value
            is dropped if the buffer exceeds capacity
            DEFAULT is OLDEST
         * capacity - determines the maximum capacity of the buffer
            DEFAULT is None, which means the buffer is unbounded
        """
        if yield_next not in _options or drop_next not in _options:
            raise ValueError()

        self.yield_next = yield_next
        self.drop_next = drop_next
        self.capacity = capacity

        self.data = deque()

    def _push(self, record):
        """The newest data is appended to the right of the buffer"""
        self.data.append(record)

    def _pop_oldest(self):
        """The oldest data is available from the left of the buffer"""
        return self.data.popleft()

    def _pop_newest(self):
        """The newest data is available form the right of the buffer"""
        return self.data.pop()

    def read(self, num=1):
        result = []

        for i in range(num):
            if self.data:
                if self.yield_next == OLDEST:
                    result.append(self._pop_oldest())
                else:
                    result.append(self._pop_newest())
            else:
                break

        return result

    def write(self, records):
        for record in records:
            self._write_one(record)

        # Return True because Buffer never blocks
        return True

    def _write_one(self, record):
        """ writes one record to self.data """
        if self.capacity:
            self._ensure_capacity()

        self._push(record)

    def _ensure_capacity(self):
        """ Removes records until there is at least 1 capacity left """
        while len(self.data) >= self.capacity:
            if self.drop_next == OLDEST:
                self.data.popleft()
            else:
                self.data.pop()
