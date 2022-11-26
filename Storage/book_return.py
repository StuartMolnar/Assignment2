from sqlalchemy import Column, Integer, String, DateTime, Float
from base import Base
import datetime


class BookReturn(Base):
    """ Book Return """

    __tablename__ = "book_return"

    id = Column(Integer, primary_key=True)
    return_id = Column(String(36), nullable=False)
    book_name = Column(String(250), nullable=False)
    days_overdue = Column(Integer, nullable=False)
    expected_fine = Column(Float, nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(100), nullable=False)

    def __init__(self, return_id, book_name, days_overdue, expected_fine, timestamp, trace_id):
        """ Initializes a book return """
        self.return_id = return_id
        self.book_name = book_name
        self.days_overdue = days_overdue
        self.expected_fine = expected_fine
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.trace_id = trace_id

    def to_dict(self):
        dict = {}
        dict['return_id'] = self.return_id
        dict['book_name'] = self.book_name
        dict['days_overdue'] = self.days_overdue
        dict['expected_fine'] = self.expected_fine
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id

        return dict

