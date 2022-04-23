# Bright ID Gas Faucet

BrightID users can claim free gas tokens on supported chains.

## Quick start

### Using Docker

run the following command from projects root directory to build a docker image:
```shell
$ docker build . -t bright_faucet:latest
```

start the container:
```shell
$ docker run -d -p [PORT]:5678 -v [DB-FOLDER]:/code/db/ bright_faucet:latest
5eb97c398fdf6d28d3e9644ff762e7cb2dfbe716e6d2e8f1f6f43506533e8fdf
```
- [PORT]: the port that you want to be able to access the container from, example: 8080
- [DB-FOLDER]: a location to hold database files
- the output of the command is the container id

open up a shell terminal inside the container:
```shell
$ docker exec -it [cointainer_id] /bin/bash
```

inside the terminal, first run the migrations:
```shell
$ python manage.py migrate
```

create a superuser:
```shell
$ python manage.py createsuperuser
```

you can exit the terminal now. You should now be able to visit the site on ```http://127.0.0.1:[PORT]```