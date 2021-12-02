
from interface import implements

from . import Sink


class TransformAdapter(implements(Sink)):
    """
    A TransformAdapter wraps a Sink
    When it receives a record it applies the transform,
    and then sends the transformed record to the wrapped Sink
    """

    def __init__(self, inner):
        """
        Creates a new TransformAdapter
        which wraps the provided Sink
        """
        self.inner = inner

    def transform(self, record):
        """
        Transforms the record

        Arguments:
         * record - the value to transform

        Returns the transformed value
        """
        raise RuntimeError("Unimplemented")

    def write(self, records):
        records = [self.transform(record) for record in records]

        return self.inner.write(records)
