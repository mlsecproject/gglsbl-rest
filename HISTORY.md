# gglsbl-rest

## v1.5.25
Updated to Alpine 3.15.

## v1.5.24 (2021-11-17)
Updated to Alpine 3.14.3 and APScheduler 3.8.1.

## v1.5.23 (2021-06-02)
Updated to Alpine 3.13.5 for a variety of CVE fixes, such as CVE-2021-3449 , CVE-2021-3450 and CVE-2021-3177.

## v1.5.22 (2021-01-27)
Updated to Alpine 3.13 and APScheduler 3.7.0.

## v1.5.21 (2020-09-29)
Install yarl, multidict, flask and gunicorn with Alpine packages instead of using pip to avoid PEP 517 issues.

## v1.5.20 (2020-08-26)
Contribution from @pchico83:
* Added support for running on Okteto Cloud;
* Improved docker build time by streamlining Dockerfile.

## v1.5.19 (2020-08-07)
Updated to Alpine 3.12.

## v1.5.18 (2020-05-03)
Updated to Alpine 3.11.6 and flask 1.1.2.

## v1.5.17 (2020-03-31)
Updated to Alpine 3.11.5.

## v1.5.16 (2020-01-23)
Updated to Alpine 3.11.3.

## v1.5.15 (2019-12-23)
Updated to Alpine 3.11.

## v1.5.14 (2019-12-09)
Updated to Alpine 3.10.3, APScheduler 3.6.3 and gunicorn 20.0.4 for functional and security fixes.

## v1.5.13 (2019-09-02)
Updated to Alpine 3.10.2 and APScheduler 3.6.1 for functional and security fixes.

## v1.5.12 (2019-07-10)
* Updated dependencies to Flask 1.1.1, which fixes a logging issue where some log entries were being duplicated.
* Updated body of 404 response when no matches are found by gglsbl to contain the same JSON format as the 200 response.

## v1.5.11 (2019-06-21)
Use alpine:3.10 for latest OS updates.

## v1.5.10 (2019-06-04)
Updated dependencies Flask (1.0.3), APScheduler (3.6.0) and gglsbl (1.4.15).

## v1.5.9 (2019-05-10)
Mitigate CVE-2019-5021 as per https://alpinelinux.org/posts/Docker-image-vulnerability-CVE-2019-5021.html

## v1.5.8 (2019-02-15)
- Removed use of pid package since APScheduler max_instances=1 should already prevent concurrent executions of the update process.

## v1.5.7 (2019-02-01)
- Use alpine:3.9 for latest OS updates;
- Upgrade pid to 2.2.1.

## v1.5.6 (2019-01-08)
- Migrate to Python 3.

## v1.5.5 (2018-12-21)
- Use alpine:3.8 as base image directly for latest package and OS updates;
- Update dependencies: gglsbl 1.4.14, and gunicorn 19.9.0;
- Replace use of crond with apscheduler Python package to run regular updates;
- Since crond is not longer used, no processes need to run as root and we can use `USER` Dockerfile directive to drop privileges.

## v1.5.4 (2018-06-28)
- Upgrade Flask to 1.0.2;
- Upgrade gglsbl to 1.4.11;
- Upgrade gunicorn to 19.8.1.

## v1.5.3 (2018-04-14)
- Upgraded to gglsbl-rest 1.4.10 and pid 2.2.0;
- Removed dead code and unnecessary WAL mode setting from update.py.

## v1.5.2 (2018-03-07)
- Updated gglsbl to version 1.4.8 for [fixes and improvements](https://github.com/afilipovich/gglsbl/releases).

## v1.5.1 (2017-12-14)
- Use alpine:3.7 as base image directly for latest package and OS updates.

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
