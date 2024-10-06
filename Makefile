CODE_DIRECTORIES = magic

lint:
	@poetry run ruff check --fix $(CODE_DIRECTORIES)

format:
	@poetry run ruff format $(CODE_DIRECTORIES)

test:
	@poetry run pytest

run:
	@poetry run python -m magic.app