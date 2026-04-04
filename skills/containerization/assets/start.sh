#!/bin/bash
# Auto-detect hardware acceleration and launch with appropriate profile
# Usage: ./start.sh [--build]

BUILD_FLAG=""
if [ "${1:-}" = "--build" ]; then
  BUILD_FLAG="--build"
fi

if command -v nvidia-smi &>/dev/null && nvidia-smi &>/dev/null; then
  PROFILE="nvidia"
  echo "Detected NVIDIA GPU — using CUDA profile"
elif [ -d "/dev/dri" ] && ls /dev/dri/renderD* &>/dev/null 2>&1; then
  PROFILE="intel"
  echo "Detected Intel GPU — using OpenVINO profile"
else
  PROFILE="cpu"
  echo "No GPU detected — using CPU profile"
fi

echo "Starting with profile: $PROFILE"
docker compose --profile "$PROFILE" up -d $BUILD_FLAG
