from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime

class BookWithdrawal(Base):
    """ Book Withdrawal """

    __tablename__ = "book_withdrawal"

    id = Column(Integer, primary_key=True)
    withdrawal_id = Column(String(36), nullable=False)
    book_name = Column(String(250), nullable=False)
    genre = Column(String(100), nullable=False)
    num_of_pages = Column(Integer, nullable=False)
    days_allowed = Column(Integer, nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(36), nullable=False)

    def __init__(self, withdrawal_id, book_name, genre, num_of_pages, days_allowed, timestamp, trace_id):
        self.withdrawal_id = withdrawal_id
        self.book_name = book_name
        self.genre = genre
        self.num_of_pages = num_of_pages
        self.days_allowed = days_allowed
        self.timestamp = timestamp 
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.trace_id = trace_id

    def to_dict(self):
        """ Dictionary Representation of a book withdrawal """
        dict = {}
        dict['withdrawal_id'] = self.withdrawal_id
        dict['book_name'] = self.book_name
        dict['genre'] = self.genre
        dict['num_of_pages'] = self.num_of_pages
        dict['days_allowed'] = self.days_allowed
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id

        return dict


