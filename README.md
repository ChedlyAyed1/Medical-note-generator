# Medical Note Generator

Personal monorepo for a medical note generation pipeline built with Django, WhisperX, and Groq.

- `django_app` handles the API, orchestration, and persistence
- `whisperx_service` handles CPU transcription and diarization
- `Groq` is used for clinical note generation

## Architecture

```text
audio upload -> Django job creation -> WhisperX transcription service -> transcript persistence -> Groq note generation
```

## Project Goal

The goal of this project is to turn raw clinical audio into structured medical notes through a clean service-oriented architecture.

The current workflow is:

1. Upload audio through Django
2. Send the audio to WhisperX for transcription
3. Store transcript segments and speaker labels
4. Generate a clinical note from the transcript with Groq

## Why this structure

- Keep heavy speech-to-text dependencies outside the main Django app
- Keep business logic out of views and serializers
- Use small, named modules instead of catch-all files

## External Dependencies

- WhisperX powers the speech-to-text pipeline used by `whisperx_service`
  Repository: https://github.com/m-bain/whisperX
- Groq provides the chat-completions API used for note generation
  Platform: https://groq.com/

This repository does not vendor or fork WhisperX. It integrates WhisperX as an external dependency and wraps it inside a dedicated service boundary.

## Prerequisites

- Windows + WSL Ubuntu for local development
- `uv`
- Python `3.12`
- `ffmpeg`

## First commands

```bash
cp .env.example .env
cd django_app && uv sync
cd ../whisperx_service && uv sync
```

## Local Run

Run Django:

```bash
cd django_app
uv run python manage.py migrate
uv run python manage.py runserver
```

Run WhisperX:

```bash
cd whisperx_service
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Useful local URLs:

- Django healthcheck: `http://127.0.0.1:8000/health/`
- Django API docs: `http://127.0.0.1:8000/api/docs/`
- WhisperX healthcheck: `http://127.0.0.1:8001/health`
- WhisperX docs: `http://127.0.0.1:8001/docs`

## Current Status

- WhisperX CPU transcription is working
- Speaker diarization is working with normalized labels such as `spk1` and `spk2`
- Django upload and transcription job flow is in place
- Groq integration is in place
- Background jobs and production hardening are still pending

## Immediate next milestones

1. Create migrations and wire PostgreSQL if you want production parity early.
2. Add asynchronous workers for heavy tasks such as transcription, diarization, and note generation.
3. Evaluate Celery with Redis or RabbitMQ once the synchronous flow is stable.
4. Add prompt versioning and note validation rules specific to your medical workflow.
