.PHONY: install generate test run docker-build

install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements-dev.txt

generate:
	. .venv/bin/activate && python -m scripts.generate_corpus

test:
	. .venv/bin/activate && python -m pytest -q

run:
	. .venv/bin/activate && python -m uvicorn flash_dental_copilot.api:application --reload --port 8080

docker-build:
	docker build -t flash-dental-copilot .
