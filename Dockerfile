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
    && apt install -y openssh-server \
    && mv ./sshd_config /etc/ssh/sshd_config\
    && pip install django-debug-toolbar==3.2.2 \
    && pip install django-notifications-hq==1.6.0 \
    && pip install boto3==1.20.26 \
    && pip install django-storages==1.12.3 \
    && apt install memcached \
    && pip install python-memcached==1.59 \
    && apt install cache \
    && pip install cache==3.5.3 \
    && useradd -s  /bin/bash iree\
    && usermod -aG sudo iree

CMD ["/bin/bash"]
