# Django-Twitter-Project

## Setup Docker Environment
### Start Docker:
```
docker run -p 80:8000 -p 9005:22 -v "$(pwd)":/vagrant -i -t --name twitterenv ubuntu:18.04 bash
apt install sudo
sudo bash startup.sh
```
### Provision
```
sudo bash ./provision.sh 
echo 'export PATH="/home/iree/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Start MySQL
```
sudo service mysql start
```

### re-run provision.sh to setup mysql
```
sudo bash ./provision.sh
```

### Try MySQL
```
mysql -u root -p
```


### Setup SSH
```
sudo apt install openssh-server
```
Find `PermitRootLogin prohibit-password` and change to `PermitRootLogin yes`to enable ssh remote visit docker
```
sudo vim /etc/ssh/sshd_config
```
```
sudo service ssh restart
```
You can connect to docker on your host with following command:
```
ssh jiuzhang@localhost -p 9005
```
Remember to configure Pycharm Interpreter

## Run Django Project
username/passwd: admin/admin
``` 
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
python manage.py createsuperuser
```
Start the server again and visit `localhost/admin`, we can login as admin to Django
```
python manage.py runserver 0.0.0.0:8000
```


