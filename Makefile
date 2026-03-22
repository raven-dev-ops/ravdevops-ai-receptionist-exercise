.PHONY: run test check docker

run:
	uvicorn app.main:app --reload

test:
	pytest -q

check:
	python scripts/review_check.py

docker:
	docker compose up --build
