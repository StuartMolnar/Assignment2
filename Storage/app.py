from threading import Thread
import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import mysql.connector
import pymysql
from base import Base
from book_withdrawal import BookWithdrawal
from book_return import BookReturn
import logging
import logging.config
import uuid
import yaml
import datetime

import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread


with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())


DB_ENGINE = create_engine(f"mysql+pymysql://{app_config['datastore']['user']}:{app_config['datastore']['password']}@{app_config['datastore']['hostname']}:{app_config['datastore']['port']}/{app_config['datastore']['db']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


logger.info(f"Connecting to DB. Hostname:{app_config['datastore']['hostname']}, Port:{app_config['datastore']['port']}")


#---GET Requests---

def get_health():
    return NoContent, 200

def get_withdrawals(timestamp):
    """ Gets new book withdrawals after the timestamp """

    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")

    withdrawals = session.query(BookWithdrawal).filter(BookWithdrawal.date_created >= timestamp_datetime)

    
    withdrawals_list = []

    for withdrawal in withdrawals:
        withdrawals_list.append(withdrawal.to_dict())

    session.close()

    logger.info(f"Query for Book Withdrawal events after {timestamp} returns {len(withdrawals_list)} results")
    return withdrawals_list, 200


def get_returns(timestamp):
    """ Gets new book returns after the timestamp """

    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")

    returns = session.query(BookReturn).filter(BookReturn.date_created >= timestamp_datetime)
    returns_list = []
    for bkreturn in returns:
        returns_list.append(bkreturn.to_dict())

    session.close()


    logger.info(f"Query for Book Return events after {timestamp} returns {len(returns_list)} results")
    return returns_list, 200



def store_book_withdrawal(payload):
    """ Recieves a book withdraw event """

    session = DB_SESSION()

    bw = BookWithdrawal(payload['withdrawal_id'],
                        payload['book_name'],
                        payload['genre'],
                        payload['num_of_pages'],
                        payload['days_allowed'],
                        payload['timestamp'],
                        payload['trace_id'])
                        
    session.add(bw)
    session.commit()
    session.close()

    logger.debug(f"Stored event WithdrawalEvent with a trace id of {payload['trace_id']}")


    return NoContent, 201


#---Store payload in DB---

def store_book_return(payload):
    """ Recieves a book return event """

    session = DB_SESSION()

    br = BookReturn(payload['return_id'],
                    payload['book_name'],
                    payload['days_overdue'],
                    payload['expected_fine'],
                    payload['timestamp'],
                    payload['trace_id'])

    session.add(br)
    session.commit()
    session.close()

    logger.debug(f"Stored event WithdrawalEvent with a trace id of {payload['trace_id']}")


    return NoContent, 201


def process_messages():
    """ Process event messages """
    hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]

    #Create a consume n a consumer group, that only reads new messages
    #(uncomitted message) when the service re-starts (i.e., it doesn't read 
    # all the old messages from the history in the message queue)
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)

    #this is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info(f'Message: {msg}')

        payload = msg['payload']

        if msg['type'] == 'WithdrawalEvent':
            store_book_withdrawal(payload)
        elif msg['type'] == 'ReturnEvent':
            store_book_return(payload)

        consumer.commit_offsets()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml",
            strict_validation=True,
            validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)

