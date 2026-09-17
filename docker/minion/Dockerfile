FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        gnupg \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Add Salt Project repository
RUN mkdir -m 755 -p /etc/apt/keyrings && \
    curl -fsSL \
        https://packages.broadcom.com/artifactory/api/security/keypair/SaltProjectKey/public \
        | gpg --dearmor \
        | tee /etc/apt/keyrings/salt-archive-keyring.pgp > /dev/null && \
    curl -fsSL \
        https://github.com/saltstack/salt-install-guide/releases/latest/download/salt.sources \
        | tee /etc/apt/sources.list.d/salt.sources

# Install Salt Minion
RUN apt-get update && \
    apt-get install -y --no-install-recommends salt-minion && \
    rm -rf /var/lib/apt/lists/*

EXPOSE 4505 4506

CMD ["salt-minion", "-l", "info"]