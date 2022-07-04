.PHONY: devinstall
devinstall:
	pip install --upgrade --upgrade-strategy eager -r requirements-dev.txt

.PHONY: install
install:
	pip install --upgrade --upgrade-strategy eager -r requirements.txt

.PHONY: flaketest
flaketest:
	flake8
