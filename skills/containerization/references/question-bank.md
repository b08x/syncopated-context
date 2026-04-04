# Pre-Flight Review Question Bank

Questions are organized by category and gated by detection conditions. Only ask
questions whose gate condition is met. Each question includes the decision it
informs in the final containerization plan.

## Host Environment

These questions apply to every containerization request.

### Q-ENV-01: Deployment Target
- **Gate:** Always
- **Ask:** "What is the deployment target for this project?"
- **Options:** Local development, Cloud VM (AWS/GCP/Azure), On-prem server, Edge device, CI/CD pipeline only
- **Informs:** `plan.environment.target` — affects resource limits, volume strategies, network config
- **Why it matters:** Edge deployments need smaller images; CI/CD may only need build validation; cloud VMs have different GPU passthrough than bare metal.

### Q-ENV-02: Docker Installation
- **Gate:** Always
- **Ask:** "Is Docker (with Compose v2) already installed on the target host?"
- **Options:** Yes / No / Not sure
- **Informs:** `plan.environment.docker_installed` — whether to include setup instructions
- **Why it matters:** Compose v2 syntax differs from legacy v1. GPU passthrough requires Docker 19.03+ with specific runtime configuration.

### Q-ENV-03: Operating System
- **Gate:** Always
- **Ask:** "What OS is running on the target host?"
- **Options:** Linux (Ubuntu/Debian), Linux (RHEL/Fedora), macOS, Windows (WSL2), Windows (native Docker Desktop)
- **Informs:** `plan.environment.os` — affects device passthrough paths, group permissions, volume performance
- **Why it matters:** `/dev/dri` and `/dev/accel` are Linux-only. macOS Docker has no GPU passthrough. WSL2 has partial NVIDIA support but no Intel iGPU passthrough.

## Hardware Acceleration

### Q-HW-01: NVIDIA GPU Availability
- **Gate:** `has_ai_workload == true` OR user explicitly mentions GPU
- **Ask:** "Does the target host have an NVIDIA GPU with drivers installed?"
- **Follow-up if yes:** "Is the NVIDIA Container Toolkit (nvidia-ctk) installed and configured?"
- **Options:** Yes (drivers + toolkit) / Yes (drivers only, no toolkit) / No NVIDIA GPU / Not sure
- **Informs:** `plan.hardware.nvidia` — whether to include nvidia profile and CUDA builds
- **Why it matters:** Having an NVIDIA GPU on the host does NOT mean the container runtime can access it. The NVIDIA Container Toolkit must be separately installed. Without it, `deploy.resources.reservations.devices` will fail silently or error.

### Q-HW-02: Intel GPU/NPU Availability
- **Gate:** `has_ai_workload == true` OR user explicitly mentions Intel
- **Ask:** "Does the target host have an Intel integrated GPU or NPU (Core Ultra)?"
- **Follow-up if yes:** "Can you confirm `/dev/dri/renderD128` exists on the host? (`ls /dev/dri/`)"
- **Options:** Yes (iGPU) / Yes (iGPU + NPU) / No / Not sure
- **Informs:** `plan.hardware.intel` — whether to include intel profile and OpenVINO builds
- **Why it matters:** Intel iGPU passthrough requires specific DRM device nodes and user group membership. If `/dev/dri` doesn't exist, the intel profile will fail at runtime with permission errors.

### Q-HW-03: Desired Compute Strategy
- **Gate:** `has_ai_workload == true`
- **Ask:** "For AI/ML inference, which hardware should the containers target?"
- **Options:** CPU only (simplest), NVIDIA GPU (fastest for supported models), Intel OpenVINO (efficient for Intel hardware), All profiles (generate all, choose at deploy time)
- **Informs:** `plan.hardware.target_profiles[]` — which ai-worker variants to generate
- **Why it matters:** Generating all three profiles adds complexity. If the user knows they only deploy on NVIDIA, omitting intel and cpu profiles keeps the compose cleaner and avoids maintaining unused Dockerfiles.

## Per-Service Review

### Q-SVC-01: Frontend GPU Requirement
- **Gate:** Frontend detected AND `has_ai_workload == true`
- **Ask:** "Your frontend ({framework}) was detected alongside AI workloads. The frontend itself does not need GPU access. Confirm: should the frontend service run on all profiles without GPU passthrough?"
- **Options:** Correct, no GPU needed / Actually, the frontend does client-side ML (e.g., TensorFlow.js) — but note this runs in-browser, not in Docker
- **Informs:** `plan.services.frontend.needs_gpu` (almost always false)
- **Why it matters:** This is the exact scenario the user described — a React app on a host with NVIDIA drivers doesn't mean the React container needs CUDA. Prevents unnecessary image bloat and misleading compose config.

### Q-SVC-02: Backend Dependencies
- **Gate:** Backend detected
- **Ask:** "Which of these detected databases does your backend actually connect to?"
- **Present:** List of detected databases from detection JSON
- **Options:** Checkboxes for each detected database + "None of these — I use an external/managed database" + "All of the above"
- **Informs:** `plan.services.backend.databases[]` — which data services to include in compose
- **Why it matters:** Detection finds references in code/config, but some may be legacy, commented out, or only used in specific environments. Including unnecessary databases wastes resources and adds startup time.

### Q-SVC-03: External vs Containerized Services
- **Gate:** Any database detected
- **Ask:** "Should these databases run as containers, or will you connect to external/managed instances (e.g., AWS RDS, managed Redis)?"
- **Per-database options:** Containerize it / Use external (I'll provide connection string)
- **Informs:** `plan.databases[].containerized` — whether to include in compose or just wire env vars
- **Why it matters:** Production deployments often use managed databases. Containerizing postgres when an RDS instance exists creates data duplication risk and operational confusion.

### Q-SVC-04: AI Worker Entry Point
- **Gate:** AI workload detected
- **Ask:** "What is the main entry script for your AI/inference service?"
- **Default suggestion:** Based on detected files (inference_service.py, model_server.py, etc.)
- **Informs:** `plan.services.ai_worker.entry_cmd` — the CMD in the AI Dockerfile
- **Why it matters:** AI projects often have multiple Python scripts (training, inference, evaluation). The wrong entry point means the container starts the wrong process.

### Q-SVC-05: AI Model Loading Strategy
- **Gate:** AI workload detected
- **Ask:** "How should AI models be loaded?"
- **Options:** Download at build time (baked into image) / Download at runtime (mounted volume or fetched on start) / Models are already in the repo
- **Informs:** `plan.services.ai_worker.model_strategy` — affects Dockerfile RUN steps and volume mounts
- **Why it matters:** Baking models into images creates very large (multi-GB) images that are slow to push/pull. Runtime loading is more flexible but adds startup latency. This is a critical production decision.

## Networking and Ports

### Q-NET-01: Port Conflicts
- **Gate:** Always
- **Ask:** "Are any of these ports already in use on the target host?"
- **Present:** Default ports: 3000 (frontend), 4567/5000/8000 (backend), 5432 (postgres), 6379 (redis), 8000 (chromadb)
- **Informs:** `plan.ports` — port mapping overrides in compose
- **Why it matters:** Port conflicts cause silent failures or misleading error messages at `docker compose up`.

### Q-NET-02: API Proxying
- **Gate:** Frontend AND backend both detected
- **Ask:** "Should the frontend's Nginx proxy API requests to the backend? (e.g., `/api/*` routes to backend service)"
- **Options:** Yes, proxy through Nginx / No, frontend calls backend directly (CORS) / Not sure
- **Informs:** `plan.services.frontend.api_proxy` — whether to include proxy config in nginx-spa.conf
- **Why it matters:** Proxying through Nginx simplifies CORS and lets the frontend call relative URLs. Direct calls require CORS headers on the backend and absolute URLs in frontend config.

## Production Readiness

### Q-PROD-01: Environment Secrets
- **Gate:** Always
- **Ask:** "Should the generated `.env` file contain placeholder defaults (for dev) or should all secrets be left blank (for production)?"
- **Options:** Placeholder defaults (dev-friendly) / Blank values with comments (production)
- **Informs:** `plan.environment.env_style` — how .env is generated
- **Why it matters:** Shipping default passwords like `changeme` into production is a security incident waiting to happen.

### Q-PROD-02: Healthcheck Strictness
- **Gate:** Any database detected
- **Ask:** "Should services wait for database health checks before starting? (Recommended for production, slows down dev startup)"
- **Options:** Yes, strict dependency ordering / No, start everything in parallel
- **Informs:** `plan.databases[].healthcheck_required` — whether depends_on uses condition: service_healthy
- **Why it matters:** Health checks add 10-30 seconds to startup but prevent race conditions where the backend crashes because postgres isn't ready yet.
