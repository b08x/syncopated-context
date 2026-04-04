# Containerization Plan Schema

The pre-flight review agent produces a `containerization-plan.json` file that
captures all decisions made during the review. This plan is consumed by the
containerization skill to generate artifacts without ambiguity.

## Schema

```json
{
  "project_name": "my-app",
  "created_at": "2026-02-10T12:00:00Z",

  "environment": {
    "target": "cloud-vm | local-dev | on-prem | edge | ci-cd",
    "os": "linux-debian | linux-rhel | macos | windows-wsl2 | windows-native",
    "docker_installed": true,
    "env_style": "dev-defaults | production-blank"
  },

  "hardware": {
    "nvidia": {
      "available": true,
      "toolkit_installed": true
    },
    "intel": {
      "available": false,
      "igpu": false,
      "npu": false,
      "dev_dri_confirmed": false
    },
    "target_profiles": ["cpu", "nvidia"]
  },

  "services": {
    "frontend": {
      "include": true,
      "framework": "react",
      "build_tool": "vite",
      "location": "./services/web-frontend",
      "port": 3000,
      "needs_gpu": false,
      "api_proxy": true,
      "api_proxy_target": "/api/"
    },
    "backend": {
      "include": true,
      "framework": "sinatra",
      "language": "ruby",
      "location": "./services/backend-api",
      "port": 4567,
      "entry_cmd": "bundle exec rackup --host 0.0.0.0 -p 4567",
      "databases": ["postgres-vector", "redis-cache"]
    },
    "ai_worker": {
      "include": true,
      "location": "./services/ai-inference",
      "entry_cmd": "python inference_service.py",
      "ai_libraries": ["torch", "transformers", "chromadb"],
      "model_strategy": "runtime-download | build-baked | repo-included",
      "needs_gpu": true
    }
  },

  "databases": {
    "postgres-vector": {
      "include": true,
      "containerized": true,
      "image": "pgvector/pgvector:pg16",
      "port": 5432,
      "healthcheck_required": true,
      "init_script": true
    },
    "redis-cache": {
      "include": true,
      "containerized": true,
      "image": "redis:7-alpine",
      "port": 6379,
      "healthcheck_required": true
    },
    "chromadb": {
      "include": true,
      "containerized": true,
      "image": "chromadb/chroma:latest",
      "port": 8000,
      "healthcheck_required": true
    },
    "falkordb": {
      "include": false,
      "reason": "User confirmed not needed"
    }
  },

  "ports": {
    "frontend": 3000,
    "backend": 4567,
    "postgres": 5432,
    "redis": 6379,
    "chromadb": 8000,
    "falkordb": null
  },

  "refactoring": {
    "needed": true,
    "current_structure": "flat",
    "target_structure": "microservices",
    "approved": true
  },

  "notes": [
    "User confirmed NVIDIA toolkit is installed",
    "Frontend does not need GPU - confirmed",
    "Using managed Redis in production, containerized for dev"
  ]
}
```

## Field Reference

### environment
| Field | Values | Effect on Generation |
|-------|--------|---------------------|
| `target` | cloud-vm, local-dev, on-prem, edge, ci-cd | Edge: use slim images, no dev tools. CI: build-only, no volumes. |
| `os` | linux-debian, linux-rhel, macos, windows-wsl2, windows-native | Non-linux: omit /dev/dri, warn about GPU limitations |
| `docker_installed` | boolean | If false: include install instructions in output |
| `env_style` | dev-defaults, production-blank | dev: `.env` has `changeme` defaults. prod: blank with comments |

### hardware
| Field | Effect |
|-------|--------|
| `nvidia.available` | Include nvidia profile in compose |
| `nvidia.toolkit_installed` | If false and nvidia available: warn, suggest install steps |
| `intel.available` | Include intel profile in compose |
| `intel.dev_dri_confirmed` | If false and intel available: include verification note |
| `target_profiles` | Array of profiles to actually generate (subset of cpu/nvidia/intel) |

### services
| Field | Effect |
|-------|--------|
| `*.include` | Whether to generate Dockerfile and compose entry |
| `*.needs_gpu` | Whether service appears in GPU-specific profiles |
| `*.port` | Port mapping in compose |
| `ai_worker.model_strategy` | runtime-download: add volume mount. build-baked: add RUN download step |

### databases
| Field | Effect |
|-------|--------|
| `*.containerized` | true: include in compose. false: only wire env var |
| `*.healthcheck_required` | true: depends_on with condition. false: simple depends_on |
| `*.init_script` | true: mount init.sql to entrypoint dir |

## Validation Rules

Before writing the plan file, verify:
1. Every service in `services.backend.databases[]` exists in `databases`
2. No duplicate ports in `ports`
3. If `ai_worker.include` is true, at least one profile in `hardware.target_profiles`
4. If `hardware.nvidia.available` is false, "nvidia" is not in `target_profiles`
5. If `hardware.intel.available` is false, "intel" is not in `target_profiles`
6. If `environment.os` starts with "macos" or "windows", warn about GPU limitations
