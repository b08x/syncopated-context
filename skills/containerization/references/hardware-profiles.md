# Hardware Acceleration Profiles Reference

## NVIDIA GPU (CUDA)

**Prerequisites on host:**
- NVIDIA driver installed
- NVIDIA Container Toolkit (`nvidia-ctk`) installed and configured
- Docker daemon configured with nvidia runtime

**Compose configuration:**
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1          # or "all" for multi-GPU
          capabilities: [gpu]  # add "utility" for nvidia-smi access
```

**Environment variables:**
- `NVIDIA_VISIBLE_DEVICES=all` — expose all GPUs (or specific IDs like `0,1`)
- `NVIDIA_DRIVER_CAPABILITIES=compute,utility` — fine-grained capability control

**Dockerfile build arg:** `DEVICE_TYPE=gpu` triggers full CUDA PyTorch install.

**Verification command:** `docker exec <container> nvidia-smi`

---

## Intel iGPU / NPU (OpenVINO)

**Prerequisites on host:**
- Intel GPU drivers (i915 for iGPU, intel_vpu for NPU)
- `/dev/dri` exists (DRM render nodes)
- `/dev/accel` exists (NPU, Intel Core Ultra and newer)
- User in `render` and `video` groups

**Compose configuration:**
```yaml
devices:
  - /dev/dri:/dev/dri          # iGPU access via DRM
  - /dev/accel:/dev/accel      # NPU access (Core Ultra)
group_add:
  - video                       # GPU render permission
  - render                      # GPU render permission
environment:
  - ONEAPI_DEVICE_SELECTOR=level_zero:gpu
```

**Dockerfile requirements (runtime stage):**
- `intel-opencl-icd` package for OpenCL support
- OpenVINO pip package in builder stage

**Dockerfile build arg:** `DEVICE_TYPE=openvino` triggers CPU PyTorch + OpenVINO install.

**Verification command:** `docker exec <container> python -c "from openvino import Core; print(Core().available_devices)"`

**Common issues:**
- Permission denied on `/dev/dri/renderD128`: ensure `group_add: [render, video]`
- NPU not detected: check that `/dev/accel/accel0` exists on host
- OpenCL errors: verify `intel-opencl-icd` is installed in container

---

## CPU Fallback

No special hardware configuration needed. Acts as universal fallback for development or hosts without acceleration hardware.

**Compose configuration:** No `deploy`, `devices`, or `group_add` keys.

**Dockerfile build arg:** `DEVICE_TYPE=cpu` triggers CPU-only PyTorch (~200MB vs ~1GB+ CUDA).

**When to use:**
- Development environments
- CI/CD pipelines
- Hosts without GPU hardware
- Cost-sensitive deployments where inference latency is acceptable

---

## Profile Selection Logic

To auto-detect the appropriate profile on the host system:

```bash
# detect_hardware.sh
if command -v nvidia-smi &>/dev/null && nvidia-smi &>/dev/null; then
  echo "nvidia"
elif [ -d "/dev/dri" ] && ls /dev/dri/renderD* &>/dev/null; then
  echo "intel"
else
  echo "cpu"
fi
```

Usage: `docker compose --profile $(./detect_hardware.sh) up -d`
