def command(command):
    return __proxy__["srlinux_ssh.command"](command)

def get_facts():
    return __proxy__["srlinux_ssh.get_facts"]()


def get_interfaces():
    return __proxy__["srlinux_ssh.get_interfaces"]()
