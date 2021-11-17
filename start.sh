#!/usr/bin/env bash

# basic set up environment
apt update
apt install vim
apt install python3 python3-pip wget dos2unix sudo lsb-release iproute2

# create user
passwd root
adduser iree
usermod -aG sudo iree
su - iree
cd ../../vagrant/


# run provision.sh
sudo bash ./provision.sh 
echo 'export PATH="/home/iree/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc


# try mysql
sudo service mysql start

# re-run provision.sh to setup mysql
sudo bash ./provision.sh