SHELL := /bin/bash

bump:
	poetry version prerelease

build:
	rm -rf dist
	poetry build

install:
	-pipx uninstall "$(shell poetry version | awk '{print $$1}')"
	pipx install --force "$(shell ls -d dist/*.whl)"

publish:
	poetry publish

clean:
	rm -rf venv
	rm -rf imports cdktf.out

init:
	terraform init

upgrade:
	terraform init -upgrade

validate:
	terraform validate

plan:
	terraform plan -out=.plan

apply:
	terraform apply .plan
	rm -f .plan

refresh:
	terraform refresh

console:
	terraform console

apply-refresh:
	terraform apply -refresh-only

get:
	poetry run cdktf get
	amanibhavam/cdk/__init__.py
	amanibhavam/cdk/aws/__init__.py
	git add */cdk
	-pre-commit
	git add */cdk
	pre-commit

synth:
	poetry run amanibhavam
	git add -f cdktf.out/stacks/default/cdk.tf.json
	-pre-commit
	git add -f cdktf.out/stacks/default/cdk.tf.json
	pre-commit
