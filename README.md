[![docker stars](https://img.shields.io/docker/stars/mlsecproject/gglsbl-rest.svg)](https://hub.docker.com/r/mlsecproject/gglsbl-rest/)
[![docker pulls](https://img.shields.io/docker/pulls/mlsecproject/gglsbl-rest.svg)](https://hub.docker.com/r/mlsecproject/gglsbl-rest/)
[![docker build status](https://img.shields.io/docker/build/mlsecproject/gglsbl-rest.svg)](https://hub.docker.com/r/mlsecproject/gglsbl-rest/)

# gglsbl-rest

This repository implements a Dockerized REST service to look up URLs in Google Safe Browsing 
v4 API based on [gglsbl](https://github.com/afilipovich/gglsbl) using 
[Flask](https://pypi.python.org/pypi/Flask) and 
[gunicorn](https://pypi.python.org/pypi/gunicorn).

## Basic Design

The main challenge with running gglsbl in a REST service is that the process of
updating the local sqlite database takes several minutes. Plus, the sqlite database is locked
during writes, so that will essentially cause very noticeable downtime or a race condition that
delays the updates if a single sqlite file was used.

So instead what gglsbl-rest does is to keep two sets of sqlite databases, and while one is
being used by the REST service the other is updated regularly by a chron job. 
Once the update on done on the secondary sqlite file, it starts being used by the REST service
for any new requests.

The current implementation does not use [volumes](https://docs.docker.com/engine/tutorials/dockervolumes/)
to store the sqlite files, but it could very easily be made to do so. I have found that both
running locally on my laptop and on [AWS ECS](https://aws.amazon.com/ecs/) performance was
not significantly improved by using a volume, but YMMV.

## Environment Variables

The configuration of the REST service can be done using the following environment variables:

* `GSB_API_KEY` is *required* and should contain your 
[Google Safe Browsing v4 API key](https://developers.google.com/safe-browsing/v4/get-started).

* `WORKERS` controls how many gunicorn workers to instantiate. Defaults to twice the number
of detected cores plus one.

* `TIMEOUT` controls how many seconds before gunicorn times out on a request. Defaults to 120.

* `MAX_RETRIES` controls how many times the service should retry performing the request if
an error occurs. Defaults to 3.

## Building and Running

Download the latest automated build from
[Docker Hub](https://hub.docker.com/r/mlsecproject/gglsbl-rest/) as follows:
```bash
docker pull mlsecproject/gglsbl-rest
```

Then, you can run a new container based on that image by executing, for example:
```bash
docker run -e GSB_API_KEY=<your API key> -p 127.0.0.1:5000:5000 -i mlsecproject/gglsbl-rest 
```

This will cause the service to listen on port 5000 of the host machine. Please realize that
when the service first starts it downloads a new local partial hash database from scratch 
before starting the REST service. So it might take several minutes to become available. By
starting it in interactive mode you can read the log output to notice when the gunicorn 
processes start.

## Querying the REST Service

The REST service will respond to queries for `/gglsbl/v1/lookup/<URL>`. Make sure you 
[percent encode](https://en.wikipedia.org/wiki/Percent-encoding) the URL you are querying.
If no sign of maliciousness is found, the service will return with a 404 status. Otherwise,
a 200 response with a JSON body is returned to describe it.

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

There' an additional `/gglsbl/v1/status` URL that you can access to check if the service is
running and also get some indication of how old the current sqlite database is:
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
