from nile_test.dataflow.buffers import Buffer
from nile_test.dataflow.transform_adapter import TransformAdapter


class DoublingTransformer(TransformAdapter):
    def transform(self, record):
        return record * 2


def test_transforms():
    buf = Buffer()
    assert len(buf.data) == 0

    doubler = DoublingTransformer(buf)
    doubler.write([1, 2, 3])
    assert list(buf.data) == [2, 4, 6]
