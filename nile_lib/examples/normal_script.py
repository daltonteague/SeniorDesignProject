import os
import sys
import requests
sys.path.append(os.path.abspath(".."))

from nile_test.toxiproxy import ToxiProxy, Proxy, Toxic # noqa: E402


# check if the "proxy_without_latency" exists

'''
if requests.get("http://localhost:8474/proxies/proxy_without_latency").ok:
    print("Proxy with out latency exists, deleting")
    requests.delete("http://localhost:8474/proxies/proxy_without_latency")
    print("Deleted")

requests.delete("http://localhost:8474/proxies", proxies={})
'''

hostname = "localhost:8474"
toxiproxy = ToxiProxy(hostname)

toxiproxy.delete_proxies()
print('12345' + str(toxiproxy.get_proxies()) + '45678')

# Check that a ToxiProxy can be found
assert toxiproxy.exists(), f"ToxiProxy server not found at '{hostname}'"
# If this line is reached, the server exists
print(f"Found ToxiProxy server at '{hostname}'")
print(f"URL is '{toxiproxy.get_url()}'")

# Create object representing a Proxy named 'proxy1'
proxy1 = Proxy(toxiproxy, name="proxy_without_latency")

# Check if the ToxiProxy server has a Proxy named 'proxy1'
# If it does, remove it from the server to establish a clean baseline
print("Establishing clean baseline")
if proxy1.exists():
    print("Proxy 'proxy_without_latency' exists, deleting...")
    proxy1.delete()
    print("Finished deleting")
    assert not proxy1.exists(), \
        "A Proxy named 'proxy_without_latency' should not exist on server after delete"
    print("Proxy named 'proxy_without_latency' deleted, baseline is clean")
else:
    print("No Proxy named 'proxy_without_latency' found, baseline is clean")

# Create a Proxy named 'proxy1' on the server
proxy1_upstream = "localhost:8000"
proxy1_listen = "127.0.0.1:8001"

print(f"Creating Proxy named 'proxy_without_latency' on server '{hostname}'")
print(f"upstream='{proxy1_upstream}', listen='{proxy1_listen}'")
print("...")

proxy1.make(
    upstream_address=proxy1_upstream,
    listen_address=proxy1_listen)

print("Finished creating")
print(f"URL is {proxy1.get_url()}")

# Verify that 'proxy1' is now created
assert proxy1.exists(), \
    "A Proxy named 'proxy_without_latency' should exist on server after creation"

# Verify that the server knows the correct upstream value
retrieved_upstream = proxy1.get_upstream()

assert proxy1_upstream == retrieved_upstream, \
    f"Found upstream '{retrieved_upstream}', expected '{proxy1_upstream}'"

# Verify that the server knows the correct listen value
retrieved_listen = proxy1.get_listen()

assert retrieved_listen == proxy1_listen, \
    f"Found listen '{retrieved_listen}', expected '{proxy1_listen}'"

print("Values on server are correct")
