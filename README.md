# Wilma Webb Application
## Deplyment
Clone the repo

Then go in to the directory:
```
cd finite/
```

Have your python working
```
pip install -r requirements.txt
```
This will install all moudels that are required to run django localy

Have a config.json file in the /etc/config.json
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
        "CRYP_PASS_1"   : "Hash salt or encryption key",
        "CRYP_PASS_2"   : "Hash salt or encryption key",
        "CRYP_PASS_3"   : "Hash salt or encryption key",
	"MAIL_RECIVERS"	: ["your mail"],
	"CLASS_HASH"	: "Hash salt or encryption key",
	"SCHOOL_HASH"	: "Hash salt or encryption key",
	"LINK_HASH"	: "Hash salt or encryption key",
	"SCHOOL_CRYPT_pass"	: "Hash salt or encryption key",
	"HOUR_PASS"	: "Hash salt or encryption key"
}
```

For this to work you will of course have a postgres server runing somwhere where you have access to it or change the settings for the database in the settings file


After this it's just to run:
```
./manage.py migrate
./manage.py runserver
```

This will run up the server on your local host. Do not close down the terminal becouse that will terminate the server

If something is already running on port 8000 the runserver command will fail and you need to run it again and type a port that is not in user after ./manage.py runserver (example) 8001
After this you can go to your webb browser and type in:
```
http://127.0.0.1:8000/
```
