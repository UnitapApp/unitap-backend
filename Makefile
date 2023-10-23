.PHONY: local-setup install-pre-commit install-local-reqs docker-build-dev docker-up-dev


install-local-reqs:
	pip install -r requirements/local.txt

install-pre-commit:
	pre-commit uninstall; pre-commit install

setup-pre-commit:
	$(MAKE) install-local-reqs
	$(MAKE) install-pre-commit;

docker-build-dev:
	docker-compose -f docker-compose.yml build

docker-up-dev:
	docker-compose up -d --force-recreate --build

docker-down-dev:
	docker-compose down
