import os
import sys
import requests
sys.path.append(os.path.abspath(".."))

from nile_test.toxiproxy import ToxiProxy, Proxy, Toxic # noqa: E402




hostname = "localhost:8474"
toxiproxy = ToxiProxy(hostname)

toxiproxy.delete_proxies()

# Check that a ToxiProxy can be found
assert toxiproxy.exists(), f"ToxiProxy server not found at '{hostname}'"
# If this line is reached, the server exists
print(f"Found ToxiProxy server at '{hostname}'")
print(f"URL is '{toxiproxy.get_url()}'")

# Create object representing a Proxy named 'proxy1'
proxy1 = Proxy(toxiproxy, name="proxy_with_latency")

# Check if the ToxiProxy server has a Proxy named 'proxy1'
# If it does, remove it from the server to establish a clean baseline
print("Establishing clean baseline")
if proxy1.exists():
    print("Proxy 'proxy_with_latency' exists, deleting...")
    proxy1.delete()
    print("Finished deleting")
    assert not proxy1.exists(), \
        "A Proxy named 'proxy_with_latency' should not exist on server after delete"
    print("Proxy named 'proxy_with_latency' deleted, baseline is clean")
else:
    print("No Proxy named 'proxy_with_latency' found, baseline is clean")

# Create a Proxy named 'proxy1' on the server
proxy1_upstream = "localhost:8000"
proxy1_listen = "127.0.0.1:8001"

print(f"Creating Proxy named 'proxy_with_latency' on server '{hostname}'")
print(f"upstream='{proxy1_upstream}', listen='{proxy1_listen}'")
print("...")

proxy1.make(
    upstream_address=proxy1_upstream,
    listen_address=proxy1_listen)

print("Finished creating")
print(f"URL is {proxy1.get_url()}")

# Verify that 'proxy_with_latency' is now created
assert proxy1.exists(), \
    "A Proxy named 'proxy_with_latency' should exist on server after creation"

# Verify that the server knows the correct upstream value
retrieved_upstream = proxy1.get_upstream()

assert proxy1_upstream == retrieved_upstream, \
    f"Found upstream '{retrieved_upstream}', expected '{proxy1_upstream}'"

# Verify that the server knows the correct listen value
retrieved_listen = proxy1.get_listen()

assert retrieved_listen == proxy1_listen, \
    f"Found listen '{retrieved_listen}', expected '{proxy1_listen}'"

print("Values on server are correct")


toxic1 = Toxic(proxy1, name="toxic1")

# Check if the Proxy has a Toxic named 'toxic1'
# If it does, remove it from the proxy to establish a clean baseline
print("Establishing clean baseline")
if toxic1.exists():
    print("Toxic 'toxic1' exists, deleting...")
    toxic1.delete()
    print("Finished deleting")
    assert not toxic1.exists(), \
        "A Toxic named 'toxic1' should not exist on server after delete"
    print("Toxic named 'toxic1' deleted, baseline is clean")
else:
    print("No Toxic named 'toxic1' found, baseline is clean")

toxic1_type = "latency"
toxic1_stream = "downstream"
toxic1_toxicity = 1
toxic1_attributes = {
    "latency": 2000,
    "jitter": 0
}

print(f"Creating Toxic named 'proxy1' on proxy '{proxy1.name}'")
print(f"t_type='{toxic1_type}', stream='{toxic1_stream}', toxicity='{toxic1_toxicity}', attributes='{toxic1_attributes}'")
print("...")

toxic1.make(
    t_type=toxic1_type,
    stream=toxic1_stream,
    toxicity=toxic1_toxicity,
    attributes=toxic1_attributes)

print("Finished creating")
print(f"URL is {toxic1.get_url()}")

# Verify that 'proxy1' is now created
assert toxic1.exists(), \
    "A Toxic named 'toxic1' should exist on server after creation"


# Verify that the server knows the correct type value
retrieved_type = toxic1.get_type()

assert toxic1_type == retrieved_type, \
    f"Found type '{retrieved_type}', expected '{toxic1_type}'"

# Verify that the server knows the correct stream value
retrieved_stream = toxic1.get_stream()

assert retrieved_stream == toxic1_stream, \
    f"Found listen '{retrieved_stream}', expected '{toxic1_stream}'"

# Verify that the server knows the correct toxicity value
retrieved_toxicity = toxic1.get_toxicity()

assert retrieved_toxicity == toxic1_toxicity, \
    f"Found listen '{retrieved_toxicity}', expected '{toxic1_toxicity}'"

# Verify that the server knows the correct attributes value
retrieved_attributes = toxic1.get_attributes()

assert retrieved_attributes == toxic1_attributes, \
    f"Found listen '{retrieved_attributes}', expected '{toxic1_attributes}'"

print("Values on server are correct")
