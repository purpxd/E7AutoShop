from sqlobject import *
import os
from datetime import datetime
database_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.db")

connection_string = f'sqlite:///{database_file}'
connection = connectionForURI(connection_string)
sqlhub.processConnection = connection

class Sessions(SQLObject):
    date = DateCol(default=datetime.today())
    covenants = IntCol()
    mystics = IntCol()
    friendships = IntCol()
    session_duration = IntCol()
    session_refreshes = IntCol()
    gems_spent = IntCol()
    gold_spent = IntCol()
    

class Settings(SQLObject):
    enable_friendship = IntCol(default=0)
    port_number = IntCol(default=None, notNull=False)
    delay = IntCol(default=0)
Sessions.createTable(ifNotExists=True)
Settings.createTable(ifNotExists=True)


