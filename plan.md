# SaltStack Learning Lab

This repository builds a small SaltStack lab locally using **WSL + Docker + VS Code**.

The goal is not to build a production Salt deployment. The goal is to progressively understand how Salt works:

- Salt master / minion architecture
- Minion authentication and keys
- Remote execution
- Grains
- Pillar
- Salt states
- Jinja
- Targeting
- Multiple minions
- Role-based configuration
- Proxy minions

The lab intentionally grows in stages so that each Salt concept is introduced before the next layer depends on it.

---

## Target architecture

We will eventually build this:

```text
                         Docker network
                              │
                    ┌─────────┴─────────┐
                    │                   │
              ┌─────▼─────┐       ┌────▼─────┐
              │   master  │       │  control │
              │  Salt     │       │  tooling │
              └─────┬─────┘       └──────────┘
                    │
          ┌─────────┼───────────────┐
          │         │               │
     ┌────▼────┐ ┌──▼───────┐ ┌────▼─────┐
     │ web-1   │ │ worker-1 │ │ db-1     │
     │ minion  │ │ minion   │ │ minion   │
     └─────────┘ └──────────┘ └───────────┘

                    Later:
                  ┌────────────┐
                  │ proxy      │
                  │ minion     │
                  └─────┬──────┘
                        │
                  external device
```

The first milestone is deliberately much smaller:

```text
WSL
└── Docker
    ├── salt-master
    └── salt-minion
```

Both containers are on the same Docker network. The master is reached by its Docker DNS name rather than `localhost`.

Salt uses a master/client model: the master issues commands and minions execute them. Minions authenticate with the master using Salt keys. [Salt installation overview](https://docs.saltproject.io/salt/install-guide/en/latest/topics/overview.html)

---

# Phase 0 — Prepare WSL

## 0.1 Verify WSL version

From Windows PowerShell:

```powershell
wsl.exe -l -v
```

Make sure your Ubuntu distribution is running under **WSL 2**.

If necessary:

```powershell
wsl.exe --set-version Ubuntu 2
```

Docker Desktop's WSL integration requires WSL 2 for this workflow. See the official Docker WSL documentation:
https://docs.docker.com/desktop/features/wsl/

Inside WSL:

```bash
cat /etc/os-release
uname -a
```

---

# Phase 1 — Install Docker

## Recommended approach: Docker Desktop + WSL integration

For a Windows + WSL development environment, use Docker Desktop's WSL 2 backend rather than installing a second Docker daemon inside Ubuntu.

Docker explicitly recommends uninstalling a separately installed Docker Engine/CLI inside the WSL distribution before using Docker Desktop's WSL integration, because running both can cause conflicts.

Official documentation:

https://docs.docker.com/desktop/features/wsl/

Install Docker Desktop on Windows, start it, then enable:

```text
Docker Desktop
  → Settings
    → Resources
      → WSL Integration
        → Enable your Ubuntu distribution
```

Then restart WSL if necessary:

```powershell
wsl --shutdown
```

Start Ubuntu again.

Verify from WSL:

```bash
docker version
```

Then:

```bash
docker run --rm hello-world
```

You should see Docker's hello-world output.

Also verify Compose:

```bash
docker compose version
```

We will use **Docker Compose** for the lab because it makes the master/minion topology explicit and makes adding more minions later very easy.

---

# Phase 2 — Create the Git repository structure

From WSL:

```bash
mkdir -p ~/projects
cd ~/projects

mkdir salt-learning
cd salt-learning

git init
```

Open the repository in VS Code:

```bash
code .
```

The repository will eventually look roughly like:

```text
salt-learning/
├── README.md
├── plan.md
├── docker-compose.yml
├── docker/
│   ├── master/
│   │   └── Dockerfile
│   └── minion/
│       └── Dockerfile
├── master/
│   ├── config/
│   ├── keys/
│   └── file_roots/
├── minions/
│   ├── web/
│   ├── worker/
│   └── db/
├── pillar/
│   ├── top.sls
│   ├── common.sls
│   ├── web.sls
│   ├── worker.sls
│   └── db.sls
└── states/
    ├── top.sls
    ├── common.sls
    ├── web.sls
    ├── worker.sls
    └── db.sls
```

Do **not** create all of this immediately.

We will grow the repository as the learning progresses.

---

# Phase 3 — Understand the Docker networking model

Before installing Salt, understand one important Docker concept.

We will create a Docker network:

```text
salt-net
```

The containers will communicate using Docker DNS:

```text
salt-master
```

Therefore the minion configuration will eventually contain:

```yaml
master: salt-master
```

NOT:

```yaml
master: localhost
```

Inside a container:

```text
localhost
```

means **that container itself**.

This is one of the reasons containers are useful for this lab: they make the master/minion network boundary explicit.

---

# Phase 4 — Build the Salt master container

Create:

```text
docker/
└── master/
    └── Dockerfile
```

The master image should contain the Salt master package and run:

```text
salt-master
```

in the foreground.

Do not install Salt directly into WSL. Salt itself should live inside the containers.

The official Salt documentation recommends the standard package installation approach and currently provides Salt packages through the Salt Project repositories.

https://docs.saltproject.io/salt/install-guide/en/latest/topics/install-by-operating-system/linux-deb.html

For the container image, we can use an appropriate Ubuntu base image and install the current Salt package from the official Salt repository.

---

# Phase 5 — Build the Salt minion container

Create:

```text
docker/
└── minion/
    └── Dockerfile
```

The minion image should contain:

```text
salt-minion
```

and run:

```text
salt-minion
```

in the foreground.

Its configuration will point to:

```yaml
master: salt-master
id: lab-minion
```

Salt's official configuration documentation recommends using `/etc/salt/master.d/*.conf` and `/etc/salt/minion.d/*.conf` for custom configuration rather than modifying the large default configuration files.

https://docs.saltproject.io/salt/install-guide/en/latest/topics/configure-master-minion.html

---

# Phase 6 — Create docker-compose.yml

Create:

```text
docker-compose.yml
```

The initial topology should contain exactly two services:

```text
salt-master
salt-minion
```

Both should be attached to:

```text
salt-net
```

Conceptually:

```yaml
services:

  salt-master:
    ...

  salt-minion:
    ...

networks:
  salt-net:
    ...
```

The master should expose the Salt ports to the minion network:

```text
4505
4506
```

These are Salt's normal master/minion communication ports.

We do not need to expose them to Windows for this first lab because both containers communicate over the internal Docker network.

---

# Phase 7 — Start the lab

Build and start:

```bash
docker compose up --build -d
```

Check:

```bash
docker compose ps
```

Expected:

```text
NAME          STATUS
salt-master   running
salt-minion   running
```

Inspect logs:

```bash
docker compose logs salt-master
```

and:

```bash
docker compose logs salt-minion
```

For debugging:

```bash
docker compose logs -f salt-master
```

or:

```bash
docker compose logs -f salt-minion
```

---

# Phase 8 — Verify container networking

Enter the minion:

```bash
docker compose exec salt-minion bash
```

From inside the minion:

```bash
getent hosts salt-master
```

You should receive the Docker-network IP of the master.

Then exit:

```bash
exit
```

This establishes the networking foundation before introducing Salt.

---

# Phase 9 — Understand Salt keys

Start the master and minion containers.

The minion will generate its identity/key and present it to the master.

From WSL:

```bash
docker compose exec salt-master salt-key -L
```

You should see something similar to:

```text
Accepted Keys:
Denied Keys:
Unaccepted Keys:
lab-minion
Rejected Keys:
```

Accept it:

```bash
docker compose exec salt-master salt-key -a lab-minion
```

Verify:

```bash
docker compose exec salt-master salt-key -L
```

Now:

```text
Accepted Keys:
lab-minion
```

This is an important Salt concept:

```text
minion
   │
   │ authentication key
   ▼
master
   │
   │ accept
   ▼
trusted minion
```

The official Salt quickstart follows this same key-acceptance flow.

https://docs.saltproject.io/salt/install-guide/en/latest/topics/quickstart.html

---

# Phase 10 — First Salt command

Run:

```bash
docker compose exec salt-master salt '*' test.ping
```

Expected:

```text
lab-minion:
    True
```

Then:

```bash
docker compose exec salt-master salt '*' test.version
```

And:

```bash
docker compose exec salt-master salt '*' cmd.run 'hostname'
```

At this point we have:

```text
VS Code
   │
   ▼
Git repository
   │
   ▼
Docker Compose
   │
   ├── salt-master
   │       │
   │       │ Salt protocol
   │       ▼
   └── salt-minion
```

---

# Phase 11 — Add Grains

Grains are facts about a minion.

Run:

```bash
docker compose exec salt-master \
  salt 'lab-minion' grains.items
```

Then query individual grains:

```bash
docker compose exec salt-master \
  salt 'lab-minion' grains.get os
```

```bash
docker compose exec salt-master \
  salt 'lab-minion' grains.get kernel
```

```bash
docker compose exec salt-master \
  salt 'lab-minion' grains.get num_cpus
```

Think:

```text
Grains = facts about the machine
```

Examples:

```text
OS
kernel
CPU architecture
CPU count
memory
hostname
network interfaces
```

Later we will add custom grains for roles such as:

```yaml
role: web
role: worker
role: db
```

and use those for targeting.

---

# Phase 12 — Add Pillar

Create a persistent pillar directory in the repository:

```text
pillar/
├── top.sls
└── common.sls
```

Configure the master so that:

```text
pillar/
```

is mounted as the Salt pillar root.

Create:

```yaml
# pillar/top.sls

base:
  '*':
    - common
```

Then:

```yaml
# pillar/common.sls

app:
  environment: development
  owner: salt-learning
```

Verify:

```bash
docker compose exec salt-master \
  salt 'lab-minion' pillar.items
```

Then:

```bash
docker compose exec salt-master \
  salt 'lab-minion' pillar.get app:environment
```

Think:

```text
Grains
  = facts discovered from the minion

Pillar
  = configuration/data supplied by the master
```

---

# Phase 13 — Add Salt states

Create:

```text
states/
└── demo.sls
```

The first state should manage something extremely simple, for example:

```text
/tmp/salt-demo/
    hello.txt
```

The state should:

1. Create the directory.
2. Create the file.
3. Put some text into the file.

Apply it:

```bash
docker compose exec salt-master \
  salt 'lab-minion' state.apply demo
```

Then inspect the minion:

```bash
docker compose exec salt-minion \
  cat /tmp/salt-demo/hello.txt
```

This introduces the central Salt concept:

```text
State
  ↓
desired state
  ↓
minion
  ↓
actual system
```

---

# Phase 14 — Combine State + Pillar + Jinja

Modify the state so that it consumes pillar values.

For example:

```jinja
Application: {{ pillar['app']['name'] }}
Environment: {{ pillar['app']['environment'] }}
Owner: {{ pillar['app']['owner'] }}
```

Apply the state again:

```bash
docker compose exec salt-master \
  salt 'lab-minion' state.apply demo
```

Inspect the generated file.

This is the first point where the major Salt building blocks come together:

```text
                 Salt Master
                     │
          ┌──────────┼──────────┐
          │          │          │
       Pillar      State      Target
          │          │          │
          └──────────┼──────────┘
                     │
                     ▼
                 Minion
                     │
                  Grains
                     │
                     ▼
              Managed system
```

---

# Phase 15 — Add targeting

Learn the three basic targeting styles.

## Minion ID

```bash
salt 'lab-minion' test.ping
```

## Glob

```bash
salt '*' test.ping
```

## Grain targeting

```bash
salt -G 'os:Ubuntu' test.ping
```

Later:

```bash
salt -G 'role:web' test.ping
```

and:

```bash
salt -G 'role:worker' test.ping
```

This will become important once we have multiple minions.

---

# Phase 16 — Expand to multiple minions

Once the single-minion lab is understood, change Docker Compose to:

```text
salt-master
    │
    ├── web-1
    ├── worker-1
    └── db-1
```

Each container should have:

```yaml
id: web-1
```

or:

```yaml
id: worker-1
```

or:

```yaml
id: db-1
```

Then:

```bash
salt-key -L
```

will show:

```text
Unaccepted Keys:
    web-1
    worker-1
    db-1
```

Accept them:

```bash
salt-key -A
```

Then:

```bash
salt '*' test.ping
```

should contact all three.

---

# Phase 17 — Introduce roles using Grains

Give each minion a role.

For example:

```yaml
role: web
```

```yaml
role: worker
```

```yaml
role: db
```

Now:

```bash
salt -G 'role:web' test.ping
```

targets only the web minions.

Likewise:

```bash
salt -G 'role:worker' test.ping
```

and:

```bash
salt -G 'role:db' test.ping
```

This should be one of the major learning milestones.

---

# Phase 18 — Role-specific Pillar

Change:

```text
pillar/
```

to:

```text
pillar/
├── top.sls
├── common.sls
├── web.sls
├── worker.sls
└── db.sls
```

Example:

```yaml
# web.sls

role:
  name: web

app:
  port: 8080
```

Worker:

```yaml
# worker.sls

role:
  name: worker

worker:
  concurrency: 4
```

DB:

```yaml
# db.sls

role:
  name: db

database:
  port: 5432
```

The master should assign the appropriate pillar data to each minion.

---

# Phase 19 — Role-specific states

Build:

```text
states/
├── top.sls
├── common.sls
├── web.sls
├── worker.sls
└── db.sls
```

The objective is to reach:

```text
                    Salt Master
                         │
             ┌───────────┼───────────┐
             │           │           │
          web-1       worker-1      db-1
             │           │           │
          role:web    role:worker   role:db
             │           │           │
          web state   worker state  db state
```

At this point the lab starts resembling a real infrastructure configuration-management system.

---

# Phase 20 — Add a second web/worker node

Expand to:

```text
master
  │
  ├── web-1
  ├── web-2
  ├── worker-1
  ├── worker-2
  └── db-1
```

Now practice:

```bash
salt -G 'role:web' test.ping
```

```bash
salt -G 'role:worker' test.ping
```

```bash
salt -G 'role:web' state.apply web
```

This demonstrates why targeting and role-based configuration matter.

---

# Phase 21 — Introduce a Proxy Minion

Only after understanding normal minions should we introduce proxy minions.

A proxy minion represents a device/system that cannot run a normal Salt minion.

Conceptually:

```text
                    Salt Master
                         │
                         │
                   proxy-minion
                         │
                         ▼
                 external target
```

The proxy minion still participates in the Salt master/minion model, but the proxy process translates Salt operations into operations understood by the target.

This will let us explore:

- `salt-proxy`
- proxy configuration
- proxy grains
- proxy pillar
- proxy states
- external systems/devices
- why proxy minions exist

---

# Phase 22 — Eventually manage Docker itself with Salt

After understanding Salt's normal master/minion model, we can explore Salt's Docker execution/state modules.

For example:

```text
Salt Minion
     │
     ▼
Docker API
     │
     ├── containers
     ├── networks
     └── images
```

Salt provides Docker container state functionality, including `docker_container`.

https://docs.saltproject.io/en/latest/ref/states/all/salt.states.docker_container.html

This is a separate concept from our current setup:

> We are currently using Docker to provide machines on which Salt runs.

Later we can use Salt to manage Docker resources.

---

# Recommended learning sequence

Do not skip ahead.

```text
01. WSL
      ↓
02. Docker
      ↓
03. Docker Compose
      ↓
04. Master container
      ↓
05. Minion container
      ↓
06. Docker networking
      ↓
07. Salt keys
      ↓
08. Remote execution
      ↓
09. Grains
      ↓
10. Pillar
      ↓
11. States
      ↓
12. Jinja
      ↓
13. Targeting
      ↓
14. Multiple minions
      ↓
15. Roles
      ↓
16. Role-specific pillar
      ↓
17. Role-specific states
      ↓
18. Multiple nodes per role
      ↓
19. Proxy minions
      ↓
20. Salt managing Docker
```

---

# Suggested repository milestones

Use Git commits to preserve each learning stage.

```text
01-initial-repo
02-docker-working
03-master-minion-running
04-minion-key-accepted
05-first-salt-command
06-grains
07-pillar
08-first-state
09-jinja
10-targeting
11-multiple-minions
12-role-based-grains
13-role-based-pillar
14-role-based-states
15-proxy-minion
16-salt-manages-docker
```

This makes the repository useful as a learning journal as well as a working lab.

---

# VS Code workflow

All configuration and code should be edited in VS Code.

From WSL:

```bash
cd ~/projects/salt-learning
code .
```

Use the VS Code terminal for:

```bash
docker compose ...
git ...
```

Use VS Code for:

```text
Dockerfiles
docker-compose.yml
Salt configuration
Pillar YAML
Salt states
Jinja templates
README.md
```

Avoid editing files directly inside running containers except for temporary debugging.

The repository should be the source of truth.

---

# Final learning objective

By the end of this project, the following command should make intuitive sense:

```bash
salt -G 'role:web' state.apply web
```

You should be able to mentally expand it as:

```text
salt
 │
 ├── Targeting
 │     └── find minions whose grain says role=web
 │
 ├── State
 │     └── apply the web desired state
 │
 ├── Pillar
 │     └── provide web-specific configuration
 │
 ├── Jinja
 │     └── render configuration using pillar/grains
 │
 └── Minion
       └── make the actual system converge to the desired state
```

That is the core Salt mental model this repository is intended to teach.

