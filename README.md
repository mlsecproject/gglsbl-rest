[![docker stars](https://img.shields.io/docker/stars/mlsecproject/gglsbl-rest.svg)](https://hub.docker.com/r/mlsecproject/gglsbl-rest/) [![docker pulls](https://img.shields.io/docker/pulls/mlsecproject/gglsbl-rest.svg)](https://hub.docker.com/r/mlsecproject/gglsbl-rest/) [![docker build status](https://img.shields.io/docker/build/mlsecproject/gglsbl-rest.svg)](https://hub.docker.com/r/mlsecproject/gglsbl-rest/) [![<CircleCI>](https://circleci.com/gh/mlsecproject/gglsbl-rest.svg?style=svg)](https://app.circleci.com/pipelines/github/mlsecproject/gglsbl-rest)

# gglsbl-rest

This repository implements a Dockerized REST service to look up URLs in Google Safe Browsing v4 API based on [gglsbl](https://github.com/afilipovich/gglsbl) using [Flask](https://pypi.python.org/pypi/Flask) and [gunicorn](https://pypi.python.org/pypi/gunicorn).

## Basic Design

The main challenge with running gglsbl in a REST service is that the process of updating the local sqlite database takes several minutes. Plus, the sqlite database is locked during writes by default, so that would essentially cause very noticeable downtime or a race condition.

So what gglsbl-rest does since version 1.4.0 is to set the sqlite database to [write-ahead logging](https://sqlite.org/wal.html) mode so that readers and writers can work concurrently. A scheduled task runs every 30 minutes to update the database and then performs a [full checkpoint](https://sqlite.org/pragma.html#pragma_wal_checkpoint) to ensure readers have optimal performance.

Versions before 1.4.0 maintained two sets of files on disk and switched between them, which is why the status endpoint has the output format lists "alternatives". But the current approach has many advantages, as it reuses fresh downloaded data across updates and cached full hash data.

The regular update is executed using [APScheduler](https://pypi.org/project/APScheduler/) on the [gunicorn](https://pypi.python.org/pypi/gunicorn) master process. For security reasons, [gunicorn](https://pypi.python.org/pypi/gunicorn) is executed with a regular user called `gglsbl` using the Dockerfile `USER` directive.

## Environment Variables

The configuration of the REST service can be done using the following environment variables:

* `GSB_API_KEY` is *required* and should contain your [Google Safe Browsing v4 API key](https://developers.google.com/safe-browsing/v4/get-started).

* `WORKERS` controls how many gunicorn workers to instantiate. Defaults to 8 times the number of detected cores plus one.

* `TIMEOUT` controls how many seconds before gunicorn times out on a request. Defaults to 120.

* `MAX_REQUESTS` controls how many requests a worker can server before it is restarted, as per the [max_requests](http://docs.gunicorn.org/en/stable/settings.html#max-requests) gunicorn setting. Defaults to restarting workers after they serve 16,384 requests.

* `LIMIT_REQUEST_LINE` controls the maximum size of the HTTP request line (operation, protocol version, URI and query parameters), as per the [limit_request_line](http://docs.gunicorn.org/en/stable/settings.html#limit-request-line) gunicorn setting. Defaults to 8190, set to 0 to allow any length.

* `KEEPALIVE` controls how long a persistent connection can be idle before it is closed, as per the [keepalive](http://docs.gunicorn.org/en/stable/settings.html#keepalive) gunicorn setting. Defaults to 60 seconds.

* `MAX_RETRIES` controls how many times the service should retry performing the request if an error occurs. Defaults to 3.

* `HTTPS_PROXY` sets the proxy URL if the service is running behind a proxy. Not set by default. (HTTP_PROXY is not necessary as gglsbl-rest only queries HTTPS URLs)

## Running

### Docker

You can run the latest automated build from [Docker Hub](https://hub.docker.com/r/mlsecproject/gglsbl-rest/) as follows:
```bash
docker run -e GSB_API_KEY=<your API key> -p 127.0.0.1:5000:5000 mlsecproject/gglsbl-rest 
```

This will cause the service to listen on port 5000 of the host machine. Please realize that when the service first starts it downloads a new local partial hash database from scratch before starting the REST service. So it might take several minutes to become available. 

You can run `docker logs --follow <container name/ID>` to tail the output and determine when the gunicorn workers start, if necessary.

### Okteto Cloud

First, [add a secret](https://okteto.com/docs/cloud/secrets) to your Okteto Cloud namespace with the value of your `GSB_API_KEY` key.

Next, click on the following button to deploy the application:

[![Develop on Okteto](https://okteto.com/develop-okteto.svg)](https://cloud.okteto.com/deploy?repository=https://github.com/mlsecproject/gglsbl-rest)


This will execute an automated pipeline that will make the service to listen on https://rest-[YOUR-GITHUB-ID].cloud.okteto.net/port. Please realize that when the service first starts it downloads a new local partial hash database from scratch before starting the REST service. So it might take several minutes to become available. 

You can see the logs from the Okteto Cloud dashboard to determine when the gunicorn workers start, if necessary.

Once the application is running on Okteto Cloud, you can develop it by executing the following commands:

```
$ okteto up
 ✓  Development container activated
 ✓  Files synchronized
    Namespace: YOUR-GITHUB-ID
    Name:      rest
    Forward:   5000 -> 5000

Welcome to your development container. Happy coding!
YOUR-GITHUB-ID:rest okteto> pip install -r requirements.txt
YOUR-GITHUB-ID:rest okteto> python app.py

### Production

In production, you might want to mount `/home/gglsbl/db` in a [tmpfs RAM disk](https://docs.docker.com/engine/admin/volumes/tmpfs/) for improved performance. Recommended size is 4+ gigabytes, which is roughly twice of a freshly initialized database, but YMMV.

## Querying the REST Service

The REST service will respond to queries for `/gglsbl/v1/lookup/<URL>`. Make sure you [percent encode](https://en.wikipedia.org/wiki/Percent-encoding) the URL you are querying. If no sign of maliciousness is found, the service will return with a 404 status. Otherwise, a 200 response with a JSON body is returned to describe it.

Here's an example query and response to a test URL where matches are guaranteed to be found, pretty formatted using [jq](https://stedolan.github.io/jq/):
```bash
$ curl "http://127.0.0.1:5000/gglsbl/v1/lookup/http%3A%2F%2Ftestsafebrowsing.appspot.com%2Fapiv4%2FANY_PLATFORM%2FSOCIAL_ENGINEERING%2FURL%2F" | jq
{
  "matches": [
    {
      "platform": "ANY_PLATFORM",
      "threat": "SOCIAL_ENGINEERING",
      "threat_entry": "URL"
    },
    {
      "platform": "WINDOWS",
      "threat": "SOCIAL_ENGINEERING",
      "threat_entry": "URL"
    },
    {
      "platform": "LINUX",
      "threat": "SOCIAL_ENGINEERING",
      "threat_entry": "URL"
    },
    {
      "platform": "OSX",
      "threat": "SOCIAL_ENGINEERING",
      "threat_entry": "URL"
    },
    {
      "platform": "ALL_PLATFORMS",
      "threat": "SOCIAL_ENGINEERING",
      "threat_entry": "URL"
    },
    {
      "platform": "CHROME",
      "threat": "SOCIAL_ENGINEERING",
      "threat_entry": "URL"
    }
  ],
  "url": "http://testsafebrowsing.appspot.com/apiv4/ANY_PLATFORM/SOCIAL_ENGINEERING/URL/"
}
```

Here's an example lookup of google.com which should yield no matches (notice the 404 status code):
```bash
$ curl -i "http://127.0.0.1:5000/gglsbl/v1/lookup/http%3A%2F%2Fgoogle.com"
HTTP/1.1 404 NOT FOUND
Server: gunicorn/19.9.0
Date: Wed, 10 Jul 2019 21:41:21 GMT
Connection: close
Content-Type: application/json
Content-Length: 41

{"matches":[],"url":"http://google.com"}
```

There' an additional `/gglsbl/v1/status` URL that you can access to check if the service is running and also get some indication of how old the current sqlite database is:
```bash
$ curl "http://127.0.0.1:5000/gglsbl/v1/status" | jq
{
  "alternatives": [
    {
      "active": true,
      "ctime": "2017-10-30T20:20:55+0000", 
      "mtime": "2017-10-30T20:20:55+0000", 
      "name": "/home/gglsbl/db/sqlite.db", 
      "size": 2079985664
    }
  ], 
  "environment": "prod"
}
```

A much more convenient way to query the service from the command-line, though, is to use [gglsbl-rest-client](https://github.com/seanmcfeely/gglsbl-rest-client), maintained by [Sean McFeely](https://github.com/seanmcfeely).


## Who's using gglsbl-rest

* [neonknight](https://github.com/neonknight) reports gglsbl-rest is used as a bridge between the [fuglu mail filter engine](https://gitlab.com/fumail/fuglu) and Google Safebrowsing API through a [plug-in](https://gitlab.com/fumail/fuglu-extra-plugins/blob/master/safebrowsing/gglsbl.py).
* [Sean McFeely](https://github.com/seanmcfeely) reports gglsbl-rest is used in [ACE - Analysis Correlation Engine](https://github.com/ace-ecosystem/ACE) to help security analysts perform their activities in a more automated manner, including Google Safebrowsing API lookup of URLs.

If your project or company are using gglsbl-rest and you would like them to be listed here, please open a [GitHub issue](https://github.com/mlsecproject/gglsbl-rest/issues) and we'll include you.
