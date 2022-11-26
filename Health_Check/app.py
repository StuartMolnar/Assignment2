from requests import session
import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.background import BackgroundScheduler
from base import Base
import yaml
import logging
import logging.config
import datetime
import requests


with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine(f"sqlite:///{app_config['datastore']['filename']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


'''
        CREATE TABLE health
        (id INTEGER PRIMARY KEY ASC,
        receiver VARCHAR(100) NOT NULL,
        storage VARCHAR(100) NOT NULL,
        processing VARCHAR(100) NOT  NULL,
        audit VARCHAR(100) NOT NULL,
        last_updated VARCHAR(100) NOT NULL)

'''

'''
eventstore:
  receiver_url: http://localhost:8080
  storage_url: http://localhost:8090
  processing_url: http://localhost:8100
  audit_url: http://localhost:8110
'''

def get_health_check():
    pass

def check_health():
    receiver_endpoint = f"{app_config['eventstore']['receiver_url']}/get_health"
    storage_endpoint = f"{app_config['eventstore']['storage_endpoint']}/get_health"
    processing_endpoint = f"{app_config['eventstore']['processing_endpoint']}/get_health"
    audit_endpoint = f"{app_config['eventstore']['audit_endpoint']}/get_health"

    responses = {"Receiver" : requests.get(receiver_endpoint),
                 "Storage" : requests.get(storage_endpoint),
                 "Processing" : requests.get(processing_endpoint),
                 "Audit" : requests.get(audit_endpoint)}
    last_updated = datetime.datetime.now()

    session = DB_SESSION()
    health_response = Health(receiver_endpoint,
                    storage_endpoint,
                    processing_endpoint,
                    audit_endpoint,
                    last_updated)




def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(check_health, 'interval', seconds=app_config['scheduler']['period_sec'])
    logger.info("Periodic processing initiated")
    sched.start()




app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml",
            strict_validation=True,
            validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8120, use_reloader=False)

