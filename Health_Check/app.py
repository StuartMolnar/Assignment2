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
from health import Health


with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine(f"sqlite:///{app_config['datastore']['filename']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def get_health_check():
    return ('a', 'a', 'a', 'a')

def check_health():
    logger.info("Health check initiated")

    receiver_endpoint = requests.get(f"{app_config['eventstore']['receiver_url']}/get_health")
    storage_endpoint = f"{app_config['eventstore']['storage_endpoint']}/get_health"
    processing_endpoint = f"{app_config['eventstore']['processing_endpoint']}/get_health"
    audit_endpoint = f"{app_config['eventstore']['audit_endpoint']}/get_health"

    
    responses = {"Receiver" : requests.get(receiver_endpoint),
                 "Storage" : requests.get(storage_endpoint),
                 "Processing" : requests.get(processing_endpoint),
                 "Audit" : requests.get(audit_endpoint)}
    last_updated = datetime.datetime.now()

    logger.debug("responses:", responses)

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

