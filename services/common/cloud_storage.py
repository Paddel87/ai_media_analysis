import asyncio
import hashlib
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import aiofiles
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
        Lädt eine Datei in den Cloud-Speicher hoch

        Args:
            local_path: Lokaler Pfad der Datei
            remote_path: Pfad im Cloud-Speicher
            chunk_size: Größe der Chunks für Chunked Upload
            retry_count: Anzahl der Wiederholungsversuche

        Returns:
            bool: True wenn erfolgreich, False sonst
        """
        local_path = Path(local_path)
        if not local_path.exists():
            self.logger.error(f"Local file not found: {local_path}")
            return False

        file_size = local_path.stat().st_size
        upload_id = None

        try:
            if self.config.provider == "aws":
                if file_size > chunk_size:
                    # Multipart Upload für große Dateien
                    response = self.client.create_multipart_upload(
                        Bucket=self.config.bucket_name, Key=remote_path
                    )
                    upload_id = response["UploadId"]

                    parts = []
                    with open(local_path, "rb") as f:
                        for i, chunk in enumerate(
                            iter(lambda: f.read(chunk_size), b"")
                        ):
                            part_number = i + 1
                            response = self.client.upload_part(
                                Bucket=self.config.bucket_name,
                                Key=remote_path,
                                PartNumber=part_number,
                                UploadId=upload_id,
                                Body=chunk,
                            )
                            parts.append(
                                {"PartNumber": part_number, "ETag": response["ETag"]}
                            )

                    self.client.complete_multipart_upload(
                        Bucket=self.config.bucket_name,
                        Key=remote_path,
                        UploadId=upload_id,
                        MultipartUpload={"Parts": parts},
                    )
                else:
                    # Direkter Upload für kleine Dateien
                    self.client.upload_file(
                        str(local_path), self.config.bucket_name, remote_path
                    )

            elif self.config.provider == "gcp":
                blob = self.bucket.blob(remote_path)
                blob.upload_from_filename(str(local_path))

            elif self.config.provider == "azure":
                with open(local_path, "rb") as f:
                    self.container.upload_blob(name=remote_path, data=f, overwrite=True)

            elif self.config.provider == "dropbox":
                with open(local_path, "rb") as f:
                    self.client.files_upload(
                        f.read(), remote_path, mode=dropbox.files.WriteMode.overwrite
                    )

            elif self.config.provider == "mega":
                self.client.upload(str(local_path))

            self.logger.info(f"Successfully uploaded {local_path} to {remote_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error uploading {local_path}: {str(e)}")
            if upload_id and self.config.provider == "aws":
                try:
                    self.client.abort_multipart_upload(
                        Bucket=self.config.bucket_name,
                        Key=remote_path,
                        UploadId=upload_id,
                    )
                except Exception as abort_error:
                    self.logger.error(
                        f"Error aborting multipart upload: {str(abort_error)}"
                    )
            return False

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
        self, prefix: Optional[str] = None, max_results: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Listet Dateien im Cloud-Speicher auf

        Args:
            prefix: Optionaler Präfix für die Suche
            max_results: Maximale Anzahl der Ergebnisse

        Returns:
            List[Dict[str, Any]]: Liste der gefundenen Dateien mit Metadaten
        """
        try:
            files = []

            if self.config.provider == "aws":
                paginator = self.client.get_paginator("list_objects_v2")
                for page in paginator.paginate(
                    Bucket=self.config.bucket_name, Prefix=prefix, MaxKeys=max_results
                ):
                    for obj in page.get("Contents", []):
                        files.append(
                            {
                                "name": obj["Key"],
                                "size": obj["Size"],
                                "last_modified": obj["LastModified"].isoformat(),
                                "etag": obj["ETag"],
                            }
                        )

            elif self.config.provider == "gcp":
                blobs = self.bucket.list_blobs(prefix=prefix, max_results=max_results)
                for blob in blobs:
                    files.append(
                        {
                            "name": blob.name,
                            "size": blob.size,
                            "last_modified": blob.updated.isoformat(),
                            "etag": blob.etag,
                        }
                    )

            elif self.config.provider == "azure":
                blobs = self.container.list_blobs(
                    name_starts_with=prefix, maxresults=max_results
                )
                for blob in blobs:
                    files.append(
                        {
                            "name": blob.name,
                            "size": blob.size,
                            "last_modified": blob.last_modified.isoformat(),
                            "etag": blob.etag,
                        }
                    )

            elif self.config.provider == "dropbox":
                result = self.client.files_list_folder(prefix or "", limit=max_results)
                for entry in result.entries:
                    if isinstance(entry, dropbox.files.FileMetadata):
                        files.append(
                            {
                                "name": entry.path_display,
                                "size": entry.size,
                                "last_modified": entry.server_modified.isoformat(),
                                "etag": entry.content_hash,
                            }
                        )

            elif self.config.provider == "mega":
                files_list = self.client.get_files()
                for file_id, file_data in files_list.items():
                    if prefix and not file_data["a"]["n"].startswith(prefix):
                        continue
                    files.append(
                        {
                            "name": file_data["a"]["n"],
                            "size": file_data["s"],
                            "last_modified": datetime.fromtimestamp(
                                file_data["ts"]
                            ).isoformat(),
                            "etag": file_id,
                        }
                    )

            return files

        except Exception as e:
            self.logger.error(f"Error listing files: {str(e)}")
            return []

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
                    or file["last_modified"] > stats["last_modified"]
                ):
                    stats["last_modified"] = file["last_modified"]

            return stats

        except Exception as e:
            self.logger.error(f"Error getting storage stats: {str(e)}")
            return {
                "provider": self.config.provider,
                "bucket": self.config.bucket_name,
                "error": str(e),
            }
