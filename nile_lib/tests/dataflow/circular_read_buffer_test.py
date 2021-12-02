from nile_test.dataflow.buffers import CircularReadBuffer


def test_init():
    data = ["test1", "test2", "test3"]
    buf = CircularReadBuffer(buffer_data=list(data))
    assert list(buf.buffer_data) == list(data)
    assert buf.cursor == 0


def test_read():
    buf = CircularReadBuffer(buffer_data=["test1", "test2", "test3"])
    assert buf.cursor == 0
    assert buf.read() == ["test1"]
    assert buf.cursor == 1
    assert buf.read() == ["test2"]
    assert buf.cursor == 2
    assert buf.read() == ["test3"]
    assert buf.cursor == 0
    assert buf.read() == ["test1"]
    assert buf.cursor == 1


def test_read_empty():
    buf = CircularReadBuffer(buffer_data=[])
    assert buf.cursor == 0
    assert buf.read() == []
    assert buf.cursor == 0
