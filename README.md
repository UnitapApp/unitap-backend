# Bright ID Gas Faucet

BrightID users can claim free gas tokens on supported chains.

## Quick start

create a `private.py` file inside `brightIDfaucet` directory and add the following

```python
FIELD_KEY = "rnPAm1QKx8hepMhqV0IKJxB9tdR_hhU4-0EVTGVXQg0="
SECRET_KEY = 'django-insecure-!=_mi0j#rhk7c9p-0wg-3me6y&fk$+fahz6fh)k1n#&@s(9vf5'
DEBUG = False
USE_MOCK = False # only set True for running tests 
```

### Using Docker

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


### Using Local Virtual Environment
create a new virtualenv and activate it:
```shell
$ python3.8 -m virtualenv .venv
$ source .venv/bin/activate
```
install requirements:
```shell
$ pip install -r requirements.txt
```
run migrations:
```shell
$ python manage.py migrate
```

run server:
```shell
$ python manage.py runserver
```

### running tests

You need [ganache](https://www.npmjs.com/package/ganache-cli) or any web3 rpc compatible test chain to run the tests.

edit ```faucet/test.py``` and set the following according to your local test chain:
```python
test_rpc_url = "http://127.0.0.1:7545"
test_chain_id = 1337
test_wallet_key = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d" # must hold some native tokens
```

run tests:
```shell
$ python manage.py test
```