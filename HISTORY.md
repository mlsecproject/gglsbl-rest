# gglsbl-rest

## v1.2.0 (2017-10-25)
- Updated logging configuration so that even background tasks write to Docker logs;
- Define regular recycling of gunicorn workers as inspired by https://github.com/amrael/gglsbl-rest/commit/0fd51f17ee879c736387eeb93512a1d11223a68c.

## v1.1.0 (2017-10-19)
- Updated to gglsbl v1.4.6 and Flask 0.12.2;
- Reuse gglsbl SafeBrowsingList object across requests for improved performance (#2);
- Retry gglsbl lookup a configurable number of times before giving up (#4).

## v1.0.0 (2017-06-05)
Initial release.
