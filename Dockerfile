FROM ubuntu:18.04

RUN echo 'Start!' \
    && ln -sf /bin/bash /bin/sh \
    && apt update \
    && apt install -y vim \
    && apt install -y python3 python3-pip wget dos2unix sudo lsb-release iproute2

COPY requirements.txt provision.sh sshd_config /vagrant/

RUN cd /vagrant \
    && chmod +x ./provision.sh \
    && bash provision.sh \
    && service mysql start \
    && bash ./provision.sh \
    && python -m pip install django-debug-toolbar \
    && apt install -y openssh-server \
    && mv ./sshd_config /etc/ssh/sshd_config\
    && useradd -s  /bin/bash iree\
    && usermod -aG sudo iree

CMD ["/bin/bash"]
