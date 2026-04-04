# Dockerfile Templates Reference

Multi-stage build templates for each supported framework. All templates follow these principles:
- Builder stage compiles/installs dependencies with build tools
- Runtime stage contains only binaries and shared libraries
- Non-root user (`appuser`) for security
- Exec-form CMD for proper signal handling

## Ruby / Sinatra

Optimized for gems with C-extensions (pg, nokogiri). Uses Alpine for minimal size.

```dockerfile
# Stage 1: Builder
FROM ruby:3.2-alpine AS builder
RUN apk add --no-cache build-base postgresql-dev git
WORKDIR /app
COPY Gemfile Gemfile.lock ./
RUN bundle config set --local path 'vendor/bundle' && \
    bundle config set --local without 'development test' && \
    bundle install --jobs=4 --retry=3

# Stage 2: Runtime
FROM ruby:3.2-alpine AS runner
RUN apk add --no-cache postgresql-client tzdata && \
    adduser -D -u 1000 appuser
WORKDIR /app
COPY --from=builder --chown=appuser:appuser /app/vendor/bundle /app/vendor/bundle
COPY --from=builder --chown=appuser:appuser /app/.bundle /app/.bundle
COPY --chown=appuser:appuser . .
USER appuser
ENV RACK_ENV=production
CMD ["bundle", "exec", "rackup", "--host", "0.0.0.0", "-p", "4567"]
```

**Adaptation notes:**
- If no C-extensions: drop `build-base` and `postgresql-dev` from builder
- For Rails: change CMD to `["bundle", "exec", "rails", "server", "-b", "0.0.0.0"]`
- Add `EXPOSE 4567` (Sinatra) or `EXPOSE 3000` (Rails) as appropriate

## React / Vite (Static SPA)

Build with Node, serve with Nginx. Node.js is entirely absent from runtime.

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine-slim AS production
COPY --from=builder /app/dist /usr/share/nginx/html
# Optional: SPA routing config
# COPY nginx-spa.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Adaptation notes:**
- For yarn: replace `npm ci` with `yarn install --frozen-lockfile`
- For pnpm: replace with `corepack enable && pnpm install --frozen-lockfile`
- CRA outputs to `build/` not `dist/` — adjust COPY path
- For Next.js SSR: use `node:20-alpine` runtime instead of Nginx
- Include `nginx-spa.conf` from assets/ for SPA routing

## Python / Flask (Web API)

Virtual environment copied between stages for clean separation.

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim AS runner
WORKDIR /app
RUN groupadd -r appuser && useradd -r -g appuser appuser
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv
COPY --chown=appuser:appuser . .
ENV PATH="/opt/venv/bin:$PATH"
USER appuser
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

**Adaptation notes:**
- FastAPI: change CMD to `["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]`
- Django: change CMD to `["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]`
- If using pyproject.toml: replace `pip install -r requirements.txt` with `pip install .`

## Python / AI Inference (Hardware-Adaptive)

Supports CPU, NVIDIA CUDA, and Intel OpenVINO via build arg.

```dockerfile
# Stage 1: Builder
FROM python:3.10-slim AS builder
ARG DEVICE_TYPE=cpu
WORKDIR /app
RUN apt-get update && apt-get install -y git build-essential

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .

# Conditional: CPU-only PyTorch is ~200MB vs CUDA ~1GB+
RUN if [ "$DEVICE_TYPE" = "cpu" ]; then \
      pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu; \
    elif [ "$DEVICE_TYPE" = "openvino" ]; then \
      pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
      pip install --no-cache-dir openvino openvino-dev; \
    else \
      pip install --no-cache-dir torch torchvision; \
    fi
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.10-slim AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Intel OpenCL support (only adds ~15MB, safe to include universally)
RUN apt-get update && apt-get install -y --no-install-recommends \
    intel-opencl-icd 2>/dev/null || true && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY . .
CMD ["python", "inference_service.py"]
```

**Adaptation notes:**
- Adjust `CMD` to match the actual entry script name
- For TensorFlow: replace PyTorch install lines with `pip install tensorflow` (CPU) or `pip install tensorflow[and-cuda]` (GPU)
- For models that need downloading at build time, add `RUN python -c "from transformers import AutoModel; AutoModel.from_pretrained('model-name')"`

## Node.js Backend (Express/Fastify/NestJS)

```dockerfile
# Stage 1: Builder (for TypeScript projects)
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build 2>/dev/null || true

# Stage 2: Runtime
FROM node:20-alpine AS runner
RUN adduser -D -u 1000 appuser
WORKDIR /app
COPY --from=builder --chown=appuser:appuser /app/dist ./dist
COPY --from=builder --chown=appuser:appuser /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:appuser /app/package.json .
USER appuser
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

**Adaptation notes:**
- For plain JS (no build step): skip builder stage, just `COPY . .` and `CMD ["node", "index.js"]`
- For NestJS: CMD is typically `["node", "dist/main.js"]`
- Add health check: `HEALTHCHECK CMD wget -qO- http://localhost:3000/health || exit 1`
