.PHONY: publish
publish:
	python update_version.py
	rm -rf dist
	pdm build
	aws codeartifact login --tool twine --domain aryon --domain-owner 027574771246 --repository private
	export TWINE_USERNAME=aws
	export TWINE_PASSWORD=$$(aws codeartifact get-authorization-token --domain aryon --domain-owner 027574771246 --query authorizationToken --output text)
	export TWINE_REPOSITORY_URL=https://aryon-027574771246.d.codeartifact.eu-central-1.amazonaws.com/pypi/private/simple/
	twine upload --verbose --repository codeartifact dist/env_cli-*.tar.gz