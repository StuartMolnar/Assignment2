from sqlalchemy import Column, Integer, DateTime
from base import Base

class Stats(Base):
    """ Processing Statistics """
    __tablename__ = "stats"
    id = Column(Integer, primary_key=True)
    num_bk_withdrawals = Column(Integer, nullable=False)
    num_bk_returns = Column(Integer, nullable=False)
    max_overdue_length = Column(Integer, nullable=False)
    max_overdue_fine = Column(Integer, nullable=False)
    longest_book_withdrawn = Column(Integer, nullable=False)
    last_updated = Column(DateTime, nullable=False)

    def __init__(self, num_bk_withdrawals, num_bk_returns, max_overdue_length, max_overdue_fine, longest_book_withdrawn, last_updated):
        """ Initializes a processing statistics object """
        self.num_bk_withdrawals = num_bk_withdrawals
        self.num_bk_returns = num_bk_returns
        self.max_overdue_length = max_overdue_length
        self.max_overdue_fine = max_overdue_fine
        self.longest_book_withdrawn = longest_book_withdrawn
        self.last_updated = last_updated

    def to_dict(self):
        """ Dictionary Representation of a statistics """
        dict = {}
        dict['num_bk_withdrawals'] = self.num_bk_withdrawals
        dict['num_bk_returns'] = self.num_bk_returns
        dict['max_overdue_length'] = self.max_overdue_length
        dict['max_overdue_fine'] = self.max_overdue_fine
        dict['longest_book_withdrawn'] = self.longest_book_withdrawn
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:%M:%S")
        
        return dict
