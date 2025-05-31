# AI Media Analysis Platform

A comprehensive media analysis platform that leverages artificial intelligence to analyze images and videos for various content types, including NSFW content, poses, text, and restraints.

## 🌟 Features

- **Multi-Service Architecture**: Modular design with specialized services for different analysis tasks
- **Real-time Processing**: Efficient batch processing and frame sampling for video analysis
- **GPU Acceleration**: NVIDIA GPU support for high-performance inference
- **Scalable Infrastructure**: Docker-based deployment with resource management
- **Job Management**: Asynchronous job processing with status tracking
- **RESTful API**: FastAPI-based endpoints for easy integration

## 🏗️ Architecture

### Core Services

- **Vision Pipeline**: Central service coordinating all analysis tasks
- **Job Manager**: Handles job queuing and processing
- **Restraint Detection**: Specialized service for detecting restraints and related materials
- **NSFW Detection**: Content moderation using CLIP-based models
- **Pose Estimation**: Body pose and movement analysis
- **OCR Detection**: Text and logo recognition
- **Face Recognition**: Face detection and re-identification

### Supporting Services

- **Redis**: Message broker and caching
- **Control Service**: System orchestration
- **Streamlit UI**: Web interface for monitoring and control
- **Vector Database**: Efficient storage and retrieval of embeddings

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- NVIDIA GPU with CUDA support
- NVIDIA Container Toolkit
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Paddel87/ai_media_analysis.git
   cd ai_media_analysis
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Build and start the services:
   ```bash
   docker-compose up -d
   ```

### Configuration

Key configuration options in `.env`:

```env
# API Keys
VAST_API_KEY=your_vast_api_key
RUNPOD_API_KEY=your_runpod_api_key

# Service URLs
VISION_PIPELINE_URL=http://vision_pipeline:8000
JOB_MANAGER_URL=http://job_manager_api:8000

# Processing Settings
BATCH_SIZE=4
FRAME_SAMPLING_RATE=2
MAX_WORKERS=4
```

## 📊 API Documentation

### Vision Pipeline Endpoints

- `POST /analyze/video`: Analyze video content
- `POST /analyze/image`: Analyze single image
- `GET /health`: Service health check

### Job Manager Endpoints

- `POST /jobs`: Create new analysis job
- `GET /jobs/{job_id}`: Get job status
- `GET /jobs`: List all jobs

## 🔧 Development

### Project Structure

```
ai_media_analysis/
├── services/
│   ├── vision_pipeline/
│   ├── restraint_detection/
│   ├── job_manager/
│   └── common/
├── control/
├── streamlit_ui/
├── data/
└── setup/
```

### Adding New Services

1. Create service directory in `services/`
2. Add Dockerfile and requirements.txt
3. Update docker-compose.yml
4. Implement service logic
5. Add health check endpoint

## 📈 Performance

- Batch processing for efficient resource utilization
- LRU caching for repeated frame analysis
- Asynchronous processing for concurrent tasks
- GPU acceleration for ML inference
- Resource limits and reservations for stability

## 🔒 Security

- API key authentication
- Secure service communication
- Resource isolation
- Input validation
- Error handling and logging

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📝 License

This project is licensed under the MIT License - see [LICENSE.md](LICENSE.md) for details.

## 📞 Support

For support, please open an issue in the GitHub repository.

## 🔄 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

## 📊 Status

Current project status and roadmap can be found in [STATUS.md](STATUS.md).
