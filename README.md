# Django-Twitter-Project

## Setup Docker Environment
### Start Docker:
```
docker run -p 80:8000 -p 9005:22 -v "$(pwd)":/vagrant -i -t --name mytwitterenv mytwitter:1.0
```
### Provision
```
apt install sudo
sudo bash startup.sh
sudo bash ./provision.sh 
echo 'export PATH="/home/iree/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Start MySQL
```
sudo service mysql start
```

### re-run provision.sh to set up mysql
```
sudo bash ./provision.sh
```

### Try MySQL
```
mysql -u root -p
```


### Setup SSH to configure Pycharm Interpreter
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
ssh iree@localhost -p 9005
```
To configure Pycharm Interpreter:  
In Pycharm -> Preferences -> Project:XXX -> Python Interpreter -> Add... -> SSH Interpreter -> host:localhost / username:username / port:9005 -> next -> Password -> Next -> Change nothing -> Finish

## Run Django Project
Run following command to create a new django project
```
django-admin.py startproject twitter
```
migrate the database structure
superuser username/passwd: admin/admin
``` 
python manage.py migrate
```
Must run on `0.0.0.0` rather than `127.0.0.1` for host visit
```
python manage.py runserver 0.0.0.0:8000
python manage.py createsuperuser
```
Start the server again and visit `localhost/admin`, we can log in as admin to Django
```
python manage.py runserver 0.0.0.0:8000
```

## Install Django Rest Framework

Add `djangorestframework==3.12.2` to `requirements.txt` file. And execute following command to install Django Rest Framework. 
```
pip install -r requirements.txt 
```
Or, you can install by using `pip install djangorestframework` command. After installation, use `pip freeze > requirements.txt` to export your all settings for records. the requirements.txt file will increase since there also be some dependent packages.

**Tips: Each time update the requirements.txt, it usually needs some update to settings.py file**

Add `'rest_framework'` to settings.py to `INSTALLED_APPS`.
And add `REST_FRAMEWORK` for future use.

#Tips for Real World
**1. Use whitelist, not blacklist**
>In Django Rest Framework, it provides some method such as `list, retrieve, destroy, put, patch...` in `ModelViewSet`class. We can create our class inheriting from ModelViewSet. This class will inherit all the method. However, it's not recommend for in your work. Because you should design the class only with necessary methods. Redundancy may bring risk.

**2. Use UTC time in DataBase**

**3. When create a new attribute in a table in the Database, choose *null = True* rather than set a default value**
>Setting default value may bring trouble, especially when the table is very large. For example, there is a million data in the table, setting a new default value will cause a *for loop* to iterate this table, which may lead the database crush.

**4. Don't delete data in database**
> You can set an attribute such as *is_valid* to mark this data is useless
> rather than delete it.

**5. Changing table structure in your ORM,
you need to ...**
> **When add attribute:**
> First migrate database, then deploy code
> 
> **When delete attribute**
> First deploy code, then migrate database
> 
> **Because:**
> It's ok for a web framework to have more data in database 
> than in ORM. If you restart your webserver (deploy code) first after add attributes,
> the server may crush since it cannot find data in the haven't migrated database.
> 
> **Caution: DON'T ADD AND DELETE AT THE SAME TIME**