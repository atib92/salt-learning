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
