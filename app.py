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

# Keep last query object so we can try to re-use it across requests
sbl = None
last_api_key = None
last_name = None
last_ctime = None


@app.route('/gglsbl/lookup/<path:url>', methods=['GET'])
@app.route('/gglsbl/v1/lookup/<path:url>', methods=['GET'])
def app_lookup(url):
    # input validation
    if not isinstance(url, (str, unicode)):
        abort(400)

    # find out which API key to use
    api_key = request.headers.get('x-gsb-api-key', gsb_api_key)
    if not api_key:
        app.logger.error('no API key to use')
        abort(401)

    # find out which is the active database
    active = get_active()
    if not active or not active['mtime']:
        abort(503)

    # look up URL
    global sbl, last_api_key, last_name, last_ctime
    try:
        if api_key != last_api_key or active['name'] != last_name or active['ctime'] != last_ctime:
            app.logger.info('re-opening database')
            sbl = SafeBrowsingList(api_key, active['name'], True)
            last_api_key = api_key
            last_name = active['name']
            last_ctime = active['ctime']
        resp = sbl.lookup_url(url)
    except:
        app.logger.exception("exception handling [" + url + "]")
        sbl = None
        last_api_key = None
        last_name = None
        last_ctime = None
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
