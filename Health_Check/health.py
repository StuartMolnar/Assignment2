from sqlalchemy import Column, Integer, DateTime, String
from base import Base

class Stats(Base):
    """ Processing Statistics """
    __tablename__ = "stats"
    id = Column(Integer, primary_key=True)
    receiver = Column(String(100), nullable=False)
    storage = Column(String(100), nullable=False)
    max_overdue_length = Column(String(100), nullable=False)
    audit = Column(String(100), nullable=False)
    last_updated = Column(DateTime, nullable=False)

    def __init__(self, receiver, storage, processing, audit, last_updated):
        """ Initializes a processing statistics object """
        self.receiver = receiver
        self.storage = storage
        self.processing = processing
        self.audit = audit
        self.last_updated = last_updated

    def to_dict(self):
        """ Dictionary Representation of a statistics """
        dict = {}
        dict['receiver'] = self.receiver
        dict['storage'] = self.storage
        dict['processing'] = self.processing
        dict['audit'] = self.audit
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:%M:%S")
        
        return dict