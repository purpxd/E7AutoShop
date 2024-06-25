from sqlobject import *
import os
from datetime import datetime, timedelta
database_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.db")
connection_string = f'sqlite:///{database_file}'
connection = connectionForURI(connection_string)
sqlhub.processConnection = connection


class Sessions(SQLObject):
    date = DateCol(default=datetime.today().strftime("%Y-%m-%d"))
    covenants = IntCol()
    mystics = IntCol()
    gems_spent = IntCol()
    gold_spent = IntCol()
    
    @classmethod
    def create_update(cls, date, covenants, mystics, gems, gold):
        entry = cls.selectBy(date=date).getOne(default=None)
        if entry is None:
            cls(date=date, covenants=covenants, mystics=mystics, gems_spent=gems, gold_spent=gold)
        else:
            entry.covenants += covenants
            entry.mystics += mystics
            entry.gems_spent += gems
            entry.gold_spent += gold
    @classmethod
    def get_data(cls):
            return cls.select(orderBy='-date')

Sessions.createTable(ifNotExists=True)