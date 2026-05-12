.PHONY: install test run api clean

install:
	python3 -m venv .venv
	.venv/bin/pip install -e ".[dev]"

test:
	.venv/bin/python -m pytest

run:
	.venv/bin/python -m app.cli

api:
	.venv/bin/uvicorn app.main:app --reload

clean:
	rm -rf .pytest_cache .ruff_cache startup_city_data_pipeline.egg-info
