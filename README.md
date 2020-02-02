# Wilma Webb Application
## Deplyment
For this to work you have to put your ssh public key in to gitlab

Then go in to the directory:
```
cd theapp/
```

Have your python working
```
pip install -r requirements.txt
```
This will install all moudels that are required to run django localy

Have a config.json file in the /etc/  folder
```
{
	"SECRET"	: "Projekt secret key",
	"EMAIL_ADDR"	: "Email address",
	"EMAIL_PASS"	: "Password for email",
	"NAME"		: "Database name",
        "USER"		: "User for data base",
        "PASSWORD"	: "Password for user for database",
        "HOST"		: "localhost",
        "PORT"		: "1234"
}
```
The Email stuff you can just coment out in the settings.py file if you just want it up and runing on local maskine
For this to work you will of course have a postgres server runing somwhere where you have access to it


After this it's just to run:
```
./manage.py makemigrations
./manage.py migrate
./manage.py runserver
```

This will run up the server on your local host. Do not close down the terminal becouse that will terminate the server

After this you can go to your webb browser and type in:
```
http://127.0.0.1:8000/
```
