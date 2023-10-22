# Bright ID Gas Faucet

BrightID users can claim free gas tokens on supported chains.

## Quick start

create a `.env` file and add the following

```bash
POSTGRES_DB="unitap"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="postgres"
FIELD_KEY="rnPAm1QKx8hepMhqV0IKJxB9tdR_hhU4-0EVTGVXQg0="
SECRET_KEY="django-insecure-!=_mi0j#rhk7c9p-0wg-3me6y&fk$+fahz6fh)k1n#&@s(9vf5"
BRIGHT_PRIVATE_KEY=""
DEBUG="True"
SENTRY_DSN="DEBUG-DSN"
```

_read more about `DATABASE_URL` in the [dj-database-url](https://github.com/kennethreitz/dj-database-url#url-schema) docs_

### Setup pre-commit
pre-commit works with python3.10.

create a new virtualenv and activate it:

```shell
python -m virtualenv .venv
source .venv/bin/activate
```

install pre-commit:

```shell
make setup-pre-commit
```

### Using Docker Compose

you might need "sudo" privilege to run the following.

run the following command from projects root directory to build a docker image from this repo and run it:

```shell
make docker-up-dev
```

#### create a superuser:

find unitap-backend image container ID:

```shell
docker ps | grep unitap-backend
```

sample output:

```
61a36aae8213   unitap-backend         "/bin/sh -c ./start.…"   6 minutes ago    Up About a minute   0.0.0.0:5678->5678/tcp   brightidfaucet-backend-1
```

**_61a36aae8213_** is the container id. Open a shell inside this container:

```shell
docker exec -it 61a36aae8213 /bin/bash
```

create a superuser:

```shell
python manage.py createsuperuser
```

you can exit the terminal now. You should now be able to visit the site on `http://127.0.0.1:5678/admin/` and use the superuser credentials to login.

### Using Local Virtual Environment

create a new virtualenv and activate it:

```shell
python -m virtualenv .venv
source .venv/bin/activate
```

install requirements:

```shell
pip install -r requirements/base.txt
```

run migrations:

```shell
mkdir db # make sure db folder exists
python manage.py migrate
```

run server:

```shell
python manage.py runserver
```

### running tests

You need [ganache](https://www.npmjs.com/package/ganache-cli) or any web3 rpc compatible test chain to run the tests.

edit `faucet/test.py` and set the following according to your local test chain:

```python
test_rpc_url = "http://127.0.0.1:7545"
test_chain_id = 1337
test_wallet_key = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d" # must hold some native tokens
```

run tests:

```shell
ganache-cli -d -p 7545
python manage.py test
```
