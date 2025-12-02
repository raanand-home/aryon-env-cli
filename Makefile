.PHONY: publish
publish:
	export CODEARTIFACT_AUTH_TOKEN=$$(aws codeartifact get-authorization-token --domain aryon --domain-owner 027574771246 --query authorizationToken --output text);  pdm publish