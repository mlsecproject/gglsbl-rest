[![docker stars](https://img.shields.io/docker/stars/mlsecproject/gglsbl-rest.svg)](https://hub.docker.com/r/mlsecproject/gglsbl-rest/) [![docker pulls](https://img.shields.io/docker/pulls/mlsecproject/gglsbl-rest.svg)](https://hub.docker.com/r/mlsecproject/gglsbl-rest/) [![docker build status](https://img.shields.io/docker/build/mlsecproject/gglsbl-rest.svg)](https://hub.docker.com/r/mlsecproject/gglsbl-rest/)

# gglsbl-rest

This repository implements a Dockerized REST service to look up URLs in Google Safe Browsing v4 API based on [gglsbl](https://github.com/afilipovich/gglsbl) using [Flask](https://pypi.python.org/pypi/Flask) and [gunicorn](https://pypi.python.org/pypi/gunicorn).

## Basic Design

The main challenge with running gglsbl in a REST service is that the process of updating the local sqlite database takes several minutes. Plus, the sqlite database is locked during writes, so that will essentially cause very noticeable downtime or a race condition that delays the updates if a single sqlite file was used.

So instead what gglsbl-rest does is to keep two sets of sqlite databases, and while one is being used by the REST service the other is updated regularly by a chron job. Once the update on done on the secondary sqlite file, it starts being used by the REST service for any new requests.

## Environment Variables

The configuration of the REST service can be done using the following environment variables:

* `GSB_API_KEY` is *required* and should contain your [Google Safe Browsing v4 API key](https://developers.google.com/safe-browsing/v4/get-started).

* `WORKERS` controls how many gunicorn workers to instantiate. Defaults to twice the number of detected cores plus one.

* `TIMEOUT` controls how many seconds before gunicorn times out on a request. Defaults to 120.

* `MAX_REQUESTS` controls how many requests a worker can server before it is restarted, as per the [max-requests gunicorn setting](http://docs.gunicorn.org/en/stable/settings.html#max-requests). Default to restarting worker after it serves 16,384 requests.

* `MAX_RETRIES` controls how many times the service should retry performing the request if an error occurs. Defaults to 3.

## Running

You can run the latest automated build from [Docker Hub](https://hub.docker.com/r/mlsecproject/gglsbl-rest/) as follows:
```bash
docker run -e GSB_API_KEY=<your API key> -p 127.0.0.1:5000:5000 mlsecproject/gglsbl-rest 
```

This will cause the service to listen on port 5000 of the host machine. Please realize that when the service first starts it downloads a new local partial hash database from scratch before starting the REST service. So it might take several minutes to become available. 

You can run `docker logs --follow <container name/ID>` to tail the output and determine when the gunicorn workers start, if necessary.

In production, you might want to mount `/root/gglsbl-rest/db` in a [tmpfs RAM disk](https://docs.docker.com/engine/admin/volumes/tmpfs/) for dramatically improved performance. Recommended size is 4 gigabytes to accommodate the worst case scenario of two full databases on disk at once during the update process.

## Querying the REST Service

The REST service will respond to queries for `/gglsbl/v1/lookup/<URL>`. Make sure you [percent encode](https://en.wikipedia.org/wiki/Percent-encoding) the URL you are querying. If no sign of maliciousness is found, the service will return with a 404 status. Otherwise, a 200 response with a JSON body is returned to describe it.

Here's an example query and response:
```bash
$ curl "http://127.0.0.1:5000/gglsbl/v1/lookup/http%3A%2F%2Ftestsafebrowsing.appspot.com%2Fapiv4%2FANY_PLATFORM%2FSOCIAL_ENGINEERING%2FURL%2F"
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
      "platform": "CHROME",
      "threat": "SOCIAL_ENGINEERING",
      "threat_entry": "URL"
    },
    {
      "platform": "LINUX",
      "threat": "SOCIAL_ENGINEERING",
      "threat_entry": "URL"
    },
    {
      "platform": "ALL_PLATFORMS",
      "threat": "SOCIAL_ENGINEERING",
      "threat_entry": "URL"
    }
  ],
  "url": "http://testsafebrowsing.appspot.com/apiv4/ANY_PLATFORM/SOCIAL_ENGINEERING/URL/"
}
```

There' an additional `/gglsbl/v1/status` URL that you can access to check if the service is running and also get some indication of how old the current sqlite database is:
```bash
$ curl "http://127.0.0.1:5000/gglsbl/v1/status"
{
  "alternatives": [
    {
      "active": true,
      "ctime": "2017-06-05T05:08:29+0000",
      "mtime": "2017-06-05T05:08:29+0000",
      "name": "/root/gglsbl-rest/db/gsb_v4.a.db",
      "size": 1592377344,
      "switch": "a"
    },
    {
      "active": false,
      "ctime": null,
      "mtime": null,
      "name": "/root/gglsbl-rest/db/gsb_v4.b.db",
      "size": null,
      "switch": "b"
    }
  ],
  "environment": "prod"
}
```

## Who's using gglsbl-rest

* [Niddel](https://www.niddel.com) uses gglsbl-rest as an enrichment in its Magnet product;

* [neonknight](https://github.com/neonknight) reports gglsbl-rest is used as a bridge between the [fuglu mail filter engine](https://github.com/gryphius/fuglu) and Google Safebrowsing API through a [plug-in](https://github.com/gryphius/fuglu-extra-plugins/blob/master/safebrowsing/gglsbl.py).

If your project or company are using gglsbl-rest and you would like them to be listed here, please open a [GitHub issue](https://github.com/mlsecproject/gglsbl-rest/issues) and we'll include you.
