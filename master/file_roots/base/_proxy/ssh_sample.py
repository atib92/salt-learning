import logging
import json

log = logging.getLogger(__name__)

__virtualname__ = "ssh_sample"

# Tell Salt that this module is allowed to run
# for proxies of type "ssh_sample".
__proxyenabled__ = ["ssh_sample"]

def __virtual__():
    return __virtualname__


def init(opts):
    log.info("Initializing simulated SSH network device")


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
    proxy_config = __opts__["proxy"]

    host = proxy_config["host"]
    username = proxy_config["username"]
    password = proxy_config["password"]

    log.info("Executing command '%s' on %s", command, host)

    import paramiko

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=host,
            username=username,
            password=password,
            timeout=10,
        )

        remote_command = (
            f"python3 /opt/sim-device/network_cli.py "
            f"{command}"
        )

        stdin, stdout, stderr = client.exec_command(remote_command)

        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        if error:
            raise RuntimeError(error)

        return output

    finally:
        client.close()

def shutdown(opts):
    log.info("Shuttingdown simulated SSH network device")

def get_facts():
    return json.loads(command("show version --json"))


def get_interfaces():
    return json.loads(command("show interfaces --json"))


def get_routes():
    return json.loads(command("show ip route --json"))