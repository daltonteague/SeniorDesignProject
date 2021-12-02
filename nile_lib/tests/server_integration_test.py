import sys
import pytest
import requests
import datetime

from nile_test import integration
from nile_test.integration import _is_slave, _is_master
from nile_test.integration.databuffer import DataBuffer
from nile_test.integration.testmanager import TestManager


def test_launch_slave(mocker, monkeypatch):
    mock_tm = mocker.patch.object(TestManager, '__init__')
    mock_db = mocker.patch.object(DataBuffer, '__init__')
    mock_tm.return_value = None
    mock_db.return_value = None
    monkeypatch.setattr(sys, "argv", ["--slave"])

    integration.launch("hostname")

    mock_tm.assert_not_called()
    mock_db.assert_called_with("hostname")


def test_launch_master(mocker, monkeypatch):
    mock_tm = mocker.patch.object(TestManager, '__init__')
    mock_db = mocker.patch.object(DataBuffer, '__init__')
    mock_tm.return_value = None
    mock_db.return_value = None
    monkeypatch.setattr(sys, "argv", ["--master"])

    integration.launch("hostname")
    mock_tm.assert_called_with("hostname")
    mock_db.assert_not_called()


def test_is_slave(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["--slave"])
    assert _is_slave()
    assert not _is_master()


def test_is_master(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["--master"])
    assert not _is_slave()
    assert _is_master()


# also tests start_test
def test_TestManager_init(mocker, monkeypatch):
    monkeypatch.setattr(sys, "argv",
                        ["--expect-slaves=1", "-f", "locustfile.py"])
    mock_post = mocker.patch.object(requests, 'post')
    mock_post.return_value.status_code = 200
    tm = TestManager("localhost")

    assert tm.hostname == "localhost"
    assert tm.slave_count == '1'
    assert tm.start_time is not None
    assert tm.config_file == 'locustfile.py'
    assert tm.arguments == "--expect-slaves=1 -f locustfile.py"

    mock_post.return_value.status_code = 400
    with pytest.raises(RuntimeError):
      tm = TestManager("localhost")

def test_TestManager_finalize_test(mocker):
    mock_post = mocker.patch.object(requests, 'post')
    mock_post.return_value.status_code = 200
    tm = TestManager("localhost")
    assert tm.finalize_test() is None

    mock_post.return_value.status_code = 400
    with pytest.raises(RuntimeError):
        tm.finalize_test()


def test_DataBuffer_init():
    data_buffer1 = DataBuffer("localhost")
    assert data_buffer1.hostname == "localhost"
    assert data_buffer1.buffer_limit == 20
    assert data_buffer1.data_endpoint == "http://localhost/api/v1/requests"
    assert len(data_buffer1.buffer) == 0

    data_buffer2 = DataBuffer("localhost", buffer_limit=30)
    assert data_buffer2.buffer_limit == 30


def test_request_success(mocker):
    data_buffer = DataBuffer("localhost")
    mock_on_request_data = mocker.patch.object(DataBuffer, "_on_request_data")
    data_buffer.request_success("get", "/", 49, 120)
    mock_on_request_data.assert_called_with("get", "/", 49, 120, True, None)


def test_request_failure(mocker):
    data_buffer = DataBuffer("localhost")
    mock_on_request_data = mocker.patch.object(DataBuffer, "_on_request_data")
    data_buffer.request_failure("get", "/", 49, 120, RuntimeError)
    mock_on_request_data.assert_called_with("get", "/", 49, 120, False,
                                            RuntimeError)


def test__on_request_data(mocker):
    mock_post = mocker.patch.object(requests, 'post')
    mock_post.return_value.status_code = 200
    data_buffer = DataBuffer("localhost")

    request_timestamp = datetime.datetime.now().isoformat()

    data_buffer._on_request_data("GET", "/", 0.1, 10, True, None,
                                 request_timestamp=request_timestamp,
                                 request_length=100, status_code=200)

    assert data_buffer.buffer[0]['request_timestamp'] == request_timestamp
    assert data_buffer.buffer[0]['request_length'] == 100
    assert data_buffer.buffer[0]['status_code'] == 200

    for i in range(19):
        data_buffer._on_request_data("GET", "/", 0.1, 10, True, None)

    assert len(data_buffer.buffer) == 20
    data_buffer._on_request_data("GET", "/", 0.1, 10, True, None)
    assert len(data_buffer.buffer) == 0


def test_on_quitting(mocker):
    mock_post = mocker.patch.object(requests, 'post')
    mock_post.return_value.status_code = 200
    data_buffer = DataBuffer("localhost")
    data_buffer._on_request_data("GET", "/", 0.1, 10, True, None)
    data_buffer.on_quitting()

    assert len(data_buffer.buffer) == 0

    mock_post.return_value.status_code = 400
    data_buffer._on_request_data("GET", "/", 0.1, 10, True, None)
    with pytest.raises(RuntimeError):
        data_buffer.on_quitting()
        assert len(data_buffer.buffer) == 1
