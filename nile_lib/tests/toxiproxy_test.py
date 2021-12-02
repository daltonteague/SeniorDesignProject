import pytest

from nile_test.toxiproxy import ToxiProxy, Proxy, Toxic

HOSTNAME = "localhost:8474"
TOXIPROXY = ToxiProxy(HOSTNAME)

TOXIPROXY_UNAVAILABLE = not TOXIPROXY.exists()
TOXIPROXY_REASON = f"Could not find ToxiProxy server at '{HOSTNAME}'"


def test_no_toxiproxy():
    assert not ToxiProxy("localhost:20").exists()


@pytest.mark.skipif(TOXIPROXY_UNAVAILABLE, reason=TOXIPROXY_REASON)
def test_basic_info():
    assert f"http://{HOSTNAME}" == TOXIPROXY.get_url()


@pytest.mark.skipif(TOXIPROXY_UNAVAILABLE, reason=TOXIPROXY_REASON)
def test_proxy_creation():
    TOXIPROXY.delete_proxies()
    proxy1 = Proxy(TOXIPROXY, name="proxy1")

    proxy1_upstream = "localhost:8000"
    proxy1_listen = "127.0.0.1:8001"

    proxy1.make(
        upstream_address=proxy1_upstream,
        listen_address=proxy1_listen)

    assert proxy1.exists(), \
        "A Proxy named 'proxy1' should exist on server after creation"

    retrieved_upstream = proxy1.get_upstream()

    assert proxy1_upstream == retrieved_upstream, \
        f"Found upstream '{retrieved_upstream}', expected '{proxy1_upstream}'"

    retrieved_listen = proxy1.get_listen()

    assert retrieved_listen == proxy1_listen, \
        f"Found listen '{retrieved_listen}', expected '{proxy1_listen}'"


@pytest.mark.skipif(TOXIPROXY_UNAVAILABLE, reason=TOXIPROXY_REASON)
def test_proxy_update():
    TOXIPROXY.delete_proxies()
    proxy1 = Proxy(TOXIPROXY, name="proxy1")

    proxy1_upstream = "localhost:8000"
    proxy1_listen = "127.0.0.1:8001"

    proxy1.make(
        upstream_address=proxy1_upstream,
        listen_address=proxy1_listen)

    new_upstream = "localhost:8003"
    proxy1.set_upstream(new_upstream)

    retrieved_upstream = proxy1.get_upstream()
    assert new_upstream == retrieved_upstream, \
        f"Found upstream '{retrieved_upstream}', expected '{new_upstream}'"

    new_listen = "127.0.0.1:8003"
    proxy1.set_listen(new_listen)

    retrieved_listen = proxy1.get_listen()
    assert retrieved_listen == new_listen, \
        f"Found listen '{retrieved_listen}', expected '{new_listen}'"


@pytest.mark.skipif(TOXIPROXY_UNAVAILABLE, reason=TOXIPROXY_REASON)
def test_toxic_creation():
    TOXIPROXY.delete_proxies()
    proxy1 = TOXIPROXY.create_proxy("proxy1",
                                    upstream_address="localhost:8000",
                                    listen_address="127.0.0.1:8001")

    toxic1 = Toxic(proxy1, name="toxic1")

    assert not toxic1.exists()

    toxic1_type = "latency"
    toxic1_stream = "downstream"
    toxic1_toxicity = 1
    toxic1_attributes = {
        "latency": 2000,
        "jitter": 0
    }

    toxic1.make(
        t_type=toxic1_type,
        stream=toxic1_stream,
        toxicity=toxic1_toxicity,
        attributes=toxic1_attributes)

    assert toxic1.exists(), \
        "A Toxic named 'toxic1' should exist on server after creation"

    # Check all getter values
    retrieved_type = toxic1.get_type()
    assert toxic1_type == retrieved_type, \
        f"Found type '{retrieved_type}', expected '{toxic1_type}'"

    retrieved_stream = toxic1.get_stream()
    assert retrieved_stream == toxic1_stream, \
        f"Found stream '{retrieved_stream}', expected '{toxic1_stream}'"

    retrieved_toxicity = toxic1.get_toxicity()
    assert retrieved_toxicity == toxic1_toxicity, \
        f"Found toxicity '{retrieved_toxicity}', expected '{toxic1_toxicity}'"

    retrieved_attributes = toxic1.get_attributes()
    assert retrieved_attributes == toxic1_attributes, \
        f"Found attributes '{retrieved_attributes}', \
            expected '{toxic1_attributes}'"


@pytest.mark.skipif(TOXIPROXY_UNAVAILABLE, reason=TOXIPROXY_REASON)
def test_toxic_update():
    TOXIPROXY.delete_proxies()
    proxy1 = TOXIPROXY.create_proxy("proxy1",
                                    upstream_address="localhost:8000",
                                    listen_address="127.0.0.1:8001")

    assert proxy1.exists()

    toxic1 = proxy1.create_toxic("toxic1",
                                 t_type="latency",
                                 stream="downstream",
                                 toxicity=1,
                                 attributes={
                                    "latency": 2000,
                                    "jitter": 0
                                 })

    assert toxic1.exists()

    # Attempt to set the toxicity
    new_toxicity = 0.5

    toxic1.set_toxicity(new_toxicity)
    retrieved_toxicity = toxic1.get_toxicity()
    assert new_toxicity == retrieved_toxicity, \
        f"Found upstream '{retrieved_toxicity}', expected '{new_toxicity}'"

    # Attempt to set the attributes
    new_attributes = {
        "latency": 5000,
        "jitter": 20
    }
    toxic1.set_attributes(new_attributes)
    retrieved_attributes = toxic1.get_attributes()
    assert new_attributes == retrieved_attributes, \
        f"Found upstream '{retrieved_attributes}', expected '{new_attributes}'"
