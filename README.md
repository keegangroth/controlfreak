# controlfreak

Command and Control server for sales demo malware apps. Written
(poorly) in Python + Django during Hackathon IX.


## APIs

### /register

Supports only POST request. The body must contain json like the
following:

```
{
    "id_type": "GOOGLE_AD_ID",
    "value": "1234",
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


### /devices

TODO


## Admin Interface

Provides a web interface allowing for viewing, creating, editing, and
deleting of database records. Also has extensive options for
RBAC. Found at `/admin`.


## Deployment

Deployed in AWS Fargate (via Docker/ECR). See the scripts directory
for more. Running instance available at
https://controlfreak.lookoutdemo.com/admin


## TODO

* automate applying migrations
* Finish README
* Tests, linting, etc
* CI infrastructure
