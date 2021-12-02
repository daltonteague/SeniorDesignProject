import sys
from .databuffer import DataBuffer
from .testmanager import TestManager


def launch(hostname, *args, **kwargs):
    """
    The launch function is run by both master and slave nodes
    to connect to the Nile server.
    for the master node, this starts a TestManager that manages the Test record
    for the slave nodes, this starts a DataBuffer that buffers
       and forwards the request data to the Nile server

    Arguments:
     * hostname - the hostname of the Nile server
    Note: All other positional and keyword arguments are forwarded to the
       TestManager or DataBuffer created by launch()
    """

    if _is_master():
        print(f'Nile: Running as master, nile-server="{hostname}"')
        TestManager(hostname, *args, **kwargs)

    elif _is_slave():
        print(f'Nile: Running as slave, nile-server="{hostname}"')
        DataBuffer(hostname, *args, **kwargs)


def _is_slave():
    """Determines whether this locustfile is being run as slave"""
    return "--slave" in sys.argv


def _is_master():
    """Determines whether this locustfile is being run as master"""
    return "--slave" not in sys.argv
