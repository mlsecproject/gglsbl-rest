import logging.config
from os import environ, path

from gglsbl import SafeBrowsingList
from pid.decorator import pidfile

# basic app configuration and options
gsb_api_key = environ['GSB_API_KEY']
dbfile = path.join(environ.get('GSB_DB_DIR', '/tmp'), 'sqlite.db')
environment = environ.get('ENVIRONMENT', 'prod').lower()
logger = logging.getLogger('update')
JOURNAL = '.update-journal'


# function that updates the hash prefix cache if necessary
@pidfile(piddir='/tmp')
def update_hash_prefix_cache():
    logger.info('opening database at ' + dbfile)
    sbl = SafeBrowsingList(gsb_api_key, dbfile, True)
    with sbl.storage.get_cursor() as dbc:
        dbc.execute('PRAGMA journal_mode = WAL')
    sbl.storage.db.commit()

    logger.info('updating database at ' + dbfile)
    sbl.update_hash_prefix_cache()

    logger.info('checkpointing database at ' + dbfile)
    with sbl.storage.get_cursor() as dbc:
        dbc.execute('PRAGMA wal_checkpoint(FULL)')
    sbl.storage.db.commit()

    logger.info("all done!")


if __name__ == '__main__':
    logging.config.fileConfig(environ.get("LOGGING_CONFIG", 'logging.conf'))
    update_hash_prefix_cache()
