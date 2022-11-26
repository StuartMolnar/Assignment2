import connexion
from connexion import NoContent
import requests
import yaml
import logging
import logging.config
import uuid

import datetime
import json
from pykafka import KafkaClient

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def get_health():
    return NoContent, 200

def get_book_withdrawal(index):
    """ Get BW in History """
    hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]

    # Here we reset the offset on start so that we retirce message at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to 100ms. There is a risk that this loop 
    # never stops if the index is large and messages are constantly being recieved.
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=100)

    logger.info(f"Retrieving BW at index {index}")

    try:
        i = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            if msg['type'] != 'WithdrawalEvent':
                continue

            if i == index:
                logger.info(f"Returned status code 200 and WithdrawalEvent at index {index}: {msg}")
                return msg, 200

            i+=1
    except:
            logger.error("No more messages found")
    
    logger.error(f"Could not find BW at index {index}")
    return { "message": "Not Found"}, 404

def get_book_return(index):
    """ Get BR in History """
    hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]

    # Here we reset the offset on start so that we retirce message at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to 100ms. There is a risk that this loop 
    # never stops if the index is large and messages are constantly being recieved.
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=100)

    logger.info(f"Retrieving BR at index {index}")
    try:
        i = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            if msg['type'] != 'ReturnEvent':
                continue

            if i == index:
                logger.info(f"Returned status code 200 and ReturnEvent at index {index}: {msg}")
                return msg, 200

            i+=1
    except:
            logger.error("No more messages found")
    
    logger.error(f"Could not find BR at index {index}")
    return { "message": "Not Found"}, 404
   


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml",
            strict_validation=True,
            validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110)