import requests
import json


class ToxiProxy:
    """
    The ToxiProxy wrapper contains the location
    of a specific ToxiProxy Server
    """
    def __init__(self, hostname):
        """
        Create a ToxiProxy wrapper
        Note: this does not have any side effects

        Arguments:
         * hostname - the ip:port or domain name of the server
        """
        self.hostname = hostname

    def get_url(self):
        return f"http://{self.hostname}"

    def get_proxies_url(self):
        return f"http://{self.hostname}/proxies"

    def exists(self):
        """
        Checks whether this ToxiProxy server exists and is reachable
        """
        try:
            return requests.get(self.get_proxies_url()).ok
        except requests.exceptions.ConnectionError:
            return False

    def create_proxy(self, name, *, upstream_address, listen_address):
        """
        Create a Proxy on this Server
        If one exists, update it to have the desired attributes
        If it does not, then make it

        Arguments:
         * name - the name of the Proxy on the server
        For the rest of the arguments see Proxy.make()
        """
        proxy = Proxy(self, name)
        if proxy.exists():
            proxy.set_upstream(upstream_address)
            proxy.set_listen(listen_address)
        else:
            proxy.make(upstream_address=upstream_address,
                       listen_address=listen_address)

        return proxy

    def get_proxy(self, name):
        """
        Get a Proxy by name if it exists
        """
        proxy = Proxy(self, name)

        if proxy.exists():
            return proxy
        else:
            return None

    def get_proxies(self):
        """
        Get a list of all proxies
        """
        proxies = requests.get(self.get_proxies_url()).text
        proxies = json.loads(proxies)
        return proxies

    def delete_proxies(self):
        for proxy in self.get_proxies().keys():
            print(proxy)
            requests.delete(f"http://{self.hostname}/proxies/{proxy}")


class Proxy:
    def __init__(self, toxiproxy, name):
        """
        Create a Proxy wrapper
        Note: this does not have any side effects

        Arguments:
         * toxiproxy - the ToxiProxy server the Proxy is on
         * name - the name of the Proxy
        """
        self.toxiproxy = toxiproxy
        self.name = name

    def get_url(self):
        return f"{self.toxiproxy.get_proxies_url()}/{self.name}"

    def get_toxics_url(self):
        return f"{self.get_url()}/toxics"

    def exists(self):
        """
        Checks whether this Proxy exists on the parent server
        """
        return requests.get(self.get_url()).ok

    def make(self, *, upstream_address, listen_address):
        """
        Tries to make this Proxy on the server with the provided values
        Raises RuntimeError if the Proxy already exists

        Arguments:
         * upstream_address - the ip:port or domain name of the upstream
         * listen_address - the ip:port or domain name of the listen
        """
        if self.exists():
            raise RuntimeError("Proxy already exists")

        json = {
            "name": self.name,
            "listen": listen_address,
            "upstream": upstream_address,
            "enabled": True
        }
        requests.post(self.toxiproxy.get_proxies_url(), json=json)

    def delete(self):
        """
        Deletes this Proxy on the Server
        """
        return requests.delete(self.get_url())

    def set_upstream(self, upstream_address):
        """
        Sets the upstream location for this Proxy on the server
        """
        json = {
          "upstream": upstream_address
        }
        url = self.get_url()
        requests.post(url, json=json)

    def get_upstream(self):
        """
        Gets the upstream location for this Proxy from the server
        """
        response = requests.get(self.get_url())
        return response.json().get("upstream")

    def set_listen(self, listen_address):
        """
        Sets the listen location for this Proxy on the server
        """
        json = {
            "listen": listen_address
        }
        url = self.get_url()
        requests.post(url, json=json)

    def get_listen(self):
        """
        Gets the listen location for this Proxy from the server
        """
        response = requests.get(self.get_url())
        return response.json().get("listen")

    def create_toxic(self, name, *, t_type, stream, toxicity, attributes):
        """
        Create a Toxic on this Proxy
        If one exists, delete it, then make the Toxic

        Arguments:
         * name - the name of the Toxic on the Proxy
        For the rest of the arguments see Toxic.make()
        """
        toxic = Toxic(self, name)

        if toxic.exists():
            toxic.delete()

        toxic.make(t_type=t_type, stream=stream,
                   toxicity=toxicity, attributes=attributes)

        return toxic

    def get_toxic(self, name):
        """
        Get a Toxic by name if it exists
        """
        toxic = Toxic(self, name)

        if toxic.exists():
            return toxic
        else:
            return None


class Toxic:
    def __init__(self, proxy, name):
        """
        Create a Toxic wrapper
        Note: this does not have any side effects

        Arguments:
         * proxy - the Proxy this Toxic is on
         * name - the name of the Toxic
        """
        self.proxy = proxy
        self.name = name

    def get_url(self):
        return f"{self.proxy.get_toxics_url()}/{self.name}"

    def exists(self):
        """
        Checks whether this Toxic exists on the parent Proxy
        """
        return requests.get(self.get_url()).ok

    def make(self, *, t_type, stream, toxicity, attributes):
        """
        Tries to make this Toxic on the Proxy with the provided values
        Raises RuntimeError if the Toxic already exists

        Arguments:
         * t_type - TODO Charlie
         * stream - 'upstream' or 'downstream'
         * toxicity - TODO Charlie
         * attributes - TODO Charlie
        """
        if self.exists():
            raise RuntimeError("Proxy already exists")

        json = {"name": self.name,
                "type": t_type,
                "stream": stream,
                "toxicity": toxicity,
                "attributes": attributes}

        requests.post(self.proxy.get_toxics_url(), json=json)

    def delete(self):
        """
        Deletes this Toxic from the Proxy
        Uses "DELETE /proxies/{proxy}/toxics/{toxic}"
        """
        requests.delete(self.get_url())

    def set_stream(self, stream):
        """
        Sets the stream property of this Toxic on the server
        """
        json = {
            "stream": stream
        }
        requests.post(self.get_url(), json=json)

    def get_stream(self):
        """
        Gets the stream property of this Toxic from the server
        """
        response = requests.get(self.get_url())
        return response.json().get("stream")

    def set_toxicity(self, toxicity):
        """
        Sets the toxicity property of this Toxic on the server
        """
        json = {
            "toxicity": toxicity
        }
        requests.post(self.get_url(), json=json)

    def get_type(self):
        """
                Gets the stream property of this Toxic from the server
                """
        response = requests.get(self.get_url())
        return response.json().get("type")

    def get_toxicity(self):
        """
        Gets the toxicity property of this Toxic from the server
        """
        response = requests.get(self.get_url())
        return response.json().get("toxicity")

    def set_attributes(self, attributes):
        """
        Sets the attributes of this Toxic on the server
        """
        json = {
            "attributes": attributes
        }
        requests.post(self.get_url(), json=json)

    def get_attributes(self):
        """
        Gets the attributes of this Toxic from the server
        """
        response = requests.get(self.get_url())
        return response.json().get("attributes")
