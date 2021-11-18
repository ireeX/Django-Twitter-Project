FROM ubuntu:18.04

RUN echo 'Start!' \
    apt update \
    apt install vim \
    apt install python3 python3-pip wget dos2unix sudo lsb-release iproute2 \

    update-alternatives --install /usr/bin/python python /usr/bin/python3.6 2 \