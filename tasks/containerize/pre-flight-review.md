---
name: pre-flight-review
description: Pre-flight review agent for containerization projects. This skill should be used before containerizing an application to gather critical deployment context such as target environment, available hardware acceleration, database requirements, and port assignments. It analyzes the project structure, asks targeted questions based on what is detected, and outputs a validated containerization-plan.json that the containerization skill consumes. Triggers include mentions of review before containerizing, pre-flight check, deployment questionnaire, or when the containerization skill is about to run on a new project.
---

# Pre-Flight Review Agent

Analyze a project and conduct a targeted review with the user to produce a
validated `containerization-plan.json`. This plan eliminates assumptions and
ensures the containerization skill generates correct, environment-specific
artifacts on the first pass.

## Why This Agent Exists

Automated detection can identify *what* is in a project, but not *how* or
*where* it will be deployed. Common false assumptions that cause runtime failures:

- A React frontend on an NVIDIA host does not need GPU passthrough
- An NVIDIA GPU on the host does not mean nvidia-ctk is installed
- A `chromadb` import in requirements.txt may be legacy/unused
- Default port 5432 may already be occupied by a host-level postgres
- A Python AI service may intend CPU-only inference despite torch being installed

The review agent catches these by asking targeted questions gated on detection
results, then encoding the answers into a structured plan.

## Workflow

```
detect project → select relevant questions → ask user → validate answers → write plan
```

### Step 1: Run Project Detection

Reuse the containerization skill's detection script. The script path is relative
to the devops plugin's skill directory:

```bash
bash <containerization-skill-path>/scripts/detect_project.sh <project-root>
```

Parse the JSON output into working variables:
- `detected_services[]` — list of services with framework, language, location
- `detected_databases[]` — list of databases with type and image
- `has_ai_workload` — boolean flag for AI/ML presence
- `current_structure` — flat, split, or microservices
- `existing_docker` — any pre-existing Dockerfiles or compose files

If no project exists (user is creating from scratch), skip detection and ask
the user what services they want to include, then proceed to environment questions.

### Step 2: Select and Ask Questions

Load `references/question-bank.md` to access the full question bank. Each
question has a **gate condition** — only ask questions whose gate is satisfied
by the detection results.

**Question selection rules:**

1. Always ask: Q-ENV-01 (target), Q-ENV-02 (Docker), Q-ENV-03 (OS), Q-NET-01 (ports), Q-PROD-01 (secrets)
2. If `has_ai_workload`: ask Q-HW-01 (NVIDIA), Q-HW-02 (Intel), Q-HW-03 (compute strategy), Q-SVC-04 (entry point), Q-SVC-05 (model loading)
3. If frontend detected: ask Q-SVC-01 (frontend GPU — especially when AI workloads also present)
4. If backend detected: ask Q-SVC-02 (database connections)
5. If any database detected: ask Q-SVC-03 (external vs container), Q-PROD-02 (healthchecks)
6. If frontend AND backend: ask Q-NET-02 (API proxy)

**Presentation guidelines:**

- Group questions into logical batches (environment, hardware, services, networking)
- Present one batch at a time to avoid overwhelming the user
- Provide sensible defaults based on detection results (the user can accept or override)
- For each question, briefly explain *why it matters* to motivate the user to answer accurately
- If the user gives a vague answer, ask a targeted follow-up rather than assuming

**Batch ordering:**

1. **Environment batch:** Q-ENV-01, Q-ENV-02, Q-ENV-03
2. **Hardware batch** (if applicable): Q-HW-01, Q-HW-02, Q-HW-03
3. **Services batch:** Q-SVC-01 through Q-SVC-05 (as gated)
4. **Infrastructure batch:** Q-NET-01, Q-NET-02, Q-SVC-02, Q-SVC-03
5. **Production batch:** Q-PROD-01, Q-PROD-02

### Step 3: Build and Validate the Plan

After collecting all answers, assemble the `containerization-plan.json` following
the schema in `references/plan-schema.md`.

**Validation checks before writing:**

1. Every database referenced in `services.backend.databases[]` exists in `databases`
2. No duplicate values in `ports`
3. If `ai_worker.include` is true, at least one entry in `hardware.target_profiles`
4. If `hardware.nvidia.available` is false, "nvidia" is NOT in `target_profiles`
5. If `hardware.intel.available` is false, "intel" is NOT in `target_profiles`
6. If OS is macOS or Windows-native, warn that GPU passthrough has limitations
7. All included services have a valid `location` path (or note that scaffolding is needed)

If validation fails, present the specific issue to the user and ask for correction.

### Step 4: Present Plan Summary

Before writing the file, present a human-readable summary of the plan:

```
=== Containerization Plan Summary ===

Target: Cloud VM (Ubuntu), Docker installed
Hardware: NVIDIA GPU (toolkit confirmed), no Intel
Profiles to generate: cpu, nvidia

Services:
  ✓ Frontend (React/Vite) → port 3000, no GPU, Nginx proxy to /api/
  ✓ Backend (Sinatra/Ruby) → port 4567, connects to postgres + redis
  ✓ AI Worker (PyTorch) → inference_service.py, models downloaded at runtime

Databases (containerized):
  ✓ PostgreSQL + pgvector → port 5432, healthcheck enabled
  ✓ Redis → port 6379, healthcheck enabled
  ✗ ChromaDB → excluded (user confirmed not needed)

Refactoring: needed (flat → microservices layout)
Environment: dev defaults in .env

Notes:
  - Frontend confirmed: no GPU needed despite NVIDIA host
  - NVIDIA Container Toolkit confirmed installed
```

Ask the user to confirm the plan. Allow amendments before writing.

### Step 5: Write the Plan File

Write `containerization-plan.json` to the project root:

```bash
# Write to project root
cat > <project-root>/containerization-plan.json << 'EOF'
{ ... validated plan JSON ... }
EOF
```

Inform the user that the containerization skill can now consume this plan:
"The plan is ready. Run the containerization skill against this project and it
will use `containerization-plan.json` to generate all artifacts without further
questions."

## Handling Edge Cases

### No project exists yet (greenfield)
Skip detection. Ask the user what services they want (frontend, backend, AI worker).
Ask environment and hardware questions normally. Set `refactoring.needed: false`
and `refactoring.current_structure: "none"` in the plan.

### Project already has Docker artifacts
Note existing Dockerfiles and compose files in the plan summary. Ask:
"This project already has Docker configuration. Should the containerization
skill overwrite existing files, or generate alongside them with a different
name (e.g., `Dockerfile.new`)?"

### User doesn't know their hardware
Suggest running diagnostic commands:
- NVIDIA: `nvidia-smi` and `docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi`
- Intel: `ls /dev/dri/` and `cat /proc/cpuinfo | grep "model name"`
- Docker: `docker compose version`

If the user cannot run these, default to CPU-only profile with a note that
GPU profiles can be added later.

### Single-service project
If only one service is detected (e.g., just a Flask API), skip batch ordering
and present a minimal question set: environment + the relevant service questions.
The compose file may only need one service plus an optional database.

## Reference Files

- **`references/question-bank.md`** — Complete question catalog with gate
  conditions, options, and impact descriptions. Load this to determine which
  questions to ask based on detection results.
- **`references/plan-schema.md`** — JSON schema for containerization-plan.json
  with field reference table and validation rules. Load this when assembling
  the final plan output.
