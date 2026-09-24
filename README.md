# SaltStack Learning Lab

A hands-on SaltStack learning environment built from scratch to understand Salt from first principles and progressively move toward **network automation and infrastructure automation**.

Disclaimer: This tutorial and its accompanying documentation were generated with the assistance of AI for learning and educational purposes. The examples, configurations, commands, explanations, and conclusions should be treated as learning material rather than authoritative production guidance. Always validate configurations and commands against the relevant SaltStack, Docker, Containerlab, network operating system, and vendor documentation before using them in a production environment.


The lab starts with traditional Salt minions and state management, then progresses through:

* Salt Master / Minion architecture
* Keys and authentication
* Grains and targeting
* Pillar and environments
* Jinja templating
* States and highstate
* Custom Salt execution modules
* Salt Proxy Minions
* Custom proxy modules
* SSH-based network-device automation
* Simulated network devices
* Nokia SR Linux with Containerlab
* NETCONF and YANG
* Model-driven network automation concepts

The eventual goal is to use the same mental model for automating real network devices such as **Nokia SR Linux, Junos, Cisco IOS/XE, IOS-XR, and Arista EOS**.

---

# 1. Lab Architecture

The lab intentionally contains multiple types of Salt-managed targets.

```text
                              ┌─────────────────────────┐
                              │       Salt Master       │
                              │                         │
                              │  States / Pillar /     │
                              │  Execution Modules /   │
                              │  Proxy Modules         │
                              └────────────┬────────────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
                    ▼                      ▼                      ▼
             ┌─────────────┐       ┌─────────────┐       ┌────────────────┐
             │ Salt Minion │       │ Salt Minion │       │ Proxy Minion   │
             │  web-1      │       │ worker-1    │       │ lab-router-1   │
             └─────────────┘       └─────────────┘       └───────┬────────┘
                                                                  │
                                                        SSH / API / NETCONF
                                                                  │
                                                                  ▼
                                                        ┌─────────────────┐
                                                        │ Network Device  │
                                                        │                 │
                                                        │ SR Linux /      │
                                                        │ Simulated Device│
                                                        └─────────────────┘
```

The important distinction is:

```text
Normal server automation:

Salt Master
    ↓
Salt Minion
    ↓
Linux host


Network automation:

Salt Master
    ↓
Salt Proxy Minion
    ↓
Network device
```

A network device does not necessarily run a Salt minion.

The proxy minion acts as the Salt execution point for the device.

---

# 2. Repository Structure

The project currently looks approximately like this:

```text
.
├── .gitignore
├── README.md
├── docker-compose.yml
│
├── docker/
│   ├── master/
│   │   └── Dockerfile
│   ├── minion/
│   │   └── Dockerfile
│   ├── worker/
│   │   └── Dockerfile
│   ├── proxy/
│   │   └── Dockerfile
│   └── sim-device/
│       └── Dockerfile
│
├── master/
│   ├── config/
│   │   └── lab.conf
│   │
│   ├── file_roots/
│   │   └── base/
│   │       ├── top.sls
│   │       │
│   │       ├── web/
│   │       │   ├── init.sls
│   │       │   ├── nginx.sls
│   │       │   ├── app.sls
│   │       │   ├── map.jinja
│   │       │   └── nginx.conf.jinja
│   │       │
│   │       ├── worker/
│   │       │   ├── init.sls
│   │       │   └── worker.sls
│   │       │
│   │       ├── _proxy/
│   │       │   ├── ssh_sample.py
│   │       │   └── srlinux_ssh.py
│   │       │
│   │       └── _modules/
│   │           ├── network.py
│   │           └── srlinux.py
│   │
│   └── pki/
│
├── pillar/
│   ├── base/
│   ├── dev/
│   └── prod/
│
├── minion/
├── web-1/
├── web-2/
├── worker/
│
├── lab-router-1/
│   ├── config/
│   │   └── proxy.conf
│   └── pki/
│
├── sim-device/
│   └── network_cli.py
│
├── containerlab/
│   └── topology.clab.yml
│
└── states/
```

The `states/` directory is currently unused. The actual Salt file root is:

```text
master/file_roots/base/
```

---

# 3. Running the Lab

Start the core Salt environment:

```bash
docker compose up -d --build
```

Check containers:

```bash
docker compose ps
```

A healthy environment contains:

```text
salt-master
salt-minion
web-1
web-2
worker-1
lab-router-1
sim-device
```

---

# 4. Verify Salt Connectivity

The first Salt command to run is:

```bash
docker compose exec salt-master salt '*' test.ping
```

Expected result:

```text
web-1:
    True

web-2:
    True

worker-1:
    True

lab-minion:
    True
```

For the proxy minion:

```bash
docker compose exec salt-master salt lab-router-1 test.ping
```

The proxy can return structured information as well:

```text
lab-router-1:
    message: Hello from the proxy module!
    source: ssh_sample.py
```

---

# 5. Salt's Core Mental Model

The most useful mental model developed throughout this lab is:

> **Grains classify the machine. Pillar configures the machine. States describe what the machine should look like.**

And around that:

```text
Master
  │
  ├── Keys          → Trust / authentication
  ├── Grains        → Facts / classification
  ├── Pillar        → Configuration / data
  ├── States        → Desired state
  ├── Targeting     → Which machines
  ├── Jinja         → Rendering / presentation
  └── Python        → Custom Salt functionality
```

---

# 6. Salt Master

The master configuration is mounted into:

```text
/etc/salt/master.d/
```

Our main configuration:

```yaml
file_roots:
  base:
    - /srv/salt/base

pillar_roots:
  base:
    - /srv/pillar/base

  dev:
    - /srv/pillar/dev

  prod:
    - /srv/pillar/prod
```

This separates:

```text
State environments
        ↓
saltenv

Pillar environments
        ↓
pillarenv
```

These are independent concepts.

---

# 7. Salt Keys

Salt uses public-key authentication between master and minions.

List keys:

```bash
docker compose exec salt-master salt-key -L
```

Typical output:

```text
Accepted Keys:
    lab-minion
    web-1
    web-2
    worker-1
    lab-router-1
```

Accept a key:

```bash
docker compose exec salt-master salt-key -a lab-minion
```

Delete a key:

```bash
docker compose exec salt-master salt-key -d lab-minion
```

The proxy minion also participates in this trust model.

---

# 8. Grains

Grains are facts associated with the target.

Example:

```bash
docker compose exec salt-master salt lab-minion grains.items
```

Custom grains were used to classify machines.

Example:

```ini
role: web
```

or:

```ini
role: worker
```

The important idea is:

```text
Grains = "What/Who is this machine?"
```

Examples:

```text
role = web
role = worker
vendor = nokia
platform = srlinux
device_type = network_device
```

---

# 9. Targeting

Salt can target minions using IDs:

```bash
salt web-1 test.ping
```

Wildcards:

```bash
salt 'web-*' test.ping
```

Grains:

```bash
salt -G 'role:web' test.ping
```

Compound targeting can combine multiple selectors.

The state tree uses grain targeting:

```yaml
base:
  'G@role:web':
    - web

  'G@role:worker':
    - worker
```

This means:

```text
Machines with role=web
        ↓
        web states

Machines with role=worker
        ↓
        worker states
```

---

# 10. Pillar

Pillar is structured configuration data supplied to minions.

Example:

```yaml
app:
  name: salt-learning
  environment: development
```

And:

```yaml
nginx:
  port: 8080
  worker_processes: 1
```

The application state does not need to hardcode these values.

Instead:

```text
State
  ↓
Reads pillar
  ↓
Renders configuration
  ↓
Applies desired state
```

Inspect pillar:

```bash
docker compose exec salt-master \
  salt lab-minion pillar.items
```

---

# 11. Pillar Environments

We created separate:

```text
pillar/
├── base/
├── dev/
└── prod/
```

Example:

```text
pillar/dev/
├── top.sls
├── common.sls
└── web.sls
```

Production:

```text
pillar/prod/
├── top.sls
├── common.sls
├── web.sls
└── web-1.sls
```

Production web configuration:

```yaml
nginx:
  port: 8080
  worker_processes: 4
```

A specific production override for `web-1`:

```yaml
nginx:
  port: 9090
  worker_processes: 8
```

Explicitly selecting the pillar environment:

```bash
docker compose exec salt-master \
  salt web-1 pillar.items pillarenv=prod
```

The important lesson:

> `saltenv` and `pillarenv` are separate.

For example:

```text
saltenv=base
pillarenv=prod
```

is perfectly valid.

Explicitly selecting `pillarenv` also prevents accidentally merging configuration from multiple pillar environments when debugging environment-specific behavior.

---

# 12. Top Files

State top file:

```yaml
base:
  'G@role:web':
    - web

  'G@role:worker':
    - worker
```

Pillar top file for production:

```yaml
prod:
  '*':
    - common

  'G@role:web':
    - web

  'web-1':
    - web-1
```

One important lesson from the lab was that a file existing under:

```text
pillar/prod/
```

does **not** automatically mean every minion receives it.

The pillar `top.sls` determines which pillar data is actually assigned.

---

# 13. States

A state describes desired configuration.

Example:

```yaml
nginx:
  pkg.installed: []

nginx-service:
  service.running:
    - name: nginx
    - enable: true
```

States can be composed.

Example:

```yaml
include:
  - web.nginx
  - web.app
```

This allows:

```text
web/init.sls
      │
      ├── web/nginx.sls
      └── web/app.sls
```

Run highstate:

```bash
docker compose exec salt-master \
  salt web-1 state.apply
```

Or:

```bash
docker compose exec salt-master \
  salt web-1 state.highstate
```

---

# 14. Jinja

Salt states use Jinja for templating.

For example:

```jinja
worker_processes {{ nginx.worker_processes }};
```

The data can come from pillar.

Conceptually:

```text
Pillar
  ↓
Jinja
  ↓
Rendered Salt state/configuration
  ↓
System
```

---

# 15. Salt Map Files

We also used a `map.jinja` pattern.

Example:

```jinja
{% set nginx_defaults = {
    'port': 80,
    'worker_processes': 1
} %}

{% set nginx = nginx_defaults.copy() %}
{% if pillar.get('nginx') %}
  {% set _ = nginx.update(pillar.get('nginx')) %}
{% endif %}
```

One interesting compatibility lesson:

The Salt/Jinja environment in this lab did not provide the `combine` filter we initially attempted to use.

Instead of:

```jinja
something | combine(...)
```

we used:

```jinja
.copy()
.update()
```

This is a useful reminder that Jinja/Salt functionality depends on the actual runtime environment and version.

---

# 16. Docker vs Salt

One of the important architectural lessons from the lab was understanding the difference between Docker and Salt.

### Docker

Docker is primarily concerned with:

```text
Packaging
Isolation
Reproducibility
Immutable images
Application runtime
```

Example:

```dockerfile
FROM ubuntu:24.04

RUN apt-get update && \
    apt-get install -y nginx
```

### Salt

Salt is concerned with:

```text
Desired state
Configuration management
Convergence
Long-lived machines
Fleet orchestration
```

For example:

```text
"nginx should be installed"

"nginx should be running"

"nginx should listen on port 8080"
```

These aren't competing concepts.

They can coexist:

```text
Terraform
    ↓
Infrastructure

Salt
    ↓
Machine configuration

Docker
    ↓
Application runtime

Kubernetes
    ↓
Container/workload orchestration
```

---

# 17. Why We Built a Proxy Minion

Normal Salt:

```text
Salt Master
     ↓
Salt Minion
     ↓
Operating System
```

Network devices generally cannot run a Salt minion.

Instead:

```text
Salt Master
     ↓
Proxy Minion
     ↓
Network Device
```

The proxy minion provides an abstraction layer between Salt and the device.

This allows Salt to target a network device as if it were a Salt-managed target.

---

# 18. First Proxy: Simulated Device

The first proxy implementation was intentionally simple.

Proxy configuration:

```yaml
master: salt-master

proxy:
  proxytype: ssh_sample
  host: sim-device
  username: netadmin
  password: netadmin
```

The custom proxy module lived under:

```text
master/file_roots/base/_proxy/
```

Specifically:

```text
_proxy/ssh_sample.py
```

The important special directory is:

```text
_proxy/
```

Salt automatically synchronizes proxy modules to the proxy minion.

---

# 19. Custom Proxy Module

The module defines:

```python
__virtualname__ = "ssh_sample"
__proxyenabled__ = ["ssh_sample"]
```

And:

```python
def __virtual__():
    return __virtualname__
```

Basic lifecycle functions:

```python
def init(opts):
    return True


def shutdown(opts):
    return True
```

Basic health check:

```python
def ping():
    return True
```

Custom grains:

```python
def grains():
    return {
        "device_type": "simulated_network_device",
        "vendor": "salt-lab",
        "platform": "ssh-sim",
    }
```

---

# 20. Proxy → Device Communication

The simulated proxy used Paramiko.

Conceptually:

```text
Salt Master
    ↓
Salt execution module
    ↓
Proxy module
    ↓
Paramiko
    ↓
SSH
    ↓
sim-device
```

The proxy's command function:

```python
def command(command):
    proxy_config = __opts__["proxy"]

    host = proxy_config["host"]
    username = proxy_config["username"]
    password = proxy_config["password"]

    import paramiko

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(
        paramiko.AutoAddPolicy()
    )

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

        stdin, stdout, stderr = client.exec_command(
            remote_command
        )

        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        if error:
            raise RuntimeError(error)

        return output

    finally:
        client.close()
```

---

# 21. Custom Salt Execution Modules

Proxy modules handle device communication.

Execution modules provide the user-facing Salt functions.

Example:

```text
_modules/network.py
```

```python
def command(command):
    return __proxy__["ssh_sample.command"](command)


def get_facts():
    return __proxy__["ssh_sample.get_facts"]()


def get_interfaces():
    return __proxy__["ssh_sample.get_interfaces"]()


def get_routes():
    return __proxy__["ssh_sample.get_routes"]()
```

This creates a clean separation:

```text
Execution module
    ↓
"What operation do I want?"

Proxy module
    ↓
"How do I communicate with the device?"
```

---

# 22. Structured Network Data

The simulated device supported JSON commands:

```text
show version --json
show interfaces --json
show ip route --json
```

The proxy converted them into Python objects:

```python
def get_facts():
    return json.loads(command("show version --json"))


def get_interfaces():
    return json.loads(
        command("show interfaces --json")
    )


def get_routes():
    return json.loads(
        command("show ip route --json")
    )
```

This was an important step away from treating device CLI output as arbitrary text.

---

# 23. Example Network Commands

Raw command:

```bash
docker compose exec salt-master \
  salt lab-router-1 network.command "show ip route"
```

Structured data:

```bash
docker compose exec salt-master \
  salt lab-router-1 network.get_routes
```

Example:

```text
lab-router-1:
    10.0.0.0/24:
        interface: eth0
        status: connected

    10.0.1.0/24:
        interface: eth1
        status: connected

    0.0.0.0/0:
        gateway: 10.0.0.254
        interface: eth0
```

This gives us the first real network-automation abstraction.

---

# 24. Moving Toward a Real Network Device

The next goal was to stop pretending the device was a Python script.

We introduced **Nokia SR Linux** using Containerlab.

Architecture became:

```text
Salt Master
      │
      ▼
lab-router-1
Salt Proxy
      │
      │ SSH
      ▼
Nokia SR Linux
```

---

# 25. Containerlab

Containerlab is used to create realistic network topologies using containerized network operating systems.

The topology:

```yaml
name: salt-netlab

topology:
  nodes:
    router1:
      kind: nokia_srlinux
      image: ghcr.io/nokia/srlinux:latest
```

Deploy:

```bash
sudo containerlab deploy -t ./topology.clab.yml
```

Check topology:

```bash
sudo containerlab inspect -t ./topology.clab.yml
```

The SR Linux node is created as:

```text
clab-salt-netlab-router1
```

---

# 26. Important Docker / Containerlab Issue

Initially Containerlab was using the Docker engine exposed through Docker Desktop's WSL integration.

This caused networking problems.

Containerlab created Docker bridge interfaces inside the Docker Desktop VM, while WSL itself could not see those Linux network interfaces.

The symptom was:

```text
ERROR Failed to lookup link "br-e9523e4bd0c8":
Link not found.
```

This was not a Salt problem.

It was a Docker networking / namespace boundary problem.

---

# 27. Solution: Native Docker Inside WSL

We disabled Docker Desktop WSL integration and installed Docker Engine directly inside WSL.

Installation:

```bash
sudo apt update
sudo apt install -y curl
```

Then:

```bash
curl -sL https://containerlab.dev/setup | \
  sudo -E bash -s "all"
```

Verify Docker:

```bash
docker version
```

The important result was:

```text
Client: Docker Engine - Community
 Version: 27.5.1

Server: Docker Engine - Community
 Version: 27.5.1
```

Now both:

```text
Docker
Containerlab
```

run inside the same WSL Linux environment.

This makes Linux networking namespaces and Docker bridges visible to Containerlab.

---

# 28. WSL Memory Configuration

SR Linux is substantially heavier than our normal Salt containers.

Initially WSL had approximately:

```text
Memory: ~3.5 GiB
Swap:   ~1 GiB
```

Containerlab warned that SR Linux wanted significantly more memory.

The Windows host had approximately:

```text
Total Physical Memory: ~7.4 GB
```

We created:

```text
%USERPROFILE%\.wslconfig
```

with:

```ini
[wsl2]
memory=5GB
swap=2GB
```

Then restarted WSL:

```powershell
wsl --shutdown
```

After restarting:

```bash
free -h
```

showed approximately:

```text
Mem:    4.8Gi
Swap:   2.0Gi
```

Docker also saw approximately:

```text
Total Memory: 4.8GiB
```

This was sufficient to run SR Linux alongside the Salt environment.

---

# 29. Containerlab + Salt Network

Containerlab created a network:

```text
clab
```

with subnet:

```text
172.20.20.0/24
```

SR Linux:

```text
172.20.20.2
```

The Salt proxy was attached to the same network and received:

```text
172.20.20.3
```

The resulting topology:

```text
                    Docker / WSL
                         │
                 ┌───────┴────────┐
                 │   clab network │
                 │ 172.20.20.0/24 │
                 └───────┬────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
      lab-router-1              SR Linux
      172.20.20.3               172.20.20.2
      Salt Proxy                  router1
```

---

# 30. SR Linux

Enter the SR Linux CLI:

```bash
docker exec -it clab-salt-netlab-router1 sr_cli
```

Check version:

```text
show version
```

Example:

```text
Hostname             : router1
Chassis Type         : 7220 IXR-D2L
OS                   : SR Linux
Software Version     : v26.7.2
Architecture         : x86_64
```

Check interfaces:

```text
show interface
```

Management interface:

```text
mgmt0
```

was eventually reachable at:

```text
172.20.20.2/24
```

---

# 31. SR Linux SSH Access

We discovered that the expected `admin` user did not exist.

The device contained:

```text
linuxadmin
```

We set its password:

```bash
docker exec clab-salt-netlab-router1 \
  bash -c "echo 'linuxadmin:12345678' | chpasswd"
```

From the proxy container:

```bash
docker exec -it lab-router-1 \
  ssh linuxadmin@172.20.20.2
```

This produced:

```text
[linuxadmin@router1 ~]$
```

At this point the proxy could communicate with an actual network operating system rather than our simulated Python device.

---

# 32. Important SR Linux CLI Distinction

SSH initially lands in a Linux shell:

```text
[linuxadmin@router1 ~]$
```

Therefore this:

```bash
show interface
```

does not work directly.

`show` is an SR Linux CLI command.

We must invoke:

```bash
sr_cli
```

or:

```bash
sr_cli "show interface"
```

Therefore the automation path became:

```text
SSH
  ↓
Linux shell
  ↓
sr_cli
  ↓
SR Linux management interface
```

---

# 33. SR Linux Proxy Module

The simulated proxy was replaced by:

```text
master/file_roots/base/_proxy/srlinux_ssh.py
```

Configuration:

```yaml
master: salt-master

proxy:
  proxytype: srlinux_ssh
  host: 172.20.20.2
  username: linuxadmin
  password: "12345678"
```

The proxy module:

```python
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
```

---

# 34. SR Linux Proxy Command

The core operation is:

```python
def command(command):
    proxy_config = __opts__["proxy"]

    host = proxy_config["host"]
    username = proxy_config["username"]
    password = proxy_config["password"]

    import paramiko

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(
        paramiko.AutoAddPolicy()
    )

    try:
        client.connect(
            hostname=host,
            username=username,
            password=password,
            timeout=10,
        )

        remote_command = f"sr_cli '{command}'"

        stdin, stdout, stderr = client.exec_command(
            remote_command
        )

        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        if error:
            raise RuntimeError(error)

        return output

    finally:
        client.close()
```

---

# 35. SR Linux Execution Module

The corresponding execution module:

```text
master/file_roots/base/_modules/srlinux.py
```

contains:

```python
def command(command):
    return __proxy__["srlinux_ssh.command"](command)


def get_facts():
    return __proxy__["srlinux_ssh.get_facts"]()


def get_interfaces():
    return __proxy__["srlinux_ssh.get_interfaces"]()
```

This gives us:

```text
Salt CLI
   ↓
srlinux.command()
   ↓
_modules/srlinux.py
   ↓
__proxy__
   ↓
srlinux_ssh.command()
   ↓
Paramiko
   ↓
SSH
   ↓
sr_cli
   ↓
SR Linux
```

---

# 36. Running Commands Through Salt

Raw SR Linux CLI:

```bash
docker compose exec salt-master \
  salt lab-router-1 \
  srlinux.command "show version"
```

Interface information:

```bash
docker compose exec salt-master \
  salt lab-router-1 \
  srlinux.command "show interface"
```

The result came directly from the real SR Linux instance.

Example:

```text
mgmt0 is up
mgmt0.0 is up

IPv4 addr : 172.20.20.2/24
IPv6 addr : 3fff:172:20:20::2/64
```

---

# 37. Error Propagation

An intentionally invalid command was tested:

```bash
docker compose exec salt-master \
  salt lab-router-1 \
  srlinux.command "show vew version"
```

SR Linux returned:

```text
RuntimeError:
Parsing error: Unknown token 'vew'
```

This was useful because it verified the complete error path:

```text
Salt
 ↓
Execution module
 ↓
Proxy module
 ↓
Paramiko
 ↓
SSH
 ↓
sr_cli
 ↓
SR Linux parser
 ↓
Error
 ↓
Salt
```

The proxy isn't hiding device errors.

---

# 38. Structured SR Linux Data

The proxy also exposes structured data:

```python
def get_facts():
    output = command("show version | as json")
    return json.loads(output)


def get_interfaces():
    output = command("show interface | as json")
    return json.loads(output)
```

This is already a major improvement over scraping human-readable CLI output.

For example:

```bash
docker compose exec salt-master \
  salt lab-router-1 srlinux.get_facts
```

or:

```bash
docker compose exec salt-master \
  salt lab-router-1 srlinux.get_interfaces
```

The result is structured Python/Salt data.

---

# 39. Why CLI Automation Is Only the First Step

The SSH + CLI approach is useful, but it has limitations.

CLI automation generally looks like:

```text
Command
   ↓
Text
   ↓
Parse text
   ↓
Convert to structured data
```

Problems include:

* CLI syntax differs between vendors
* Output formatting can change
* Text parsing is brittle
* Different vendors expose different command hierarchies
* Configuration workflows can be difficult to make transactional
* Validation is harder

Modern network automation increasingly uses:

```text
YANG
NETCONF
RESTCONF
gNMI
OpenConfig
```

This leads to model-driven automation.

---

# 40. NETCONF

NETCONF provides a structured management protocol.

The conceptual difference is:

### CLI

```text
SSH :22
   ↓
Linux shell
   ↓
sr_cli
   ↓
Text
```

### NETCONF

```text
SSH :830
   ↓
NETCONF subsystem
   ↓
XML
   ↓
YANG-modeled data
```

NETCONF is therefore not just another CLI.

It is a protocol for manipulating structured configuration/state.

---

# 41. Testing NETCONF

The SR Linux device exposes NETCONF over SSH.

The OpenSSH command:

```bash
docker compose exec lab-router-1 \
  ssh -p 830 -s linuxadmin@172.20.20.2 netconf
```

is important because:

```text
-p 830
```

selects the NETCONF SSH port.

And:

```text
-s
```

requests an SSH subsystem.

The final:

```text
netconf
```

is the subsystem name.

The initial attempt where `netconf` was placed incorrectly caused OpenSSH to interpret it as a hostname.

---

# 42. NETCONF Hello Exchange

A successful NETCONF connection returned a `<hello>` message.

The server advertised capabilities including:

```text
NETCONF 1.0
NETCONF 1.1
```

and capabilities related to:

```text
candidate
confirmed-commit
rollback-on-error
validate
startup
with-defaults
NETCONF monitoring
YANG library
```

This is significant because the server isn't merely exposing a raw SSH endpoint.

It is advertising a full model-driven management interface.

---

# 43. NETCONF and YANG

The NETCONF server advertised a large set of YANG modules.

Among the advertised models were modules related to:

```text
SR Linux interfaces
SR Linux network-instance
SR Linux NETCONF server
OpenConfig interfaces
OpenConfig network instances
IETF NETCONF
NMDA
YANG library
gNMI
```

The important architectural idea is:

```text
YANG
  ↓
Data model
  ↓
NETCONF / RESTCONF / gNMI
  ↓
Network device
```

YANG defines the shape and semantics of the data.

The protocol transports and manipulates that data.

---

# 44. NETCONF Experiment with ncclient

We installed `ncclient` into the proxy environment and used a small Python script to connect.

Conceptually:

```python
from ncclient import manager

with manager.connect(
    host="172.20.20.2",
    port=830,
    username="linuxadmin",
    password="12345678",
    hostkey_verify=False,
    device_params={"name": "default"},
) as m:

    print("Connected to NETCONF")

    for capability in m.server_capabilities:
        print(capability)
```

This allowed us to inspect what the SR Linux NETCONF server actually advertises.

The experiment confirmed:

```text
Salt Proxy
    ↓
SSH
    ↓
NETCONF
    ↓
YANG
    ↓
SR Linux
```

We deliberately stopped here rather than implementing a full Salt NETCONF proxy.

---

# 45. Why We Did Not Build a NETCONF Proxy Yet

At this point we already have:

```text
Salt
  ↓
Custom proxy
  ↓
SSH
  ↓
SR Linux
```

and independently:

```text
Python
  ↓
ncclient
  ↓
NETCONF
  ↓
SR Linux
```

The next abstraction would be:

```text
Salt
  ↓
NETCONF Proxy
  ↓
ncclient
  ↓
NETCONF
  ↓
YANG
  ↓
SR Linux
```

That is a worthwhile next project, but implementing it immediately would mix several concepts:

* Salt proxy internals
* NETCONF session lifecycle
* XML
* YANG
* configuration datastore semantics
* candidate configuration
* commits
* rollback
* filtering
* namespaces

The lab therefore stops after proving that the device exposes the required model-driven interface.

---

# 46. Salt Proxy vs Network Protocol

One of the most important architectural lessons is that these are different layers.

Salt Proxy:

```text
"How does Salt communicate with this target?"
```

NETCONF:

```text
"How does a network management client manipulate structured configuration?"
```

SSH:

```text
"How do I establish a secure transport/session?"
```

YANG:

```text
"What does the network data look like?"
```

OpenConfig:

```text
"What standardized vendor-neutral models can I use?"
```

They fit together:

```text
                Salt
                 │
          Salt Proxy
                 │
        ┌────────┴────────┐
        │                 │
       SSH              NETCONF
        │                 │
     CLI/sr_cli          XML
                          │
                         YANG
                          │
                      SR Linux
```

---

# 47. Current Proxy Evolution

The proxy evolved through three stages.

## Stage 1 — Dummy Proxy

```text
Salt
 ↓
Proxy
 ↓
Hardcoded response
```

Purpose:

Learn Salt Proxy architecture.

---

## Stage 2 — Simulated Network Device

```text
Salt
 ↓
Proxy
 ↓
Paramiko
 ↓
SSH
 ↓
Python network_cli.py
```

Purpose:

Learn actual device communication without requiring a real NOS.

---

## Stage 3 — Real Network OS

```text
Salt
 ↓
Proxy
 ↓
Paramiko
 ↓
SSH
 ↓
sr_cli
 ↓
Nokia SR Linux
```

Purpose:

Validate the architecture against a real network operating system.

---

## Stage 4 — Model-Driven Networking

The next logical evolution:

```text
Salt
 ↓
NETCONF / gNMI
 ↓
YANG / OpenConfig
 ↓
Network Device
```

This stage was explored experimentally using NETCONF but not yet integrated into Salt.

---

# 48. What We Learned About Container Images

An early version of the simulated device used runtime provisioning:

```yaml
command:
  - bash
  - -c
  - |
      apt-get update &&
      apt-get install -y openssh-server &&
      useradd -m netadmin &&
      ...
```

This caused problems because the container startup procedure was not idempotent.

For example:

```bash
useradd -m netadmin
```

fails if the user already exists.

The container eventually exited.

The better approach was to build an actual image.

```dockerfile
FROM ubuntu:24.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openssh-server \
        python3 \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /run/sshd && \
    useradd -m -s /bin/bash netadmin && \
    echo 'netadmin:netadmin' | chpasswd

WORKDIR /opt/sim-device

CMD ["/usr/sbin/sshd", "-D"]
```

The lesson:

> Image construction belongs in the Dockerfile; runtime startup should primarily start the service.

---

# 49. Salt Proxy Image

The proxy image uses Salt's Onedir Python environment.

Important detail:

```text
/opt/saltstack/salt/bin/python3
```

is the Python interpreter used by Salt.

Paramiko was installed into that environment:

```dockerfile
RUN /opt/saltstack/salt/bin/python3 \
    -m pip install --no-cache-dir paramiko
```

The proxy image also installs:

```text
openssh-client
```

because it needs SSH tooling.

The Salt installation already provides:

```text
salt-proxy
```

in this Salt 3008.2 environment.

A separate `salt-proxy` apt package was not required.

---

# 50. Salt Version

The lab currently uses:

```text
Salt: 3008.2
```

Environment:

```text
Ubuntu: 24.04
Python: 3.14.6
Jinja2: 3.1.6
```

Containerlab:

```text
0.79.0
```

Docker Engine:

```text
27.5.1
```

Nokia SR Linux:

```text
v26.7.2
```

---

# 51. Useful Troubleshooting Commands

### Check containers

```bash
docker compose ps
```

### Check logs

```bash
docker compose logs salt-master
```

```bash
docker compose logs lab-router-1
```

```bash
docker compose logs sim-device
```

### Check Salt keys

```bash
docker compose exec salt-master salt-key -L
```

### Check connectivity

```bash
docker compose exec salt-master \
  salt '*' test.ping
```

### Check grains

```bash
docker compose exec salt-master \
  salt lab-router-1 grains.items
```

### Check pillar

```bash
docker compose exec salt-master \
  salt lab-minion pillar.items
```

### Check Salt version

```bash
docker compose exec salt-master \
  salt '*' test.version
```

### Check Docker networks

```bash
docker network ls
```

### Inspect Containerlab

```bash
sudo containerlab inspect -t ./containerlab/topology.clab.yml
```

### Check Docker memory

```bash
docker info | grep -i memory
```

### Check WSL memory

```bash
free -h
```

### Check SR Linux

```bash
docker exec -it clab-salt-netlab-router1 sr_cli
```

---

# 52. Debugging the Proxy

When a proxy isn't working, debug from the bottom up.

### 1. Is the target container running?

```bash
docker ps
```

### 2. Can the proxy reach the device?

```bash
docker exec -it lab-router-1 \
  ssh linuxadmin@172.20.20.2
```

### 3. Can SSH execute `sr_cli`?

```bash
docker exec lab-router-1 \
  ssh linuxadmin@172.20.20.2 \
  'sr_cli "show version"'
```

### 4. Can the proxy Python environment import Paramiko?

```bash
docker exec lab-router-1 \
  /opt/saltstack/salt/bin/python3 \
  -c "import paramiko; print(paramiko.__version__)"
```

### 5. Can Salt see the proxy?

```bash
docker compose exec salt-master \
  salt-key -L
```

### 6. Can Salt execute the custom module?

```bash
docker compose exec salt-master \
  salt lab-router-1 \
  srlinux.command "show version"
```

This bottom-up debugging strategy proved extremely useful.

---

# 53. The Complete End-to-End Path

The final working CLI architecture is:

```text
┌──────────────────────────────┐
│          Salt CLI            │
│                              │
│ srlinux.command("show ...")  │
└─────â──────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Salt Execution Module        │
│                              │
│ _modules/srlinux.py          │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────âProxy Module            │
│                              │
│ _proxy/srlinux_ssh.py        │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Paramiko                     │
└──────────────┬───────────────┘
               │
               ▼
┌â────────────────────┐
│ SSH                          │
│ 172.20.20.2                  │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Linux shell                  │
└──────────────┬───────────────┘
                    ▼
┌──────────────────────────────┐
│ sr_cli                       │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Nokia SR Linux               │
│ router1                      │
└────────────────â───────┘
```

---

# 54. The Model-Driven Path

The more advanced architecture is:

```text
                     Salt
                       │
                 Proxy / Module
                       │
             ┌─────────┴─────────┐
             │                   │
            SSH               NETCONF
             │                   │
          sr_cli                XML
                                 │
                       ANG
                                 │
                            OpenConfig
                                 │
                                 ▼
                            SR Linux
```

And eventually:

```text
                 Network Automation Platform
                           │
          ┌────────────────┼────────────────┐
          │                │                │
        Junos           SR Linux         EOS
      │                │                │
       NETCONF           gNMI            NETCONF
          │                │                │
          └────────────────┼────────────────┘
                           │
                     Common Models
                    OpenConfig / YANG
```

This is where network automation starts becoming much closer to software engineering:

```text
Typed data
Structured APIs
Schemas
Validationnsactions
Idempotency
Testing
Version control
CI/CD
```

---

# 55. Key Lessons From the Lab

## 1. Salt is more than remote command execution

The important Salt abstractions are:

```text
Targeting
Grains
Pillar
States
Jinja
Execution Modules
Proxy Modules
Environments
```

---

## 2. Proxy Minions are an abstraction boundary

The Salt master doesn't need to understand every network device.

Instead:

```text
Salt
  ↓
Proxy
  ↓
Vendor/device-specific communication
```

---

## 3. Execution modules andxy modules have different responsibilities

Execution module:

```text
What operation do I want?
```

Proxy module:

```text
How do I communicate with this device?
```

---

## 4. CLI automation is useful but limited

SSH + CLI is easy to understand and excellent for learning.

But production network automation increasingly benefits from:

```text
NETCONF
RESTCONF
gNMI
YANG
OpenConfig
```

---

## 5. Containerlab makes network automation experimentation accessible

Instead of requiring physical routers:

```text
Laptop
  ↓
WSL
  ↓
Docker
  ↓
Containerlab
  ↓
Network OS containers
```

This provides a surprisingly realistic network lab.

---

## 6. Infrastructure problems can masquerade as application problems

The Containerlab failure initially looked like a Containerlab problem:

```text
Link not found
```

But the underlying issue was:

```text
Docker Desktop VM
        ≠
WSL Linux network namespace
```

Understanding the execution environment was more important than changing Salt configuration.

 Current Capabilities

At the end of this phase, the lab can:

### Salt fundamentals

* Run a Salt Master
* Run multiple Salt Minions
* Authenticate minions
* Target minions
* Use grains
* Use pillar
* Use pillar environments
* Apply states
* Use Jinja
* Use custom execution modules

### Proxy Minions

* Run a Salt Proxy Minion
* Create custom proxy modules
* Define proxy grains
* Communicate with devices using SSH
* Expose device operations through Salt execution modules

### Network automation

* Simulate a network device
* Execute structured network commands
* Retrieve interfaces
* Retrieve routes
* Retrieve device facts

### Real NOS

* Run Nokia SR Linux through Containerlab
* Connect to SR Linux over SSH
* Execute `sr_cli`
* Retrieve real interface information
* Retrieve real device information
* Propagate device errors through Salt

### Model-driven networking

* Establish NETCONF over SSH
* Inspect NETCONF server capabilities
* Discover YANG modules
* Identify OpenConfig models
* Understand candidate/commit/rollback semantics
* Understand the relationship between NETCONF, YANG, and OpenConfig

---

# 57. What Is Still To Build

The natural next stages are:

## Stage 1 — NETCONF Salt Proxy

Implement:

```text
srlinux_netconf.py
```

using:

```text
ncclient
```

Architecture:

```text
Salt
 ↓
Proxy
 ↓
ncclient
 ↓
NETCONF
 ↓
YANG
 ↓
SR Linux
```

---

## Stage 2 — Configuration Management

Move from:

```text
show interface
```

to:

```text
get configuration
```

and eventually:

```text
son
```

with:

```text
candidate
validate
commit
rollback
```

---

## Stage 3 — YANG

Learn:

```text
YANG modules
containers
lists
leafs
leaf-lists
identity
typedef
augment
namespace
```

---

## Stage 4 — OpenConfig

Use vendor-neutral models:

```text
openconfig-interfaces
openconfig-network-instance
openconfig-platform
```

instead of vendor-specific CLI commands.

---

## Stage 5 — gNMI

Explore:

```text
gNMI
```

for:

```text
Get
Set
Subscribe
```

and streaming telemetry.

---

## Stage 6 âe Vendors

Add:

```text
Nokia SR Linux
Junos
Arista EOS
Cisco IOS/XE
Cisco IOS-XR
```

and compare:

```text
CLI
NETCONF
RESTCONF
gNMI
OpenConfig
Vendor YANG
```

---

## Stage 7 — Network Automation Platform

Eventually evolve the lab toward:

```text
                        ┌─────────────────────┐
                        │ Network Automation  │
                        │     Platform        │
                        └──────────                                  │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
           Junos                SR Linux             EOS
              │                    │                    │
           NETCONF               gNMI                 NETCONF
              │        │                    │
              └────────────────────┼────────────────────┘
                                   │
                             YANG / OpenConfig
```

At that point the project starts looking less like a Salt learning exercise and more like a real network automation platform.

---

# 58. Final Mental Model

The entire lab can ultimately be reduced to this:

```text
                    Salt Ma                  │
              ┌──────────┴──────────┐
              │                     │
          Minions               Proxy Minions
              │                     │
          Servers              Network Devices
                                    │
                         ┌──────────┴──────────┐
                         │                     │
                        CLI              ven
                         │                     │
                        SSH            NETCONF / gNMI
                                               │
                                              YANG
                                               │
                                          OpenConfig
```

And the broader infrastructure model is:

```text
Terraform
   ↓
Provision infrastructure

Salt
   ↓
Configure and converge machines/devices

Docker
   ↓
Package and run applications

↓
Orchestrate workloads

NETCONF / gNMI
   ↓
Program network devices

YANG / OpenConfig
   ↓
Define structured network data
```

The most important lesson from the project is that **network automation is fundamentally the same engineering problem as infrastructure automation once the device is exposed through a programmable, structured interface**.

The difference is primarily the management interface and the data model underneath it.

