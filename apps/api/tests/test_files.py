import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.model.file import File


@pytest.mark.asyncio
async def test_upload_csv_file(client, mock_db, mock_user):
    mock_db.commit = AsyncMock()

    async def fake_refresh(obj):
        obj.id = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
        obj.user_id = mock_user.id
        obj.conversation_id = None
        obj.name = "test.csv"
        obj.mime = "text/csv"
        obj.size_bytes = 100
        obj.kind = "data"
        obj.status = "ready"
        obj.profile_json = {"n_rows": 3, "n_cols": 2}
        obj.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)

    mock_db.refresh = AsyncMock(side_effect=fake_refresh)

    csv_content = b"name,age\nAlice,30\nBob,25\nCharlie,35"

    with (
        patch("app.router.files.save_upload_file", new_callable=AsyncMock) as mock_save,
        patch("app.router.files.auto_profile") as mock_profile,
        patch("app.router.files.get_full_path") as mock_path,
    ):
        mock_save.return_value = ("user123/file.csv", 100)
        mock_profile.return_value = {"n_rows": 3, "n_cols": 2}
        mock_path.return_value = "/tmp/test.csv"

        response = await client.post(
            "/api/v1/files/",
            files={"file": ("test.csv", csv_content, "text/csv")},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "test.csv"
    assert data["mime"] == "text/csv"
    assert data["status"] == "ready"
    assert data["profile_json"] == {"n_rows": 3, "n_cols": 2}


@pytest.mark.asyncio
async def test_list_files(client, mock_db, mock_user):
    file1 = MagicMock(spec=File)
    file1.id = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    file1.user_id = mock_user.id
    file1.conversation_id = None
    file1.name = "data.csv"
    file1.mime = "text/csv"
    file1.size_bytes = 500
    file1.kind = "data"
    file1.status = "ready"
    file1.profile_json = None
    file1.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [file1]
    mock_db.execute = AsyncMock(return_value=mock_result)

    response = await client.get("/api/v1/files/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "data.csv"


@pytest.mark.asyncio
async def test_delete_file(client, mock_db, mock_user):
    file_id = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
    file_record = MagicMock(spec=File)
    file_record.id = file_id
    file_record.user_id = mock_user.id
    file_record.storage_path = "user123/file.csv"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = file_record
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.delete = AsyncMock()
    mock_db.commit = AsyncMock()

    with patch("app.router.files.delete_file_storage") as mock_delete:
        response = await client.delete(f"/api/v1/files/{file_id}")

    assert response.status_code == 204
    mock_delete.assert_called_once()


@pytest.mark.asyncio
async def test_upload_invalid_mime(client, mock_db, mock_user):
    response = await client.post(
        "/api/v1/files/",
        files={"file": ("test.txt", b"hello world", "text/plain")},
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]
