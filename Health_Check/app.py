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
import time


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
    session = DB_SESSION()

    health = session.query(Health).order_by(Health.id.desc()).first()

    return health.to_dict()

def check_health():
    logger.info("Health check initiated")
    now = datetime.datetime.now()

    logger.debug('receiver reached')

    try:
        receiver_endpoint = f"{app_config['eventstore']['receiver_url']}/health"
        receiver_response = requests.get(receiver_endpoint, timeout=5).status_code
        logger.debug('receiver try entered')
    except Exception as e:
        logger.debug(f'receiver exception: {e}')
        receiver_response = 0
        logger.debug('receiver exception entered')

    try:
        storage_endpoint = f"{app_config['eventstore']['storage_url']}/health"
        storage_response = requests.get(storage_endpoint, timeout=5).status_code
    except Exception as e:
        logger.debug(f'storage exception: {e}')
        storage_response = 0
    
    try:
        processing_endpoint = f"{app_config['eventstore']['processing_url']}/health"
        processing_response = requests.get(processing_endpoint, timeout=5).status_code
    except Exception as e:
        logger.debug(f'processing exception: {e}')
        processing_response = 0
    
    try:
        audit_endpoint = f"{app_config['eventstore']['audit_url']}/health"
        audit_response = requests.get(audit_endpoint, timeout=5).status_code
    except Exception as e:
        logger.debug(f'audit exception: {e}')
        audit_response = 0

    receiver = ("Running" if receiver_response == 200 else "Down")
    storage = ("Running" if storage_response == 200 else "Down")
    processing = ("Running" if processing_response == 200 else "Down")
    audit = ("Running" if audit_response == 200 else "Down")


    current_time = datetime.datetime.now()
    time_elapsed = (current_time - now).total_seconds()
    logger.debug(f'responses: {[receiver, storage, processing, audit, current_time.strftime("%Y-%m-%dT%H:%M:%S")]}')

    while time_elapsed < 15:
        time.sleep(0.2)
        time_elapsed = (datetime.datetime.now() - now).total_seconds()
    

    session = DB_SESSION()
    
    
    health_response = Health(receiver,
                    storage,
                    processing,
                    audit,
                    datetime.datetime.now())

    session.add(health_response)
    session.commit()
    session.close()
    logger.info('Service health data stored to database')
    
    



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

