# Bright ID Gas Faucet

BrightID users can claim free gas tokens on supported chains.

## Quick start

### Using Docker

create a `private.py` file inside `brightIDFaucet` directory and add the following

```python
FIELD_KEY = "rnPAm1QKx8hepMhqV0IKJxB9tdR_hhU4-0EVTGVXQg0="
SECRET_KEY = 'django-insecure-!=_mi0j#rhk7c9p-0wg-3me6y&fk$+fahz6fh)k1n#&@s(9vf5'
DEBUG = False
USE_MOCK = False

```

**note: leave the DEBUG field blank for production**

#

you might need "sudo" privilege to run the following.

run the following command from projects root directory to build a docker image:

```shell
$ docker build . -t bright_faucet:latest
```

start the container:

```shell
$ docker run -d -p [PORT]:5678 -v [DB-FOLDER]:/code/db/ -v [STATIC-FOLDER]:/code/static/ bright_faucet:latest
5eb97c398fdf6d28d3e9644ff762e7cb2dfbe716e6d2e8f1f6f43506533e8fdf
```

- [PORT]: the port that you want to be able to access the container from, example: 8080
- [DB-FOLDER]: a location to hold database files
- [STATIC-FOLDER]: a location to hold static files
- the output of the command is the container id

open up a shell terminal inside the container:

```shell
$ docker exec -it [container_id] /bin/bash
```

inside the terminal, first run the migrations:

```shell
$ python manage.py migrate
```

collect static files:
```shell
$ python manage.py collectstatic
```

create a superuser:

```shell
$ python manage.py createsuperuser
```

you can exit the terminal now. You should now be able to visit the site on `http://127.0.0.1:[PORT]`
