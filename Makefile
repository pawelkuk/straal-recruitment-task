.PHONY: black test isort format
test:
		pytest --capture=no -vv --reuse-db
black:
		black .
isort:
		isort .
format: isort black
	echo Ready to commit!