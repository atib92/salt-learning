def command(command):
    """
    Execute a command on the proxied network device.
    """
    return __proxy__["ssh_sample.command"](command)