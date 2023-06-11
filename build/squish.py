from datetime import datetime
from collections import defaultdict
from sqlalchemy import create_engine, Column, Integer, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
class Session(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True)
    date = Column(Date, default=datetime.today())
    covenants = Column(Integer)
    mystics = Column(Integer)
    friendships = Column(Integer)
    session_duration = Column(Integer)
    session_refreshes = Column(Integer)
    gems_spent = Column(Integer)
    gold_spent = Column(Integer)

def squeeze():
    engine = create_engine('sqlite:///data.db')
    Base.metadata.create_all(engine)
    Session.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    today = datetime.today().date()

    matching_rows = session.query(Session).filter(Session.date != today).all()

    combined_data = defaultdict(lambda: defaultdict(int))
    for row in matching_rows:
        date_str = row.date.strftime('%Y-%m-%d') 
        combined_data[date_str]['covenants'] += row.covenants
        combined_data[date_str]['mystics'] += row.mystics
        combined_data[date_str]['friendships'] += row.friendships
        combined_data[date_str]['session_duration'] += row.session_duration
        combined_data[date_str]['session_refreshes'] += row.session_refreshes
        combined_data[date_str]['gems_spent'] += row.gems_spent
        combined_data[date_str]['gold_spent'] += row.gold_spent

    session.query(Session).filter(Session.date != today).delete()

    for date, data in combined_data.items():
        session.add(Session(date=datetime.strptime(date, '%Y-%m-%d').date(), **data))

    session.commit()

    all_rows = session.query(Session).all()
    for row in all_rows:
        print(row.date, row.covenants, row.mystics)