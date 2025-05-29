#!/bin/bash
# Create required folder structure for AI Media Analysis pipeline

echo "Initializing directory structure..."

mkdir -p data/input/videos
mkdir -p data/input/series
mkdir -p data/frames
mkdir -p data/objects
mkdir -p data/transcripts
mkdir -p data/meta
mkdir -p data/operator
mkdir -p data/feedback/trainset
mkdir -p data/logs

echo "Done. Directory tree created under ./data/"
