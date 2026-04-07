from django.core.files.uploadedfile import SimpleUploadedFile


def build_audio_file(name: str = "visit.wav", content: bytes = b"fake-audio") -> SimpleUploadedFile:
    return SimpleUploadedFile(name=name, content=content, content_type="audio/wav")
