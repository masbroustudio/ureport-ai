import os
import uuid

from fastapi import UploadFile

from app.settings import Settings


async def save_upload_file(
    file: UploadFile, user_id: uuid.UUID, settings: Settings,
    max_size_bytes: int | None = None,
) -> tuple[str, int]:
    """Save uploaded file to local storage.

    Returns (relative_storage_path, size_bytes).
    Raises ValueError if file exceeds max_size_bytes during write.
    """
    user_dir = os.path.join(settings.FILE_STORAGE_PATH, str(user_id))
    os.makedirs(user_dir, exist_ok=True)

    file_id = uuid.uuid4()
    safe_name = file.filename or "upload"
    # Sanitize filename: strip path separators, traversal sequences, and null bytes
    safe_name = (
        safe_name.replace("/", "")
        .replace("\\", "")
        .replace("..", "")
        .replace("\0", "")
    )
    if not safe_name:
        safe_name = "upload"
    storage_name = f"{file_id}_{safe_name}"
    storage_path = os.path.join(str(user_id), storage_name)
    full_path = os.path.join(settings.FILE_STORAGE_PATH, storage_path)

    size = 0
    try:
        with open(full_path, "wb") as f:
            while chunk := await file.read(8192):
                size += len(chunk)
                if max_size_bytes and size > max_size_bytes:
                    f.close()
                    os.remove(full_path)
                    raise ValueError(
                        f"File exceeds maximum allowed size of {max_size_bytes} bytes"
                    )
                f.write(chunk)
    except ValueError:
        raise
    except Exception:
        # Clean up partially written file on unexpected error
        if os.path.exists(full_path):
            os.remove(full_path)
        raise

    return storage_path, size


def delete_file_storage(storage_path: str, settings: Settings) -> None:
    """Remove file from local storage."""
    full_path = os.path.join(settings.FILE_STORAGE_PATH, storage_path)
    if os.path.exists(full_path):
        os.remove(full_path)


def get_full_path(storage_path: str, settings: Settings) -> str:
    """Get absolute path for a stored file."""
    return os.path.join(settings.FILE_STORAGE_PATH, storage_path)
