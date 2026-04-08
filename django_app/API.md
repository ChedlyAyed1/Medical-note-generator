# Django API

This document describes the Django API exposed by `django_app`.

The Django service is responsible for:

- accepting audio uploads
- creating and tracking transcription jobs
- calling `whisperx_service` for speech-to-text
- storing transcript segments
- calling Groq to generate clinical notes

## Base URLs

- Local API root: `http://127.0.0.1:8000/api/notes/`
- Swagger UI: `http://127.0.0.1:8000/api/docs/`
- OpenAPI schema: `http://127.0.0.1:8000/api/schema/`
- ReDoc: `http://127.0.0.1:8000/api/redoc/`
- Healthcheck: `http://127.0.0.1:8000/health/`

## End-to-End Flow

The current synchronous flow is:

1. Upload an audio file with `POST /api/notes/uploads/`
2. Start transcription with `POST /api/notes/jobs/{job_id}/transcribe/`
3. Generate a note with `POST /api/notes/jobs/{job_id}/generate-note/`
4. Read the final resources with:
   `GET /api/notes/jobs/{job_id}/`
   `GET /api/notes/{note_id}/`

## Endpoints

### `POST /api/notes/uploads/`

Creates an `AudioRecording` and a `TranscriptionJob`.

Request:

- `file`: audio file, required
- `language`: optional, defaults to `en`
- `patient_reference`: optional string
- `encounter_reference`: optional string

Response:

- `201 Created`
- returns a `TranscriptionJob` payload with status `pending`

Example response:

```json
{
  "id": "job-uuid",
  "status": "pending",
  "language": "en",
  "error_message": "",
  "created_at": "2026-04-08T11:25:05.240533Z",
  "updated_at": "2026-04-08T11:25:05.240578Z",
  "started_at": null,
  "finished_at": null,
  "audio_recording": {
    "id": "audio-uuid",
    "original_filename": "visit.wav",
    "patient_reference": "PAT-001",
    "encounter_reference": "ENC-001",
    "file": "/media/audio/2026/04/08/visit.wav"
  },
  "segments": [],
  "clinical_note": null
}
```

Possible errors:

- `400 Bad Request` if the payload is invalid

### `GET /api/notes/jobs/{job_id}/`

Returns the current state of a transcription job.

Response:

- `200 OK`
- returns the full `TranscriptionJob` resource, including:
  - job metadata
  - transcript segments
  - note preview if a note already exists

### `POST /api/notes/jobs/{job_id}/transcribe/`

Runs WhisperX transcription for an existing job.

Request:

- no request body
- `job_id` is passed in the URL

Response:

- `200 OK` if transcription succeeds
- returns the updated `TranscriptionJob`

After success, the job usually contains:

- `status = "completed"`
- populated `segments`
- `started_at` and `finished_at`

Possible errors:

- `400 Bad Request` if the job is not in a valid state
- `400 Bad Request` if the WhisperX call fails or times out

Notes:

- this endpoint is currently synchronous
- long audio files may require a larger `WHISPERX_TIMEOUT_SECONDS` value in Django

### `POST /api/notes/jobs/{job_id}/generate-note/`

Generates a clinical note from a completed transcript.

Request:

- no request body
- `job_id` is passed in the URL

Response:

- `201 Created`
- returns a `ClinicalNote`

Example response:

```json
{
  "id": "note-uuid",
  "job": "job-uuid",
  "note_type": "soap",
  "model_name": "openai/gpt-oss-120b",
  "prompt_version": "soap_note_v1",
  "content": "Generated note text",
  "structured_content": {
    "source": "groq"
  },
  "generated_at": "2026-04-08T12:22:42.337743Z"
}
```

Possible errors:

- `400 Bad Request` if the transcript is not completed
- `400 Bad Request` if the transcript text is empty
- `400 Bad Request` if the Groq call fails

### `GET /api/notes/{note_id}/`

Returns a previously generated clinical note.

Response:

- `200 OK`
- returns the `ClinicalNote` resource

## Main Response Shapes

### `TranscriptionJob`

- `id`
- `status`
- `language`
- `error_message`
- `created_at`
- `updated_at`
- `started_at`
- `finished_at`
- `audio_recording`
- `segments`
- `clinical_note`

### `TranscriptSegment`

- `id`
- `segment_index`
- `start`
- `end`
- `speaker`
- `text`
- `metadata`

### `ClinicalNote`

- `id`
- `job`
- `note_type`
- `model_name`
- `prompt_version`
- `content`
- `structured_content`
- `generated_at`

## Current Notes

- `language` defaults to `en` if omitted on upload
- speaker labels returned from WhisperX are normalized as `spk1`, `spk2`, and so on
- the Django app talks to `whisperx_service` over HTTP using `WHISPERX_BASE_URL`
- the current implementation is synchronous, so long transcription requests can take several minutes
- the next architectural step would be background jobs for transcription and note generation
