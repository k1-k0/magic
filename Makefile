CODE_DIRECTORIES = magic tests


ecc:
	@ls magic

lint:
	@poetry run ruff check $(CODE_DIRECTORIES)

format:
	@poetry run ruff format $(CODE_DIRECTORIES)

test:
	@poetry run pytest