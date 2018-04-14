import logging.config
from os import environ, path

from gglsbl import SafeBrowsingList
from pid.decorator import pidfile

# basic app configuration and options
gsb_api_key = environ['GSB_API_KEY']
dbfile = path.join(environ.get('GSB_DB_DIR', '/tmp'), 'sqlite.db')
logger = logging.getLogger('update')


# function that updates the hash prefix cache if necessary
@pidfile(piddir=environ.get('GSB_DB_DIR', '/tmp'))
def update_hash_prefix_cache():
    logger.info('opening database at ' + dbfile)
    sbl = SafeBrowsingList(gsb_api_key, dbfile, True)

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
