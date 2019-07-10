from os import environ, path

import logging.config
import time
from flask import Flask, request, jsonify, abort
from gglsbl import SafeBrowsingList
from subprocess import Popen

# basic app configuration and options
logging.config.fileConfig('logging.conf')
app = Flask("gglsbl-rest")
gsb_api_key = environ['GSB_API_KEY']
dbfile = path.join(environ.get('GSB_DB_DIR', '/tmp'), 'sqlite.db')
environment = environ.get('ENVIRONMENT', 'prod').lower()
max_retries = int(environ.get('MAX_RETRIES', "3"))

# Keep last query object so we can try to re-use it across requests
sbl = None
last_api_key = None


def _lookup(url, api_key, retry=1):
    # perform lookup
    global sbl, last_api_key
    try:
        if api_key != last_api_key:
            app.logger.info('re-opening database')
            sbl = SafeBrowsingList(api_key, dbfile, True)
            last_api_key = api_key
        return sbl.lookup_url(url)
    except:
        app.logger.exception("exception handling [" + url + "]")
        if retry >= max_retries:
            sbl = None
            last_api_key = None
            abort(500)
        else:
            return _lookup(url, api_key, retry + 1)


@app.route('/gglsbl/lookup/<path:url>', methods=['GET'])
@app.route('/gglsbl/v1/lookup/<path:url>', methods=['GET'])
def app_lookup(url):
    # input validation
    if not isinstance(url, str):
        abort(400)

    # find out which API key to use
    api_key = request.headers.get('x-gsb-api-key', gsb_api_key)
    if not api_key:
        app.logger.error('no API key to use')
        abort(401)

    # look up URL
    matches = _lookup(url, api_key)
    if matches:
        return jsonify(url=url, matches=[{'threat': x.threat_type, 'platform': x.platform_type,
                                          'threat_entry': x.threat_entry_type} for x in matches])
    else:
        resp = jsonify(url=url, matches=[])
        resp.status_code = 404
        return resp


@app.route('/gglsbl/status', methods=['GET'])
@app.route('/gglsbl/v1/status', methods=['GET'])
def status_page():
    return jsonify(environment=environment,
                   alternatives=[{
                       'active': True,
                       'name': dbfile,
                       'mtime': time.strftime('%Y-%m-%dT%H:%M:%S%z', time.gmtime(path.getmtime(dbfile))),
                       'ctime': time.strftime('%Y-%m-%dT%H:%M:%S%z', time.gmtime(path.getctime(dbfile))),
                       'size': path.getsize(dbfile)
                   }])


# run development Flask server if executed directly
if __name__ == '__main__':
    po = Popen("python update.py", shell=True)
    po.wait()
    app.env = 'development'
    app.run(processes=1, host="0.0.0.0", port=5001, debug=True)
