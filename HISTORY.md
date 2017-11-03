# gglsbl-rest

## v1.5.0 (2017-11-03)
- Run update.py and main gunicorn process as a regular `gglsbl` user instead of root for added security. 

## v1.4.0 (2017-10-30)
- Use a single database in sqlite WAL mode (#10);
- Default value of WORKERS is now 8 per detected CPU core plus one.

## v1.3.2 (2017-10-29)
- Use Alpine 3.6 instead of 3.4, since this moves us from sqlite 3.13 to 3.20.1 and seems to solve https://github.com/afilipovich/gglsbl/issues/28 with gglsbl 1.4.6;
- Use gglsbl 1.4.6 again.

## v1.3.1 (2017-10-28)
- Revert to gglsbl 1.4.5 to avoid exceptions on queries as per https://github.com/afilipovich/gglsbl/issues/28;
- Delete SafeBrowsingList object after database update to ensure sqlite connection is closed before moving the database file.

## v1.3.0 (2017-10-26)
- Added environment variable KEEPALIVE to control persistent connection idle period;
- Added environment variable LIMIT_REQUEST_LINE to increase the default gunicorn maximum HTTP request line size, since we embed full URLs into our URI.

## v1.2.0 (2017-10-25)
- Updated logging configuration so that even background tasks write to Docker logs;
- Define regular recycling of gunicorn workers as inspired by https://github.com/amrael/gglsbl-rest/commit/0fd51f17ee879c736387eeb93512a1d11223a68c.

## v1.1.0 (2017-10-19)
- Updated to gglsbl v1.4.6 and Flask 0.12.2;
- Reuse gglsbl SafeBrowsingList object across requests for improved performance (#2);
- Retry gglsbl lookup a configurable number of times before giving up (#4).

## v1.0.0 (2017-06-05)
Initial release.
