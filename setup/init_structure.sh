#!/bin/bash

echo "Creating service directories..."
mkdir -p services/{vision_pipeline,embedding_server,llm_summarizer,object_review,vector_db,ui,control}

echo "Setting permissions..."
chmod +x services/*/*.sh 2>/dev/null || true

echo "Done initializing project structure."
