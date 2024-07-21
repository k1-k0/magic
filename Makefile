CODE_DIRECTORIES = magic tests

lint:
	@poetry run ruff check $(CODE_DIRECTORIES)

format:
	@poetry run ruff format $(CODE_DIRECTORIES)

test:
	@poetry run pytest

run:
	@poetry run python -m magic.app