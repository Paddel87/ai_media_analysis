import logging
import os
from datetime import datetime
from typing import List

import cv2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThumbnailGenerator:
    def __init__(self, output_size=(320, 180)):
        self.output_size = output_size

    def generate_thumbnails(
        self, video_path: str, output_dir: str, num_thumbnails: int = 4
    ) -> List[str]:
        """
        Generiert Vorschaubilder für ein Video

        Args:
            video_path: Pfad zum Video
            output_dir: Ausgabeverzeichnis für Vorschaubilder
            num_thumbnails: Anzahl der zu generierenden Vorschaubilder

        Returns:
            Liste der Pfade zu den generierten Vorschaubildern
        """
        try:
            # Video öffnen
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Konnte Video nicht öffnen: {video_path}")

            # Video-Informationen
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps

            # Berechne Zeitpunkte für Vorschaubilder
            intervals = [
                duration * (i + 1) / (num_thumbnails + 1) for i in range(num_thumbnails)
            ]

            thumbnail_paths = []
            for i, interval in enumerate(intervals):
                # Frame-Position setzen
                frame_pos = int(interval * fps)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)

                # Frame lesen
                ret, frame = cap.read()
                if not ret:
                    logger.warning(f"Konnte Frame bei {interval}s nicht lesen")
                    continue

                # Vorschaubild generieren
                thumbnail = cv2.resize(frame, self.output_size)

                # Speichern
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.join(output_dir, f"thumb_{i+1}_{timestamp}.jpg")
                cv2.imwrite(output_path, thumbnail)
                thumbnail_paths.append(output_path)

            cap.release()
            return thumbnail_paths

        except Exception as e:
            logger.error(f"Fehler bei der Vorschaubild-Generierung: {str(e)}")
            raise


def process_video(video_path: str, job_id: str):
    """
    Verarbeitet ein Video und generiert Vorschaubilder

    Args:
        video_path: Pfad zum Video
        job_id: ID des Jobs
    """
    try:
        # Ausgabeverzeichnis erstellen
        output_dir = f"data/incoming/videos/{job_id}/thumbnails"
        os.makedirs(output_dir, exist_ok=True)

        # Vorschaubilder generieren
        generator = ThumbnailGenerator()
        thumbnail_paths = generator.generate_thumbnails(video_path, output_dir)

        logger.info(
            f"Vorschaubilder generiert für Job {job_id}: {len(thumbnail_paths)} Bilder"
        )
        return thumbnail_paths

    except Exception as e:
        logger.error(f"Fehler bei der Video-Verarbeitung: {str(e)}")
        raise


if __name__ == "__main__":
    # Beispiel-Verwendung
    video_path = "data/incoming/videos/job_20240101_120000/raw/example.mp4"
    job_id = "job_20240101_120000"
    process_video(video_path, job_id)
