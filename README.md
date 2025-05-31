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

### Docker and Docker Compose
- Docker Engine 24.0.0 or later
- Docker Compose v2.20.0 or later
- NVIDIA Container Toolkit

### GPU Support
The system supports various GPU configurations:

#### Local GPU Setup
- Consumer GPUs: RTX 3060, 3070, 3080, 3090, 4070, 4080, 4090
- Professional GPUs: RTX A4000, A5000, A6000
- Data Center GPUs: A100, H100

#### Cloud GPU Options
1. **Data Center GPUs** (Enterprise Cloud Providers)
   - AWS, GCP, Azure: A100, H100
   - Enterprise-grade reliability
   - 24/7 support
   - Higher cost

2. **Consumer GPUs** (Specialized Providers)
   - Vast.ai, RunPod: RTX 3080, 3090, 4080, 4090
   - Cost-effective for development
   - Flexible hourly pricing
   - Good for testing and medium workloads

3. **Professional GPUs** (Mixed Providers)
   - RTX A4000, A5000, A6000
   - Available on both enterprise and specialized providers
   - Balanced performance and cost

### System Requirements
- Minimum 16GB RAM
- 100GB free disk space
- CUDA 12.0 or later
- Ubuntu 20.04/22.04 or Windows 11 with WSL2

### Installation

1. Clone the repository:
   ```