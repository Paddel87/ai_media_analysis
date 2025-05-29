FROM pytorch/pytorch:2.2.0-cuda11.8-cudnn8-runtime

WORKDIR /app
COPY . .
RUN pip install torch torchvision torchaudio
CMD ["python", "serve.py"]