import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import boto3
import dropbox
import mega
from azure.storage.blob import BlobServiceClient
from google.cloud import storage


class CloudStorageConfig:
    def __init__(
        self,
        provider: str,
        credentials: Dict[str, Any],
        bucket_name: str,
        region: Optional[str] = None,
    ):
        self.provider = provider
        self.credentials = credentials
        self.bucket_name = bucket_name
        self.region = region


class CloudStorageManager:
    def __init__(self, config: CloudStorageConfig):
        self.config = config
        self.logger = logging.getLogger("cloud_storage")
        self._init_client()
        self._executor = ThreadPoolExecutor(max_workers=4)

    def _init_client(self):
        """Initialisiert den Cloud-Storage-Client basierend auf dem Provider"""
        if self.config.provider == "aws":
            self.client = boto3.client(
                "s3",
                aws_access_key_id=self.config.credentials["access_key"],
                aws_secret_access_key=self.config.credentials["secret_key"],
                region_name=self.config.region,
            )
        elif self.config.provider == "gcp":
            self.client = storage.Client.from_service_account_json(
                self.config.credentials["service_account_file"]
            )
            self.bucket = self.client.bucket(self.config.bucket_name)
        elif self.config.provider == "azure":
            self.client = BlobServiceClient.from_connection_string(
                self.config.credentials["connection_string"]
            )
            self.container = self.client.get_container_client(self.config.bucket_name)
        elif self.config.provider == "dropbox":
            self.client = dropbox.Dropbox(self.config.credentials["access_token"])
        elif self.config.provider == "mega":
            self.client = mega.Mega()
            self.client.login(
                self.config.credentials["email"], self.config.credentials["password"]
            )
        else:
            raise ValueError(f"Unsupported cloud provider: {self.config.provider}")

    async def upload_file(
        self,
        local_path: Union[str, Path],
        remote_path: str,
        chunk_size: int = 8 * 1024 * 1024,  # 8MB
        retry_count: int = 3,
    ) -> bool:
        """
        Lädt eine Datei in den Cloud-Speicher hoch mit optimierter Provider-Strategie.

        Args:
            local_path: Lokaler Pfad der Datei
            remote_path: Pfad im Cloud-Speicher
            chunk_size: Größe der Chunks für Chunked Upload
            retry_count: Anzahl der Wiederholungsversuche

        Returns:
            bool: True wenn erfolgreich, False sonst
        """
        try:
            # Phase 1: Validierung und Vorbereitung
            upload_context = await self._prepare_upload(
                local_path, remote_path, chunk_size
            )

            # Phase 2: Provider-spezifischer Upload
            success = await self._execute_provider_upload(upload_context, retry_count)

            # Phase 3: Post-Upload-Validierung
            if success:
                await self._validate_upload_success(upload_context)

            return success

        except Exception as e:
            self.logger.error(f"Upload error for {local_path}: {str(e)}")
            return False

    async def _prepare_upload(
        self, local_path: Union[str, Path], remote_path: str, chunk_size: int
    ) -> Dict[str, Any]:
        """Bereitet Upload vor und validiert Parameter."""
        local_path = Path(local_path)

        if not local_path.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")

        file_size = local_path.stat().st_size

        return {
            "local_path": local_path,
            "remote_path": remote_path,
            "file_size": file_size,
            "chunk_size": chunk_size,
            "requires_multipart": file_size > chunk_size,
            "upload_id": None,
        }

    async def _execute_provider_upload(
        self, context: Dict[str, Any], retry_count: int
    ) -> bool:
        """Führt provider-spezifischen Upload aus."""
        provider = self.config.provider

        for attempt in range(retry_count):
            try:
                if provider == "aws":
                    return await self._upload_to_s3(context)
                elif provider == "gcp":
                    return await self._upload_to_gcs(context)
                elif provider == "azure":
                    return await self._upload_to_azure(context)
                elif provider == "dropbox":
                    return await self._upload_to_dropbox(context)
                elif provider == "mega":
                    return await self._upload_to_mega(context)
                else:
                    raise ValueError(f"Unsupported provider: {provider}")

            except Exception as e:
                self.logger.warning(f"Upload attempt {attempt + 1} failed: {str(e)}")
                if attempt == retry_count - 1:
                    raise
                await asyncio.sleep(2**attempt)  # Exponential backoff

        return False

    async def _upload_to_s3(self, context: Dict[str, Any]) -> bool:
        """Führt S3-spezifischen Upload aus."""
        if context["requires_multipart"]:
            return await self._s3_multipart_upload(context)
        else:
            return await self._s3_simple_upload(context)

    async def _s3_simple_upload(self, context: Dict[str, Any]) -> bool:
        """Einfacher S3-Upload für kleine Dateien."""
        try:
            self.client.upload_file(
                str(context["local_path"]),
                self.config.bucket_name,
                context["remote_path"],
            )
            self.logger.info(f"S3 simple upload successful: {context['remote_path']}")
            return True
        except Exception as e:
            self.logger.error(f"S3 simple upload failed: {str(e)}")
            raise

    async def _s3_multipart_upload(self, context: Dict[str, Any]) -> bool:
        """Multipart S3-Upload für große Dateien."""
        upload_id = None
        try:
            # Initiiere Multipart Upload
            response = self.client.create_multipart_upload(
                Bucket=self.config.bucket_name, Key=context["remote_path"]
            )
            upload_id = response["UploadId"]
            context["upload_id"] = upload_id

            # Upload Parts
            parts = await self._upload_s3_parts(context)

            # Complete Upload
            self.client.complete_multipart_upload(
                Bucket=self.config.bucket_name,
                Key=context["remote_path"],
                UploadId=upload_id,
                MultipartUpload={"Parts": parts},
            )

            self.logger.info(
                f"S3 multipart upload successful: {context['remote_path']}"
            )
            return True

        except Exception:
            # Cleanup bei Fehler
            await self._cleanup_failed_s3_upload(context, upload_id)
            raise

    async def _upload_s3_parts(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Uploaded Teile einer S3 Multipart-Upload."""
        parts = []

        with open(context["local_path"], "rb") as f:
            for part_number, chunk in enumerate(
                iter(lambda: f.read(context["chunk_size"]), b""), 1
            ):
                response = self.client.upload_part(
                    Bucket=self.config.bucket_name,
                    Key=context["remote_path"],
                    PartNumber=part_number,
                    UploadId=context["upload_id"],
                    Body=chunk,
                )
                parts.append({"PartNumber": part_number, "ETag": response["ETag"]})

        return parts

    async def _cleanup_failed_s3_upload(
        self, context: Dict[str, Any], upload_id: Optional[str]
    ) -> None:
        """Bereinigt fehlgeschlagenen S3-Upload."""
        if upload_id:
            try:
                self.client.abort_multipart_upload(
                    Bucket=self.config.bucket_name,
                    Key=context["remote_path"],
                    UploadId=upload_id,
                )
                self.logger.info(f"Aborted multipart upload: {upload_id}")
            except Exception as abort_error:
                self.logger.error(
                    f"Error aborting multipart upload: {str(abort_error)}"
                )

    async def _upload_to_gcs(self, context: Dict[str, Any]) -> bool:
        """Führt GCS-Upload aus."""
        try:
            blob = self.bucket.blob(context["remote_path"])
            blob.upload_from_filename(str(context["local_path"]))
            self.logger.info(f"GCS upload successful: {context['remote_path']}")
            return True
        except Exception as e:
            self.logger.error(f"GCS upload failed: {str(e)}")
            raise

    async def _upload_to_azure(self, context: Dict[str, Any]) -> bool:
        """Führt Azure-Upload aus."""
        try:
            with open(context["local_path"], "rb") as f:
                self.container.upload_blob(
                    name=context["remote_path"], data=f, overwrite=True
                )
            self.logger.info(f"Azure upload successful: {context['remote_path']}")
            return True
        except Exception as e:
            self.logger.error(f"Azure upload failed: {str(e)}")
            raise

    async def _upload_to_dropbox(self, context: Dict[str, Any]) -> bool:
        """Führt Dropbox-Upload aus."""
        try:
            with open(context["local_path"], "rb") as f:
                self.client.files_upload(
                    f.read(),
                    context["remote_path"],
                    mode=dropbox.files.WriteMode.overwrite,
                )
            self.logger.info(f"Dropbox upload successful: {context['remote_path']}")
            return True
        except Exception as e:
            self.logger.error(f"Dropbox upload failed: {str(e)}")
            raise

    async def _upload_to_mega(self, context: Dict[str, Any]) -> bool:
        """Führt MEGA-Upload aus."""
        try:
            self.client.upload(str(context["local_path"]))
            self.logger.info(f"MEGA upload successful: {context['remote_path']}")
            return True
        except Exception as e:
            self.logger.error(f"MEGA upload failed: {str(e)}")
            raise

    async def _validate_upload_success(self, context: Dict[str, Any]) -> None:
        """Validiert erfolgreichen Upload."""
        try:
            # Prüfe ob Datei existiert (provider-agnostisch)
            files = await self.list_files(
                path=context["remote_path"], pattern=Path(context["remote_path"]).name
            )

            if not files:
                raise ValueError(
                    "Upload validation failed: File not found after upload"
                )

            uploaded_file = files[0]
            expected_size = context["file_size"]
            actual_size = uploaded_file.get("size", 0)

            if abs(expected_size - actual_size) > 1024:  # 1KB Toleranz
                raise ValueError(
                    f"Size mismatch: expected {expected_size}, got {actual_size}"
                )

            self.logger.info(f"Upload validation successful: {context['remote_path']}")

        except Exception as e:
            self.logger.error(f"Upload validation failed: {str(e)}")
            raise

    async def download_file(
        self,
        remote_path: str,
        local_path: Union[str, Path],
        chunk_size: int = 8 * 1024 * 1024,  # 8MB
        retry_count: int = 3,
    ) -> bool:
        """
        Lädt eine Datei aus dem Cloud-Speicher herunter

        Args:
            remote_path: Pfad im Cloud-Speicher
            local_path: Lokaler Pfad für die Datei
            chunk_size: Größe der Chunks für Chunked Download
            retry_count: Anzahl der Wiederholungsversuche

        Returns:
            bool: True wenn erfolgreich, False sonst
        """
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if self.config.provider == "aws":
                self.client.download_file(
                    self.config.bucket_name, remote_path, str(local_path)
                )

            elif self.config.provider == "gcp":
                blob = self.bucket.blob(remote_path)
                blob.download_to_filename(str(local_path))

            elif self.config.provider == "azure":
                blob_client = self.container.get_blob_client(remote_path)
                with open(local_path, "wb") as f:
                    blob_data = blob_client.download_blob()
                    blob_data.readinto(f)

            elif self.config.provider == "dropbox":
                self.client.files_download_to_file(str(local_path), remote_path)

            elif self.config.provider == "mega":
                self.client.download(remote_path, str(local_path))

            self.logger.info(f"Successfully downloaded {remote_path} to {local_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error downloading {remote_path}: {str(e)}")
            return False

    async def list_files(
        self,
        path: str = "",
        recursive: bool = False,
        pattern: Optional[str] = None,
        modified_after: Optional[datetime] = None,
        file_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Listet Dateien aus dem Cloud-Speicher auf.

        Args:
            path: Pfad im Cloud-Speicher
            recursive: Rekursiv durch Unterordner
            pattern: Dateiname-Muster
            modified_after: Nur Dateien nach diesem Datum
            file_types: Liste erlaubter Dateierweiterungen

        Returns:
            Liste von Datei-Informationen
        """
        try:
            # Provider-spezifische Listing-Strategie
            files = await self._get_provider_files(path, recursive)

            # Anwenden aller Filter
            filtered_files = await self._apply_file_filters(
                files, pattern, modified_after, file_types
            )

            # Sortierung und Finalisierung
            return self._finalize_file_list(filtered_files)

        except Exception as e:
            self.logger.error(f"Fehler beim Auflisten der Dateien: {str(e)}")
            raise

    async def _get_provider_files(
        self, path: str, recursive: bool
    ) -> List[Dict[str, Any]]:
        """Holt Dateien vom jeweiligen Cloud Provider."""
        if self.config.provider == "aws":
            return await self._list_s3_files(path, recursive)
        elif self.config.provider == "gcp":
            return await self._list_gcs_files(path, recursive)
        elif self.config.provider == "azure":
            return await self._list_azure_files(path, recursive)
        elif self.config.provider == "dropbox":
            return await self._list_dropbox_files(path, recursive)
        elif self.config.provider == "mega":
            return await self._list_mega_files(path, recursive)
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

    async def _list_s3_files(self, path: str, recursive: bool) -> List[Dict[str, Any]]:
        """Listet S3-Dateien auf."""
        files = []
        delimiter = "" if recursive else "/"

        try:
            response = await self.client.list_objects_v2(
                Bucket=self.config.bucket_name, Prefix=path, Delimiter=delimiter
            )

            for obj in response.get("Contents", []):
                file_info = self._create_file_info_from_s3(obj)
                files.append(file_info)

        except Exception as e:
            self.logger.error(f"S3 listing error: {str(e)}")
            raise

        return files

    async def _list_gcs_files(self, path: str, recursive: bool) -> List[Dict[str, Any]]:
        """Listet GCS-Dateien auf."""
        files = []
        delimiter = None if recursive else "/"

        try:
            blobs = self.bucket.list_blobs(prefix=path, delimiter=delimiter)

            for blob in blobs:
                file_info = self._create_file_info_from_gcs(blob)
                files.append(file_info)

        except Exception as e:
            self.logger.error(f"GCS listing error: {str(e)}")
            raise

        return files

    async def _list_azure_files(
        self, path: str, recursive: bool
    ) -> List[Dict[str, Any]]:
        """Listet Azure-Dateien auf."""
        files = []

        try:
            blobs = self.container.list_blobs(name_starts_with=path)

            for blob in blobs:
                if not recursive and "/" in blob.name[len(path) :].lstrip("/"):
                    continue

                file_info = self._create_file_info_from_azure(blob)
                files.append(file_info)

        except Exception as e:
            self.logger.error(f"Azure listing error: {str(e)}")
            raise

        return files

    async def _list_dropbox_files(
        self, path: str, recursive: bool
    ) -> List[Dict[str, Any]]:
        """Listet Dropbox-Dateien auf."""
        files = []

        try:
            result = self.client.files_list_folder(path, recursive=recursive)
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    files.append(
                        {
                            "name": entry.path_display,
                            "size": entry.size,
                            "modified": entry.server_modified,
                            "etag": entry.content_hash,
                            "provider": "dropbox",
                        }
                    )

        except Exception as e:
            self.logger.error(f"Dropbox listing error: {str(e)}")
            raise

        return files

    async def _list_mega_files(
        self, path: str, recursive: bool
    ) -> List[Dict[str, Any]]:
        """Listet Mega-Dateien auf."""
        files = []

        try:
            files_list = self.client.get_files()
            for file_id, file_data in files_list.items():
                if path and not file_data["a"]["n"].startswith(path):
                    continue
                files.append(
                    {
                        "name": file_data["a"]["n"],
                        "size": file_data["s"],
                        "modified": datetime.fromtimestamp(file_data["ts"]),
                        "etag": file_id,
                        "provider": "mega",
                    }
                )

        except Exception as e:
            self.logger.error(f"Mega listing error: {str(e)}")
            raise

        return files

    async def _apply_file_filters(
        self,
        files: List[Dict[str, Any]],
        pattern: Optional[str],
        modified_after: Optional[datetime],
        file_types: Optional[List[str]],
    ) -> List[Dict[str, Any]]:
        """Wendet alle Filter auf die Dateiliste an."""
        filtered = files

        # Pattern-Filter
        if pattern:
            filtered = self._filter_by_pattern(filtered, pattern)

        # Datum-Filter
        if modified_after:
            filtered = self._filter_by_date(filtered, modified_after)

        # Dateityp-Filter
        if file_types:
            filtered = self._filter_by_file_types(filtered, file_types)

        return filtered

    def _filter_by_pattern(
        self, files: List[Dict[str, Any]], pattern: str
    ) -> List[Dict[str, Any]]:
        """Filtert Dateien nach Name-Pattern."""
        import fnmatch

        return [f for f in files if fnmatch.fnmatch(f["name"], pattern)]

    def _filter_by_date(
        self, files: List[Dict[str, Any]], modified_after: datetime
    ) -> List[Dict[str, Any]]:
        """Filtert Dateien nach Änderungsdatum."""
        return [f for f in files if f["modified"] > modified_after]

    def _filter_by_file_types(
        self, files: List[Dict[str, Any]], file_types: List[str]
    ) -> List[Dict[str, Any]]:
        """Filtert Dateien nach Typ."""
        return [
            f
            for f in files
            if any(f["name"].lower().endswith(ext.lower()) for ext in file_types)
        ]

    def _finalize_file_list(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sortiert und finalisiert die Dateiliste."""
        return sorted(files, key=lambda x: x["modified"], reverse=True)

    def _create_file_info_from_s3(self, obj: Dict) -> Dict[str, Any]:
        """Erstellt File-Info aus S3-Objekt."""
        return {
            "name": obj["Key"],
            "size": obj["Size"],
            "modified": obj["LastModified"],
            "etag": obj["ETag"],
            "storage_class": obj.get("StorageClass", "STANDARD"),
            "provider": "s3",
        }

    def _create_file_info_from_gcs(self, blob) -> Dict[str, Any]:
        """Erstellt File-Info aus GCS-Blob."""
        return {
            "name": blob.name,
            "size": blob.size,
            "modified": blob.updated,
            "etag": blob.etag,
            "storage_class": blob.storage_class,
            "provider": "gcs",
        }

    def _create_file_info_from_azure(self, blob) -> Dict[str, Any]:
        """Erstellt File-Info aus Azure-Blob."""
        return {
            "name": blob.name,
            "size": blob.size,
            "modified": blob.last_modified,
            "etag": blob.etag,
            "storage_class": blob.blob_tier,
            "provider": "azure",
        }

    def _create_file_info_from_dropbox(
        self, entry: dropbox.files.FileMetadata
    ) -> Dict[str, Any]:
        """Erstellt File-Info aus Dropbox-Datei."""
        return {
            "name": entry.path_display,
            "size": entry.size,
            "modified": entry.server_modified,
            "etag": entry.content_hash,
            "provider": "dropbox",
        }

    def _create_file_info_from_mega(self, file_data: Dict) -> Dict[str, Any]:
        """Erstellt File-Info aus Mega-Datei."""
        return {
            "name": file_data["a"]["n"],
            "size": file_data["s"],
            "modified": datetime.fromtimestamp(file_data["ts"]),
            "etag": file_data["id"],
            "provider": "mega",
        }

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Gibt Statistiken über den Cloud-Speicher zurück

        Returns:
            Dict[str, Any]: Statistiken über den Speicher
        """
        try:
            stats = {
                "provider": self.config.provider,
                "bucket": self.config.bucket_name,
                "total_files": 0,
                "total_size": 0,
                "last_modified": None,
            }

            files = asyncio.run(self.list_files())
            for file in files:
                stats["total_files"] += 1
                stats["total_size"] += file["size"]
                if (
                    not stats["last_modified"]
                    or file["modified"] > stats["last_modified"]
                ):
                    stats["last_modified"] = file["modified"]

            return stats

        except Exception as e:
            self.logger.error(f"Error getting storage stats: {str(e)}")
            return {
                "provider": self.config.provider,
                "bucket": self.config.bucket_name,
                "error": str(e),
            }
