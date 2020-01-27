# controlfreak

Command and Control server for sales demo malware apps. Written in
Python + Django (with django-rest-framework) during Hackathon IX.


## Admin Interface

Provides a web interface allowing for viewing, creating, editing, and
deleting of database records. Found at `/admin`.

Also has extensive options for RBAC. A user can be provisioned to do
demos using this site by granting them "Active" and "Staff status" and
placing them in the "Demo Role" group. Site admins should be granted
"Superuser status" and do not need to be placed in a group.

You can find your device in the admin console by going to the
DeviceIds section and putting the value of your DeviceId in the search
bar. You can also scan through the `/devices` API.


## APIs

### /devices

Provides basic read access to devices, supports only GET requests.

You must be logged in to use the APIs in this section. If you are
making requests directly (e.g. using Postman or curl), you can use
"Basic Authentication" to supply credentials. In the browser, a link
to log in is provided at the top right of the page or you can log in
through the admin console.

This root API provides a paginated list of all devices in the
database including their associated data.


#### /devices/:id

Given the id of a specific device, this API returns the details of
that device.


#### /devices/:id/live

Given the id of a specific devices, this API serves very basic HTML
page displaying any exfiltrated data which automatically refreshes on
a regular interval.


### /register

Supports only POST request. The body must contain json like the
following:

```
{
    "id_type": "GOOGLE_AD_ID",
    "value": "0987",
    "app_guid": "my app guid"
}
```

Where `id_type` is on of the values from the `DeviceId` model in
`server/models.py`, `value` is the actual identifier, and `app_guid`
is a shared "secret" identifying which app is doing the registration.

HTTP response code may be either 201 if a new entry is created or 200
if the device has previous registered. The response body will be json
like the following:

```
{
    "token": "1234",
    "id": 1
}
```

Where `token` is used to identify the device on subsequent calls to
other apis and `id` is the database pk for the record which can be
used in the `/device/:id` route described below.


### /credentials

Supports only POST request. The body must contain json like the
following:

```
{
    "token": "1234",
    "user": "john",
    "secret": "password",
    "target": "com.boa.money"
}
```

Where `token` is the value from `/register`, `user` is some user
identifier like email or username, `secret` is some priveledged value
like a password or api key, and `target` identifies what the
credentials were stolen from like a website url or app package id.

HTTP response code may be either 201 if a new entry is created or 200
if the secret for an existing entry is updated. The response body will
be empty.


### /logs

Supports only POST request. The body must contain json like the
following:

```
{
    "token": "1234",
    "log": "blah blah bla"
}
```

Where `token` is the value from `/register` and `log` is whatever text
sequence should be saved. If logs already exist for this device, the
new value will be appended.

There is also `/logs/clear` which accepts POST with just the token in
the json body. Calling this api will permanently delete and logs for
the given device.


## Development

The server is written in Python using
[Django](https://docs.djangoproject.com/en/3.0/contents/) and [Django
REST Framework](https://www.django-rest-framework.org/). The
documentation for both is fairly extensive. The `server` directory
holds the vast majority of the code. The `controlfreak` directory is
mostly configuration.

The `manage.py` script is the entry point for running most things in
Django, check out `manage.py help` for more.

When making database schema change, Django does not require you to
have explicit migrations, but please use the `makemigrations` command
and commit the result.

### Testing

Tests are written using [Django's test
framework](https://docs.djangoproject.com/en/3.0/topics/testing/)
which is built on top of Python's unittest. The [coverage
library](https://coverage.readthedocs.io/en/coverage-5.0.3/) is
additionally used to calculate code coverage. Tests can be run using
`coverage run manage.py test && coverage report`.

Pylint is also configured and can be run using `pylint server`.


### Docker

Docker is used primarily to deploy the server, but you can also use it
locally, for example instead of virtualenv.

A working Dockerfile is included in this repository, so all you have
to do to get it running is `docker build -t controlfreak .` and
`docker run -p 8000:80 controlfreak`. You can find a basic explanation
of these commands in [Docker's getting started
documentation](https://docs.docker.com/get-started/part2/#build-and-test-your-image).

Since the local server runs with a sqlite database that uses the file
system for persistence, you may also want to add the `-v
$(pwd):/usr/src/app` option when running the container. This tells
docker to link the current directory into the container. In addition
to allow sqlite to persist your database, it will also allow Django to
detect changes you make to the code (outside of the Docker container)
and automatically reload.

You can also use Docker to run arbitrary commands. For example you can
run tests in the container with `docker run controlfreak coverage run
manage.py test && coverage report`.


## Deployment

Deployed in AWS using ECR, ECS, and Fargate. New code can be deployed
by logging into AWS (e.g. using oktatool) and running the
`scripts/deploy.sh` script.

The deployed service has three primary components: an ALB, an ECS
cluster, and an RDS database. The ALB is responsible for routing
external traffic to the server instances, which run the Docker image
(and therefore the Django server). The RDS database is necessary for
data persistence across deploys.

The ALB is the only component in a public subnet or with a public ip
address. The ECS instances and RDS databases are completely
unreachable from outside the VPC. There are also Security Group rules
in place for the database which only allow access from the ECS
instances and for the ECS instances which only allow access from the
ALB.

Secrets (e.g. the database password) are handled by AWS Secrets
Manager. They are injected into environment variables in JSON format
by the ECS service. This requires the role for the ECS service to have
permissions to read from Secrets Manager.


### DB Migrations

The deploy script executes an ECS task to run migration
automatically. The configuration for this must be kept up-to-date with
the running service, primarily the networkConfiguration, cluster, and
taskDefinition sections. Server instances which require migrations will
not be healthy (and therefore receive no traffic) until the migrations
have been run.


## TODO

* app guid checking
* stop using django debug mode when deployed
* CI/CD infrastructure
