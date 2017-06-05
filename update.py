import logging.config
import time

from gglsbl import SafeBrowsingList
from os import remove, rename
from pid.decorator import pidfile

from dbfile import *

# basic app configuration and options
gsb_api_key = environ['GSB_API_KEY']
environment = environ.get('ENVIRONMENT', 'prod').lower()
logger = logging.getLogger('update')
JOURNAL = '.update-journal'


def remove_inactive(inactive):
    if path.isfile(inactive['name']):
        logger.info('removing inactive file ' + inactive['name'])
        remove(inactive['name'])
    if path.isfile(inactive['name'] + JOURNAL):
        logger.info('removing inactive file ' + inactive['name'] + JOURNAL)
        remove(inactive['name'] + JOURNAL)


# function that updates the hash prefix cache if necessary
@pidfile(piddir='/tmp')
def update_hash_prefix_cache():
    active = get_active()
    if active and active['ctime'] and active['mtime'] and min(active['ctime'], active['mtime']) >= (
                time.time() - (30 * 60)):
        # no need to update, active DB exists and is recent
        logger.info('active database is fresh')
        inactive = get_inactive()
        # remove inactivate database if it exists to free up disk space
        remove_inactive(inactive)
    else:
        # we need to update the inactive DB, so get its info and delete it
        inactive = get_inactive()
        remove_inactive(inactive)

        # download to temporary file name
        tmp_file = inactive['name'] + '.tmp'
        logger.info('downloading database to ' + tmp_file)
        sbl = SafeBrowsingList(gsb_api_key, tmp_file, True)
        sbl.update_hash_prefix_cache()
        logger.info("finished creating " + tmp_file)

        # rename to inactive file name
        if path.isfile(tmp_file + JOURNAL):
            rename(tmp_file + JOURNAL, inactive['name'] + JOURNAL)
            logger.info("renamed " + tmp_file + JOURNAL + ' to ' + inactive['name'] + JOURNAL)
        rename(tmp_file, inactive['name'])
        logger.info("renamed " + tmp_file + ' to ' + inactive['name'])


if __name__ == '__main__':
    logging.config.fileConfig(environ.get("LOGGING_CONFIG", 'logging.conf'))
    update_hash_prefix_cache()
