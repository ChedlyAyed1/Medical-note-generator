# WhisperX Service

## Purpose

`whisperx_service` is a dedicated FastAPI microservice for CPU-based speech transcription.

It is responsible for:

- receiving an uploaded audio file
- transcribing the audio with WhisperX
- aligning timestamps
- optionally running speaker diarization
- returning a normalized JSON response

It is not responsible for:

- storing jobs in the database
- generating medical notes
- calling Groq

Those concerns belong to the Django service.

## Runtime

- Framework: FastAPI
- Server: Uvicorn
- Speech engine: WhisperX
- Device target: CPU
- Default language: `en`

## Endpoints

### `GET /health`

Simple healthcheck endpoint.

**Purpose**

- confirm that the service is reachable
- useful for manual checks, Docker healthchecks, and uptime monitoring

**Response**

```json
{
  "status": "ok"
}
```

**Status codes**

- `200 OK`: service is up

### `POST /api/v1/transcriptions`

Runs a transcription on an uploaded audio file.

**Content-Type**

`multipart/form-data`

**Form fields**

- `file`: required audio file
- `language`: optional language code, defaults to `en`

**Supported audio examples**

- `.wav`
- `.mp3`
- `.m4a`
- `.mp4`
- `.aac`
- `.flac`
- `.ogg`

**Example request**

```bash
curl -X POST "http://127.0.0.1:8001/api/v1/transcriptions" \
  -F "file=@sample.wav" \
  -F "language=en"
```

**Successful response**

```json
{
  "text": "Hello! How can I help you today?",
  "language": "en",
  "segments": [
    {
      "start": 1.938,
      "end": 2.298,
      "text": "Hello!",
      "speaker": "spk1"
    },
    {
      "start": 2.798,
      "end": 9.022,
      "text": "How can I help you today?",
      "speaker": "spk1"
    }
  ]
}
```

**Response fields**

- `text`: full transcript text
- `language`: detected or enforced language code
- `segments`: ordered transcript chunks

**Segment fields**

- `start`: segment start time in seconds
- `end`: segment end time in seconds
- `text`: text content for the segment
- `speaker`: normalized speaker label such as `spk1`, `spk2`

## Speaker Labels

When diarization is enabled, WhisperX may return speaker IDs in an internal format.
The service normalizes them to a simpler public format:

- first detected speaker becomes `spk1`
- second detected speaker becomes `spk2`
- and so on

If diarization is disabled, `speaker` will usually be an empty string.

## Environment Variables

The service reads environment variables from:

- the repo root `.env`
- the local `whisperx_service/.env` if present

### Core transcription

- `WHISPERX_MODEL_NAME`
  Default: `base`
- `WHISPERX_DEVICE`
  Default: `cpu`
- `WHISPERX_COMPUTE_TYPE`
  Default: `int8`
- `WHISPERX_BATCH_SIZE`
  Default: `4`
- `WHISPERX_ALIGN_OUTPUT`
  Default: `true`

### Diarization

- `WHISPERX_ENABLE_DIARIZATION`
  Default: `false`
- `WHISPERX_HF_TOKEN`
  Required when diarization is enabled
- `WHISPERX_MIN_SPEAKERS`
  Optional lower bound for speaker count
- `WHISPERX_MAX_SPEAKERS`
  Optional upper bound for speaker count

## Processing Flow

For `POST /api/v1/transcriptions`, the service does the following:

1. Receives the uploaded file.
2. Saves it to a temporary file.
3. Loads the WhisperX model on CPU.
4. Runs transcription.
5. Aligns segments when alignment is enabled.
6. Runs diarization when diarization is enabled.
7. Normalizes speaker labels to `spk1`, `spk2`, etc.
8. Rebuilds the full `text` field if WhisperX leaves it empty.
9. Deletes the temporary file.
10. Returns the JSON response.

## Possible Errors

### `400 Bad Request`

Common causes:

- missing `file` field
- invalid multipart payload
- request malformed by the client

### `500 Internal Server Error`

Common causes:

- WhisperX model loading failure
- `ffmpeg` missing from the runtime
- diarization enabled without `WHISPERX_HF_TOKEN`
- Hugging Face access not granted for the diarization model
- unsupported or corrupted audio file
- Python dependency mismatch inside the environment

### Diarization-specific pitfalls

If `speaker` stays empty or diarization fails, check:

- `WHISPERX_ENABLE_DIARIZATION=true`
- `WHISPERX_HF_TOKEN` is present
- the service was restarted after editing `.env`
- the Hugging Face account accepted access to the diarization model used by WhisperX

## Manual Testing

### Swagger UI

FastAPI exposes interactive docs at:

- `http://127.0.0.1:8001/docs`
- `http://127.0.0.1:8001/redoc`

### Healthcheck

```bash
curl http://127.0.0.1:8001/health
```

### Transcription

```bash
curl -X POST "http://127.0.0.1:8001/api/v1/transcriptions" \
  -F "file=@sample.wav"
```

## Notes

- This service is synchronous for now.
- CPU transcription is slower than GPU transcription, especially on the first request.
- The first transcription call may take longer because model loading happens lazily.
