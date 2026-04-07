install-django:
	pip install -e ./django_app

install-whisperx:
	pip install -e ./whisperx_service

lint:
	ruff check .

format:
	ruff format .

test:
	pytest django_app/apps/notes/tests whisperx_service/app/tests

run-django:
	cd django_app && python manage.py runserver 0.0.0.0:8000

run-whisperx:
	cd whisperx_service && uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
