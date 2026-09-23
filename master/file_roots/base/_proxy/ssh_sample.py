import logging

log = logging.getLogger(__name__)

__virtualname__ = "ssh_sample"

# Tell Salt that this module is allowed to run
# for proxies of type "ssh_sample".
__proxyenabled__ = ["ssh_sample"]

def __virtual__():
    return __virtualname__


def init(opts):
    log.info("Initializing simulated SSH network device")


def ping_1():
   return True

def ping():
    return {
        "source": "ssh_sample.py",
        "message": "Hello from the proxy module!"
    }


def grains():
    return {
        "device_type": "simulated_network_device",
        "vendor": "salt-lab",
        "platform": "ssh-sim",
    }


def command(command):
    return f"SIMULATED DEVICE: executed '{command}'"

def shutdown(opts):
    log.info("Shuttingdown simulated SSH network device")