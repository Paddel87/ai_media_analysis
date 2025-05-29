## [Unreleased]
### Added
- Integrated missing services:
  - `pose_estimation`
  - `ocr_detection`
  - `clip_nsfw`
  - `face_reid`
  - `whisper_transcriber`
- Extended docker-compose.yml to include all modules
- Created `README.md` placeholders for new services

### Changed
- Updated docker-compose to mount new volumes for extended processing
- `vision_pipeline` now supports image series

### Pending
- GPU runtime validation
- Inter-service signaling via Redis (jobs, results, scaling triggers)
- Shared logging and healthchecks
