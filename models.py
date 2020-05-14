from peewee import SqliteDatabase, Model
from peewee import CharField, DateField, BooleanField, IntegerField

db = SqliteDatabase('database.db')

class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = CharField(max_length=12, primary_key=True)
    username = CharField(max_length=32, null=True, unique=True)
    balance = IntegerField(null=True)

    class Meta:
        db_table = 'users'