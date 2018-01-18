# jwt-examples
Some simple cases about JWT tokens (PyJWT) + Flask

## Requirements
- docker
- docker-compose
- curl

## Build
```
$ cd example
$ docker-compose build
```

## Start examples
```
$ cd example
$ docker-compose up
```

## Simple
In this case there are two entities/services: issuer and calc, both using Flask to implement a simple, and incomplete, HTTP Rest API. The JWT uses registered claims (`exp`, `iat`, `iss`, `jti`, `sub` and `aud`) and implements a private claim `my:alw` which will allow fine grain regarding which actions the users can perform.

The first service, `issuer`, is the responsable to issue JWT tokens when a POST request with a valid user name is performed to `/auth/`.

The second service is `calc`, it provides two actions `sum` and `mul`. `sum` is available for all users with access to this service, on the other hand `mul` is only available to those users with explicit access in the `my:alw` claim.

### Valid users
- `user1` can access `calc`.
- `user2` can not access `calc`.
- `user3` can access `calc` and it's allowed to perform, explicitly, `non-existing` action.
- `user4` can access `calc` and it's allowed to perform, explicitly, `mul` action.
This will bring up both services, `issuer` will be listening on 8080 and `calc` on 8081. Leave the terminal open and the running.

### Cases

After spinning up the services just play with them with cURL. Just replace the `user` parameter on the first command to get a new token associated to a new user.

```
$ export TOKEN=$(curl --data "user=user4" http://127.0.0.1:8080/auth/)
$ curl -H "Authorization: Bearer $TOKEN" -F "num1=2" -F "num2=2" http://127.0.0.1:8081/sum/
$ curl -H "Authorization: Bearer $TOKEN" -F "num1=2" -F "num2=2" http://127.0.0.1:8081/mul/
```

## Proxied
Proxied examples adds more complexity to the `simple` example. It moves `calc` service to a backend network and a new service `proxy` will proxy all requests to. In this example the users access control changes for the issuer, users now are related to profiles, inthe issuer, and profiles are mapped to actions in the proxy.

### Valid users
- `user1` is an accountant with access to `mul` and `sum`.
- `user2` is an accountant without access to `mul` but `sum`.
- `user3` is a nutritionist and it does not have access to `calc`.

### Cases

It works exactly in the same way it does on Simple. Please have a look to it.

