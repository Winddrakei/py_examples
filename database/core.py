import peewee as pw
from config import *

db = pw.SqliteDatabase(DB_PATH)


class BaseModel(pw.Model):
    class Meta:
        database = db


class User(BaseModel):
    """ Модель пользователя """
    user_id = pw.IntegerField(primary_key=True)


class Record(BaseModel):
    """ Модель выполненной команды (/low, /high, /custom) """
    record_id = pw.AutoField()
    user = pw.ForeignKeyField(User, backref="history")
    command = pw.CharField()
    item = pw.CharField()
    count = pw.CharField()
    range = pw.CharField(null=True)

    def __str__(self) -> str:
        if self.range:
            return ("{command} - Товар: {item}. Цена: {range} $. Количество: {count}"
                    .format(command=self.command, item=self.item, range=self.range, count=self.count))
        return ("{command} - Товар: {item}. Количество: {count}"
                .format(command=self.command, item=self.item, count=self.count))


def create_models() -> None:
    """ Функция, создающая модели в базе данных """
    db.create_tables(BaseModel.__subclasses__())


create_models()
