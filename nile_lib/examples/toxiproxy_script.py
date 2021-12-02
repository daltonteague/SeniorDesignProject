import os
import sys
sys.path.append(os.path.abspath(".."))

from nile_test.toxiproxy import ToxiProxy, Proxy, Toxic  # noqa: E402

hostname = "localhost:8474"
toxiproxy = ToxiProxy(hostname)

# Check that a ToxiProxy can be found
assert toxiproxy.exists(), f"ToxiProxy server not found at '{hostname}'"
# If this line is reached, the server exists
print(f"Found ToxiProxy server at '{hostname}'")
print(f"URL is '{toxiproxy.get_url()}'")

# Create object representing a Proxy named 'proxy1'
proxy1 = Proxy(toxiproxy, name="proxy1")

# Check if the ToxiProxy server has a Proxy named 'proxy1'
# If it does, remove it from the server to establish a clean baseline
print("Establishing clean baseline")
if proxy1.exists():
    print("Proxy 'proxy1' exists, deleting...")
    proxy1.delete()
    print("Finished deleting")
    assert not proxy1.exists(), \
        "A Proxy named 'proxy1' should not exist on server after delete"
    print("Proxy named 'proxy1' deleted, baseline is clean")
else:
    print("No Proxy named 'proxy1' found, baseline is clean")

# Create a Proxy named 'proxy1' on the server
proxy1_upstream = "localhost:8000"
proxy1_listen = "127.0.0.1:8001"

print(f"Creating Proxy named 'proxy1' on server '{hostname}'")
print(f"upstream='{proxy1_upstream}', listen='{proxy1_listen}'")
print("...")

proxy1.make(
    upstream_address=proxy1_upstream,
    listen_address=proxy1_listen)

print("Finished creating")
print(f"URL is {proxy1.get_url()}")

# Verify that 'proxy1' is now created
assert proxy1.exists(), \
    "A Proxy named 'proxy1' should exist on server after creation"

# Verify that the server knows the correct upstream value
retrieved_upstream = proxy1.get_upstream()

assert proxy1_upstream == retrieved_upstream, \
    f"Found upstream '{retrieved_upstream}', expected '{proxy1_upstream}'"

# Verify that the server knows the correct listen value
retrieved_listen = proxy1.get_listen()

assert retrieved_listen == proxy1_listen, \
    f"Found listen '{retrieved_listen}', expected '{proxy1_listen}'"

print("Values on server are correct")

# Attempt to set the upstream
new_upstream = "localhost:8003"

print(f"Setting upstream to '{new_upstream}'...")
proxy1.set_upstream(new_upstream)

retrieved_upstream = proxy1.get_upstream()

assert new_upstream == retrieved_upstream, \
    f"Found upstream '{retrieved_upstream}', expected '{new_upstream}'"
print("Upstream updated correctly")

# Attempt to set the listen
new_listen = "127.0.0.1:8003"

print(f"Setting listen to '{new_listen}'")
proxy1.set_listen(new_listen)

retrieved_listen = proxy1.get_listen()

assert retrieved_listen == new_listen, \
    f"Found listen '{retrieved_listen}', expected '{new_listen}'"

print("Listen updated correctly")


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
print(f"t_type='{toxic1_type}'")
print(f"stream='{toxic1_stream}'")
print(f"toxicity='{toxic1_toxicity}''")
print(f"attributes='{toxic1_attributes}'")

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


# Attempt to set the toxicity
new_toxicity = 0.5

print(f"Setting toxicity to '{new_toxicity}'...")
toxic1.set_toxicity(new_toxicity)

retrieved_toxicity = toxic1.get_toxicity()

assert new_toxicity == retrieved_toxicity, \
    f"Found upstream '{retrieved_toxicity}', expected '{new_toxicity}'"
print("Toxicity updated correctly")


# Attempt to set the attributes
new_attributes = {
    "latency": 5000,
    "jitter": 20
}

print(f"Setting attributes to '{new_attributes}'...")
toxic1.set_attributes(new_attributes)

retrieved_attributes = toxic1.get_attributes()

assert new_attributes == retrieved_attributes, \
    f"Found upstream '{retrieved_attributes}', expected '{new_attributes}'"
print("Attributes updated correctly")
