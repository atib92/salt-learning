import json
import sys


COMMANDS = {
    "show version": """SaltSim OS
Version: 1.0
Vendor: SaltLab
Model: SIM-ROUTER-1
Hostname: sim-device
""",

    "show interfaces": """Interface        Status    IP Address
eth0             up        10.0.0.1/24
eth1             up        10.0.1.1/24
lo               up        127.0.0.1/8
""",

    "show ip route": """Destination      Next Hop       Interface
10.0.0.0/24      connected       eth0
10.0.1.0/24      connected       eth1
0.0.0.0/0        10.0.0.254      eth0
""",
}


STRUCTURED_DATA = {
    "show version": {
        "os": "SaltSim OS",
        "version": "1.0",
        "vendor": "SaltLab",
        "model": "SIM-ROUTER-1",
        "hostname": "sim-device",
    },
    "show interfaces": {
        "eth0": {
            "status": "up",
            "ip": "10.0.0.1/24",
        },
        "eth1": {
            "status": "up",
            "ip": "10.0.1.1/24",
        },
        "lo": {
            "status": "up",
            "ip": "127.0.0.1/8",
        },
    },
    "show ip route": [
        {
            "destination": "10.0.0.0/24",
            "next_hop": "connected",
            "interface": "eth0",
        },
        {
            "destination": "10.0.1.0/24",
            "next_hop": "connected",
            "interface": "eth1",
        },
        {
            "destination": "0.0.0.0/0",
            "next_hop": "10.0.0.254",
            "interface": "eth0",
        },
    ],
}


def main():
    args = sys.argv[1:]

    structured = "--json" in args
    args = [arg for arg in args if arg != "--json"]

    command = " ".join(args)

    if structured:
        if command not in STRUCTURED_DATA:
            print(f"% Unknown command: {command}", file=sys.stderr)
            sys.exit(1)

        print(json.dumps(STRUCTURED_DATA[command]))
        return

    if command in COMMANDS:
        print(COMMANDS[command])
        return

    print(f"% Unknown command: {command}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()