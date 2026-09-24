import json

__virtualname__ = "srlinux_ssh"
__proxyenabled__ = ["srlinux_ssh"]


def __virtual__():
    return __virtualname__


def init(opts):
    return True


def shutdown(opts):
    return True


def ping():
    return True


def grains():
    return {
        "device_type": "network_device",
        "vendor": "nokia",
        "platform": "srlinux",
    }


def command(command):
    proxy_config = __opts__["proxy"]

    host = proxy_config["host"]
    username = proxy_config["username"]
    password = proxy_config["password"]

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

        remote_command = f"sr_cli '{command}'"

        stdin, stdout, stderr = client.exec_command(remote_command)

        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        if error:
            raise RuntimeError(error)

        return output

    finally:
        client.close()

def get_facts():
    output = command("show version | as json")
    return json.loads(output)


def get_interfaces():
    output = command("show interface | as json")
    return json.loads(output)
