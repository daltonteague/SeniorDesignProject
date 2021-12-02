import time

from nile_test.dataflow import _reset
from nile_test.dataflow.buffers import Buffer
from nile_test.dataflow.pushers import DeterministicPusher, GammaPusher


def test_DPusher_init():
    in_buf = Buffer()
    out_buf = Buffer()
    dpusher = DeterministicPusher(in_buf, out_buf, quantity=1,
                                  retry_delay=0.1, cycle_delay=1)

    assert dpusher.source is in_buf
    assert dpusher.sink is out_buf
    assert dpusher.quantity == 1
    assert dpusher.retry_delay == 0.1
    assert dpusher.cycle_delay == 1


def test_DPusher_run():
    data = ["test1", "test2"]

    in_buf = Buffer()
    out_buf = Buffer()
    in_buf.write(list(data))

    assert list(in_buf.data) == data
    assert list(out_buf.data) == []

    # Retry should not be triggered
    retry_delay = 0.1
    # cycle_delay was tested to work with values greater than 0.06
    # set to 0.1 for safety margin
    cycle_delay = 0.1

    dpusher = DeterministicPusher(in_buf, out_buf, quantity=1,
                                  retry_delay=retry_delay,
                                  cycle_delay=cycle_delay)
    dpusher.start()
    # Offset us to the halfway to the first cycle
    time.sleep(cycle_delay / 2)

    # Wait until halfway after the first cycle
    time.sleep(cycle_delay)
    assert list(in_buf.data) == ["test2"]
    assert list(out_buf.data) == ["test1"]

    # Wait until halfway past the second cycle
    time.sleep(cycle_delay)
    assert list(in_buf.data) == []
    assert list(out_buf.data) == ["test1", "test2"]

    _reset()


def test_GPusher_init():
    in_buf = Buffer()
    out_buf = Buffer()
    gpusher = GammaPusher(in_buf, out_buf, quantity=1,
                          retry_shape=1, cycle_shape=1)

    assert gpusher.source is in_buf
    assert gpusher.sink is out_buf
    assert gpusher.quantity == 1
