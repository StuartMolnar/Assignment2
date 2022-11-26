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
from stats import Stats
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

def get_health():
    return NoContent, 200

def get_stats():
    """ Get stats """
    logger.info("GET request initiated")

    session = DB_SESSION()
    stats = session.query(Stats).order_by(Stats.last_updated.desc())
    session.close()
    stats_list = []


    for stat in stats:
        stats_list.append(stat.to_dict())


    if stats_list == []:
        logger.error(f"Statistics do not exist {404}")
        return "Statistics do not exist ", 404
    
    logger.info("GET request completed")
    logger.debug(f"stats: {stats_list[0]}")
    return stats_list[0], 200

withdrawals_data = []
returns_data = []
def populate_stats():
    """ Periodically update stats """
    
    now = datetime.datetime.now()
    logger.info(f'{now}')

    # logic for newly added entries
    # -----
    withdrawals_endpoint = f"{app_config['eventstore']['url']}/books/withdrawals?timestamp={now.strftime('%Y-%m-%dT%H:%M:%SZ')}"
    withdrawals_response = requests.get(withdrawals_endpoint)

    logger.debug(f'withdrawals_endpoint = {withdrawals_endpoint}')
    logger.debug(f'withdrawals_response = {withdrawals_response}')

    
    for response in withdrawals_response.json():
        logger.debug(f"inside response for loop - response = {response}")
        withdrawals_data.append(response)

    if withdrawals_response.status_code != 200:
        logger.info('Status code is not 200')
        
    logger.debug(f"withdrawals_data = {withdrawals_data}")

    #-------------------------------

    returns_endpoint = f"{app_config['eventstore']['url']}/books/returns?timestamp={now.strftime('%Y-%m-%dT%H:%M:%SZ')}"
    returns_response = requests.get(returns_endpoint)

    logger.debug(f'returns_endpoint = {returns_endpoint}')
    logger.debug(f'returns_response = {returns_response}')

    for response in returns_response.json():
        returns_data.append(response)

    if returns_response.status_code != 200:
        logger.info('Status code is not 200')

    logger.debug(f"returns_data = {returns_data}")
    #--------------------------------
    
    num_bk_withdrawals = len(withdrawals_data)
    num_bk_returns = len(returns_data)

    max_overdue_length = 0
    max_overdue_fine = 0.00
    longest_book_withdrawn = 0
    
    
    logger.debug(f'returns_data = {returns_data}')
    for bkreturn in returns_data:
        logger.debug(f"bkreturn = {bkreturn}")
        
        if bkreturn['days_overdue'] > max_overdue_length:
            max_overdue_length = bkreturn['days_overdue']
        if bkreturn['expected_fine'] > max_overdue_fine:
            max_overdue_fine = bkreturn['expected_fine']
    
    for bkwithdrawal in withdrawals_data:
        if bkwithdrawal['num_of_pages'] > longest_book_withdrawn:
            longest_book_withdrawn = bkwithdrawal['num_of_pages']
    

    if withdrawals_response.json() != [] or returns_response.json() != []:
            
        session = DB_SESSION()
        last_updated = datetime.datetime.now()

        stats = Stats(num_bk_withdrawals,
                    num_bk_returns,
                    max_overdue_length,
                    max_overdue_fine,
                    longest_book_withdrawn,
                    last_updated
        )
                            
        session.add(stats)

        session.commit()
        session.close()
    



    

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    logger.info("Periodic processing initiated")
    sched.start()




app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml",
            strict_validation=True,
            validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)

