from time import sleep

from nile_test.dataflow import _reset
from nile_test.dataflow.buffers import Buffer
from nile_test.dataflow.disconnect_adapter \
    import DeterministicDisconnectAdapter

time_until = 0.01
duration = 0.1


def test_DisAdapter_allows_while_connected():
    buf = Buffer()
    assert len(buf.data) == 0

    dis_adapter = DeterministicDisconnectAdapter(buf, time_until=time_until,
                                                 duration=duration)

    dis_adapter.connected = True
    dis_adapter.write(["test1"])
    assert len(buf.data) == 1


def test_DisAdapter_blocks_while_disconnected():
    buf = Buffer()
    assert len(buf.data) == 0

    dis_adapter = DeterministicDisconnectAdapter(buf, time_until=time_until,
                                                 duration=duration)

    dis_adapter.connected = False
    dis_adapter.write(["test1"])
    assert len(buf.data) == 0


def test_DisAdapter_starts_connected():
    buf = Buffer()
    assert len(buf.data) == 0

    dis_adapter = DeterministicDisconnectAdapter(buf, time_until=time_until,
                                                 duration=duration)
    assert dis_adapter.connected


def test_DisAdapter_becomes_disconnected():
    buf = Buffer()
    assert len(buf.data) == 0

    dis_adapter = DeterministicDisconnectAdapter(buf, time_until=time_until,
                                                 duration=duration)

    dis_adapter.start()

    sleep(time_until + (duration / 2))
    assert not dis_adapter.connected

    _reset()


def test_DisAdapter_reconnects():
    buf = Buffer()
    assert len(buf.data) == 0

    dis_adapter = DeterministicDisconnectAdapter(buf, time_until=time_until,
                                                 duration=duration)

    dis_adapter.start()

    sleep(time_until + duration + (time_until / 2))
    assert dis_adapter.connected

    _reset()
