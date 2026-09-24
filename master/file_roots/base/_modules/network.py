def command(command):
    """
    Execute a raw CLI command on the proxied network device.
    """
    return __proxy__["ssh_sample.command"](command)


def get_facts():
    """
    Return basic facts about the network device.
    """
    return __proxy__["ssh_sample.get_facts"]()


def get_interfaces():
    """
    Return interface information.
    """
    return __proxy__["ssh_sample.get_interfaces"]()


def get_routes():
    """
    Return routing information.
    """
    return __proxy__["ssh_sample.get_routes"]()