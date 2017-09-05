import logging.config
import time

from flask import Flask, request, jsonify, abort
from gglsbl import SafeBrowsingList
from multiprocessing import cpu_count

from dbfile import *

# basic app configuration and options
app = Flask("gglsbl-rest")
gsb_api_key = environ['GSB_API_KEY']
environment = environ.get('ENVIRONMENT', 'prod').lower()
max_retries = 3


def _lookup(url, active_name, retry=max_retries):
    try:
        sbl = SafeBrowsingList(gsb_api_key, active_name, True)
        resp = sbl.lookup_url(url)
    except Exception:
        if retry > 0:
            # sleep before calling again. increase timeout with every run
            time.sleep(0.1 * (max_retries - retry + 1))
            # recursively retry in case of error
            resp = _lookup(url, active_name, retry=retry-1)
        else:
            raise
    return resp


@app.route('/gglsbl/lookup/<path:url>', methods=['GET'])
@app.route('/gglsbl/v1/lookup/<path:url>', methods=['GET'])
def app_lookup(url):
    # input validation
    if not isinstance(url, (str, unicode)):
        abort(400)

    # resolve entries
    active = get_active()
    if not active or not active['mtime']:
        abort(503)
    try:
        resp = _lookup(url, active['name'])
    except Exception:
        app.logger.exception("exception handling [" + url + "]")
        abort(500)
    else:
        if resp:
            matches = [{'threat': x.threat_type, 'platform': x.platform_type,
                        'threat_entry': x.threat_entry_type} for x in resp]
            return jsonify({'url': url, 'matches': matches})
        else:
            abort(404)


@app.route('/gglsbl/status', methods=['GET'])
@app.route('/gglsbl/v1/status', methods=['GET'])
def status_page():
    retval = {'alternatives': get_alternatives(), 'environment': environment}
    for i in range(len(retval['alternatives'])):
        if retval['alternatives'][i]['mtime']:
            retval['alternatives'][i]['mtime'] = time.strftime('%Y-%m-%dT%H:%M:%S%z',
                                                               time.gmtime(retval['alternatives'][i]['mtime']))
        if retval['alternatives'][i]['ctime']:
            retval['alternatives'][i]['ctime'] = time.strftime('%Y-%m-%dT%H:%M:%S%z',
                                                               time.gmtime(retval['alternatives'][i]['ctime']))
        if path.isfile(retval['alternatives'][i]['name']):
            retval['alternatives'][i]['size'] = path.getsize(retval['alternatives'][i]['name'])
        else:
            retval['alternatives'][i]['size'] = None
    return jsonify(retval)


# run internal Flask server if executed directly
if __name__ == '__main__':
    logging.config.fileConfig('logging.conf')
    app.run(processes=int(environ.get('WORKERS', cpu_count() * 2 + 1)))
