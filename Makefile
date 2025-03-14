start:
	uvicorn intern_engine.main:app --reload

lint:
	uv run flake8