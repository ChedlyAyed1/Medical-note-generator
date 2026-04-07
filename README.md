# Medical Note Generator

Personal monorepo to build a clean medical note generation pipeline with:

- `Django + Django REST Framework` for the API, domain logic, and persistence
- `WhisperX` running on `CPU` in a dedicated FastAPI service
- `Groq` for note generation from transcripts

## Architecture

```text
audio upload -> Django job creation -> WhisperX transcription service -> transcript persistence -> Groq note generation
```

## Why this structure

- Keep heavy speech-to-text dependencies outside the main Django app
- Keep business logic out of views and serializers
- Use small, named modules instead of catch-all files
- Make the repo readable enough to use as a portfolio project

## First commands

```powershell
Copy-Item .env.example .env
pip install -e ./django_app
pip install -e ./whisperx_service
```

## Immediate next milestones

1. Create migrations and wire PostgreSQL if you want production parity early.
2. Add background job execution once the synchronous happy path works.
3. Add prompt versioning and note validation rules specific to your medical workflow.
