from ncclient import manager


with manager.connect(
    host="172.20.20.2",
    port=830,
    username="linuxadmin",
    password="12345678",
    hostkey_verify=False,
    allow_agent=False,
    look_for_keys=False,
    device_params={"name": "default"},
) as m:

    print("Connected to NETCONF")
    print()
    print("Server capabilities:")
    for capability in m.server_capabilities:
        print(capability)

    print()
    print("Running datastore:")
    reply = m.get_config(source="running")
    print(reply.xml)
