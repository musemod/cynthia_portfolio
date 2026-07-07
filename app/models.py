import datetime
from peewee import Model, CharField, TextField, DateTimeField
from app.db import mydb

class TimelinePost(Model):
    name = CharField()
    email = CharField()
    content = TextField()
    created_at = DateTimeField(default=datetime.datetime.now) # not .now()
    
    '''
    default=datetime.datetime.now() calls now() once, at import time, so every row would get the same timestamp (the moment the module loaded) instead of the time each row is created. Passing datetime.datetime.now (no parens) tells peewee to call it fresh each time a row is inserted.
    '''
    
    class Meta:
        database = mydb

mydb.connect()
mydb.create_tables( [TimelinePost] )

