import os
from peewee import MySQLDatabase, SqliteDatabase
from dotenv import load_dotenv

load_dotenv()


if os.getenv("TESTING") == "true":
    mydb = SqliteDatabase("file:memory?mode=memory&cache=shared", uri=True)
else:
    mydb = MySQLDatabase(os.getenv("MYSQL_DATABASE"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        host=os.getenv("MYSQL_HOST"),
        port=3306
    )
