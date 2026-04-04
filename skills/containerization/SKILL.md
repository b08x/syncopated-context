---
name: containerization
description: Containerize applications using Docker with hardware-adaptive profiles (CPU, NVIDIA CUDA, Intel OpenVINO). Creates Dockerfiles, compose.yaml, and handles multi-service architectures.
license: MIT
allowed-tools: Read Edit Grep Glob Bash Write
metadata:
  author: b08x
  version: "1.0.0"
  category: automation
---

# Containerization Skill

Analyze, refactor, and containerize single or multi-service applications with
production-grade multi-stage Dockerfiles, hardware-adaptive compose orchestration
(CPU / NVIDIA / Intel), and automated project structure detection.

## Workflow Overview

The skill follows an **analyze → plan → confirm → execute** workflow:

1. **Detect** — Scan the project to identify frameworks, services, and databases
2. **Plan** — Present findings and a proposed containerization plan to the user
3. **Confirm** — Wait for user approval before making structural changes
4. **Generate** — Create Dockerfiles, compose.yaml, .env, and supporting files
5. **Verify** — Validate generated artifacts and provide usage instructions

## Trigger Scenarios

| User Intent | Action |
|------------|--------|
| "Containerize my project" | Full workflow: detect → refactor → generate all artifacts |
| "Create a new app with Docker" | Scaffold canonical structure + generate all artifacts |
| "Add Docker to my frontend/backend" | Targeted: generate Dockerfile for the specified service only |
| "Generate a compose.yaml" | Generate compose from existing structure (skip refactoring) |

## Phase 1: Project Detection (or Plan Consumption)

**If a `containerization-plan.json` exists in the project root**, the pre-flight
review agent has already collected all deployment context. Load the plan and skip
to Phase 4 (Generate Artifacts), using plan values instead of asking questions.
The plan schema is defined in the pre-flight-review skill's `references/plan-schema.md`.

**If no plan exists**, run the detection script against the project root:

```bash
bash /path/to/skill/scripts/detect_project.sh <project-root>
```

The script outputs JSON with:
- `detected_services` — frameworks, languages, locations for each service
- `detected_databases` — database engines found in deps or config
- `has_ai_workload` — whether AI/ML libraries were detected
- `current_structure` — `flat`, `split`, or `microservices`
- `existing_docker` — any pre-existing Dockerfiles or compose files

If the user has no existing project (creating from scratch), skip detection and
proceed directly to scaffolding the canonical directory structure.

## Phase 2: Present Plan to User

After detection, present a clear summary of findings and proposed actions.
Format the plan as a concise table or list covering:

- Detected services and their classifications
- Whether refactoring is needed (flat → microservices layout)
- Which Dockerfiles will be generated
- Which databases/services will appear in compose.yaml
- Hardware profiles to include (always include cpu/nvidia/intel)

**Wait for explicit user confirmation before proceeding.** The user may want to
adjust service names, exclude databases, or skip refactoring.

## Phase 3: Refactoring (If Needed)

If the project structure is `flat` and the user approved refactoring, run:

```bash
# Preview changes first
bash /path/to/skill/scripts/refactor_project.sh <project-root> --dry-run

# Execute after user confirms dry-run output
bash /path/to/skill/scripts/refactor_project.sh <project-root>
```

The refactoring script produces this canonical layout:

```
project-root/
├── services/
│   ├── web-frontend/       # React/Vue/Vite SPA
│   ├── backend-api/        # Ruby/Python/Node API
│   └── ai-inference/       # Python AI/ML worker
├── infra/
│   ├── database/           # SQL init scripts
│   └── nginx/              # Gateway configs
├── scripts/                # Utility scripts
├── compose.yaml
├── .env
└── .dockerignore
```

Skip refactoring when:
- Structure is already `microservices` or `split`
- User only wants Dockerfiles for specific services
- User explicitly declines restructuring

## Phase 4: Generate Artifacts

When a `containerization-plan.json` exists, use its values directly:
- `plan.hardware.target_profiles` → which ai-worker variants to generate
- `plan.services.*.include` → which Dockerfiles to create
- `plan.databases.*.containerized` → which databases appear in compose
- `plan.ports.*` → port mappings (no default assumptions)
- `plan.services.frontend.api_proxy` → whether to include nginx proxy config
- `plan.services.ai_worker.model_strategy` → affects Dockerfile RUN steps
- `plan.environment.env_style` → dev defaults vs production blanks in .env

When no plan exists, fall back to detection results and user confirmation.

### Dockerfiles

Read `references/dockerfile-templates.md` for all multi-stage build templates.
Select and adapt the appropriate template based on detected framework:

| Detection | Template to Use |
|-----------|----------------|
| Ruby / Sinatra / Rails | Ruby/Sinatra template |
| React / Vite / Vue | React/Vite template |
| Python / Flask / FastAPI / Django | Flask template |
| Python with torch/tensorflow/openvino | AI Inference template |
| Node / Express / Fastify / NestJS | Node.js Backend template |

Adaptation checklist for each Dockerfile:
- Correct base image version for the project's language version
- Entry command matches the project's actual entry point
- Port matches the service's configured port
- Build args set for AI workloads (`DEVICE_TYPE`)
- Non-root user configured
- `.dockerignore` present in project root

### compose.yaml

Read `references/compose-reference.md` for the full compose template.
Generate compose.yaml by including only the services detected in Phase 1:

- Always include all three hardware profiles (cpu, nvidia, intel)
- Include AI worker variants only if `has_ai_workload` is true
- Include database services only if detected in the project
- Wire `depends_on` with health checks for databases
- Use environment variable substitution for all secrets and ports

### Supporting Files

Generate these alongside the main artifacts:

1. **`.env`** — from the template in compose-reference.md, populated with
   project-specific values and safe defaults
2. **`.dockerignore`** — copy from `assets/dockerignore-template`
3. **`infra/database/init.sql`** — copy from `assets/init.sql` if pgvector detected
4. **`infra/nginx/default.conf`** — copy from `assets/nginx-spa.conf` if frontend detected
5. **`start.sh`** — copy from `assets/start.sh` for hardware auto-detection launcher

### For New Projects (No Existing Code)

When creating from scratch, scaffold the full canonical directory structure with:
- Placeholder service files (minimal app.rb, app.py, or index.tsx)
- Complete Dockerfiles for each requested service
- Full compose.yaml with all requested services
- .env with documented defaults
- .dockerignore

## Phase 5: Verify and Deliver

After generating all artifacts, verify:

1. All Dockerfiles referenced in compose.yaml exist at their specified paths
2. All `depends_on` targets exist as services in compose.yaml
3. Volume mounts reference existing directories
4. Port mappings have no collisions

Provide the user with:
- Quick-start commands: `docker compose --profile cpu up --build`
- Hardware auto-detect: `bash start.sh --build`
- Service URLs: frontend at `localhost:3000`, etc.
- How to switch profiles

## Reference Files

These files contain detailed templates and configuration. Load them as needed:

- **`references/dockerfile-templates.md`** — All multi-stage Dockerfile templates
  with adaptation notes for each framework
- **`references/compose-reference.md`** — Full compose.yaml template with service
  selection rules, hardware profiles, and .env template
- **`references/hardware-profiles.md`** — NVIDIA, Intel, and CPU configuration
  details including prerequisites, verification commands, and troubleshooting

## Asset Files

Copy these into the generated project as needed:

- **`assets/nginx-spa.conf`** — Nginx config for SPA routing (frontend service)
- **`assets/init.sql`** — PGVector extension initialization
- **`assets/start.sh`** — Hardware auto-detection launcher script
- **`assets/dockerignore-template`** — Standard .dockerignore for containerized projects
