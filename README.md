# 🎓 AI Language Learning Agent

> **CSE 363 – Cloud Computing Course Project**  
> Galala University · Faculty of Computer Science and Engineering

A cloud-deployed, multi-container AI-powered English language tutor built with FastAPI, Next.js, ChromaDB, and LLMs — running on Huawei Cloud ECS with full monitoring and Kubernetes support.

🚀 **Link for the recorded video of the project:** [Production-Ready English Tutor deployed on Huawei Cloud](https://drive.google.com/file/d/19EnWRf23pz5yzYd8eOWfUHbwSOa739zb/view?usp=sharing)

🌐 **Live Demo:** [https://lang-agent-asser.duckdns.org](https://lang-agent-asser.duckdns.org)  
📊 **Monitoring:** [https://lang-agent-asser.duckdns.org/stats/](https://lang-agent-asser.duckdns.org/stats/)

---

## 📖 Overview

The **AI Language Learning Agent** is an intelligent, interactive platform that helps users master English through AI-driven tools. It uses multiple LLM models (Llama 3.3 70B via Groq/OpenRouter) combined with a Retrieval-Augmented Generation (RAG) pipeline over a curated knowledge base of **1,781 documents** covering grammar rules, vocabulary, and common phrases.

### Problem It Solves

Language learners often lack access to personalized, on-demand tutors. Traditional learning apps offer static exercises with no adaptability. This platform provides **real-time, context-aware** assistance — the AI understands what the user is asking, retrieves relevant knowledge, and generates tailored responses using state-of-the-art language models.

### Who It's For

- English language learners (beginner to advanced)
- Students preparing for language exams
- Educators looking for AI-assisted teaching tools

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🗣️ **Grammar Assistant** | Explains grammar rules with examples from the knowledge base |
| 📚 **Vocabulary Builder** | Teaches new words with definitions, synonyms, and usage |
| 🌍 **Translation Tool** | Translates text between languages with context |
| 📝 **Interactive Quizzes** | Generates custom quizzes on any topic with scoring |
| 💬 **Conversation Mode** | Free-form English conversation practice with the AI |
| 🎤 **Speech-to-Text** | Voice input via Groq Whisper for hands-free learning |
| 🔊 **Text-to-Speech** | Listen to AI responses with natural audio playback |
| 📸 **OCR (Image-to-Text)** | Extract text from images for analysis |
| 📧 **Email Reports** | Automated quiz results and session summaries via email |
| 📊 **Live Monitoring** | Real-time Grafana dashboard with container metrics |

---

## 🏗️ Architecture

```
                        ┌──────────────────────────────────────────┐
                        │          Huawei Cloud ECS Server          │
                        │           (159.138.84.175)                │
    ┌──────────┐        │                                          │
    │  User    │◄──HTTPS──► NGINX (SSL + Reverse Proxy)            │
    │ Browser  │        │       │            │          │           │
    └──────────┘        │       ▼            ▼          ▼           │
                        │  ┌─────────┐ ┌──────────┐ ┌────────┐    │
                        │  │Frontend │ │ Backend  │ │Grafana │    │
                        │  │Next.js  │ │ FastAPI  │ │Dashboard│   │
                        │  │ :3000   │ │  :8000   │ │ :3001  │    │
                        │  └─────────┘ └────┬─────┘ └───┬────┘    │
                        │                   │            │         │
                        │              ┌────▼────┐  ┌────▼─────┐  │
                        │              │ChromaDB │  │Prometheus│  │
                        │              │Vector DB│  │  :9090   │  │
                        │              │ :8000   │  └────┬─────┘  │
                        │              └─────────┘  ┌────▼─────┐  │
                        │                           │ cAdvisor │  │
                        │                           │  :8080   │  │
                        │                           └──────────┘  │
                        └──────────────────────────────────────────┘
```

### 7 Containerized Services

| # | Service | Technology | Purpose |
|---|---------|-----------|---------|
| 1 | **API Backend** | FastAPI + Python 3.11 | AI agent, RAG pipeline, OCR, TTS, STT |
| 2 | **Frontend** | Next.js 15 + React | Modern web UI with real-time chat |
| 3 | **ChromaDB** | ChromaDB | Vector database storing 1,781 learning documents |
| 4 | **NGINX** | NGINX + Certbot | HTTPS termination, reverse proxy, rate limiting |
| 5 | **Prometheus** | Prometheus | Metrics collection and time-series storage |
| 6 | **Grafana** | Grafana | Live monitoring dashboard with 6 panels |
| 7 | **cAdvisor** | Google cAdvisor | Container-level CPU/memory/network metrics |

---

## ☁️ Cloud Computing Concepts Demonstrated

### 1. Compute Layer — Containerization
All services run in **isolated Docker containers** managed via Docker Compose. Multi-stage Dockerfiles minimize image size and enforce non-root execution for security.

### 2. Network Virtualization
A custom **bridge network** (`app-network`, subnet `172.28.0.0/16`) connects all services. Inter-service communication uses **DNS hostnames** (e.g., `api-backend:8000`), not hardcoded IPs. Only NGINX exposes ports externally.

### 3. Data Persistence
Three **named Docker volumes** ensure data survives container restarts:
- `chroma_data` — 1,781 learning documents
- `prometheus_data` — metrics history
- `grafana_data` — dashboard configurations

### 4. Resource Management
**All 7 services** have explicit CPU and memory limits:

| Service | CPU Limit | Memory Limit |
|---------|-----------|-------------|
| API Backend | 2.0 cores | 5 GB |
| Frontend | 1.0 cores | 2 GB |
| ChromaDB | 2.0 cores | 5 GB |
| NGINX | 0.5 cores | 256 MB |
| Prometheus | 0.5 cores | 512 MB |
| Grafana | 0.5 cores | 512 MB |
| cAdvisor | 0.5 cores | 256 MB |

### 5. High Availability (Option B)
- **Restart policy:** `restart: unless-stopped` on all services
- **Health checks:** HTTP-based health checks on backend, frontend, and ChromaDB
- **Dependency chain:** Frontend waits for backend health before starting
- **Self-healing:** Killed containers automatically restart within seconds

### 6. Cloud Deployment
Deployed on **Huawei Cloud Elastic Cloud Server (ECS)** with:
- Public IP: `159.138.84.175`
- Domain: `lang-agent-asser.duckdns.org`
- HTTPS via Let's Encrypt SSL certificates
- Container images stored in Huawei SWR (Container Registry)

### Bonus: Monitoring Dashboard ✅
Live Grafana dashboard at `/stats/` with CPU, memory, network I/O, and container status panels — auto-refreshing every 10 seconds.

### Bonus: Kubernetes ✅
Full K8s manifest set (8 files) in the `k8s/` directory for Minikube deployment with 2 backend replicas, Ingress routing, PersistentVolumeClaims, and readiness/liveness probes.

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Option 1: Docker Compose (Recommended)
```bash
# Clone the repository
git clone https://github.com/AsserAlmasry/AIE425_FinalProject_Group-23-.git
cd AIE425_FinalProject_Group-23-

# Create your .env file (see .env.example)
cp .env.example .env
# Edit .env with your API keys

# Deploy with the automation script
.\deploy.ps1 docker        # Windows
# or
bash deploy.sh docker      # Linux/Mac
```

### Option 2: Minikube (Kubernetes)
```bash
.\deploy.ps1 minikube
```

### Option 3: Huawei Cloud (Production)
```bash
.\deploy.ps1 huawei
# Then pull and run on your ECS instance
```

---

## 📁 Project Structure

```
lang_learning_agent/
├── api/                    # FastAPI backend
│   └── main.py             # API endpoints (chat, TTS, OCR, STT, email)
├── core/                   # AI agent core logic
│   ├── agent.py            # Main agent orchestrator
│   ├── classifier.py       # Intent classification
│   ├── rag.py              # RAG engine (ChromaDB retrieval)
│   └── tools.py            # 5 specialized tools (grammar, vocab, etc.)
├── frontend/               # Next.js 15 web application
│   └── src/app/
│       ├── page.tsx         # Main chat interface
│       └── components/     # UI components
├── data/                   # Knowledge base JSON files
│   ├── grammar_kb.json     # Grammar rules and examples
│   ├── vocabulary_kb.json  # Vocabulary with definitions
│   └── phrases_kb.json     # Common phrases and idioms
├── k8s/                    # Kubernetes manifests (8 files)
├── monitoring/             # Prometheus + Grafana configs
├── nginx/                  # NGINX reverse proxy config
├── docker-compose.yml      # Multi-container orchestration
├── Dockerfile.backend      # Backend multi-stage build
├── Dockerfile.frontend     # Frontend 3-stage build
├── deploy.ps1              # Windows deployment automation
└── deploy.sh               # Linux deployment automation
```

---

## 🔒 Security

- **API Authentication:** All endpoints protected with `X-API-Key` header validation
- **CORS:** Restricted to production domain only
- **CSP Headers:** Content-Security-Policy enforced via NGINX
- **Non-root containers:** Both backend and frontend run as unprivileged users
- **Rate Limiting:** 30 req/s per IP via NGINX
- **Input Validation:** Pydantic models with field constraints
- **Error Sanitization:** Internal errors logged server-side, generic messages returned to clients
- **SSH Hardening:** MaxAuthTries 3, OS packages fully patched

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 15, React, TypeScript, CSS |
| **Backend** | FastAPI, Python 3.11, Uvicorn |
| **AI/ML** | Groq (Llama 3.3 70B), OpenRouter, EasyOCR, gTTS, Whisper |
| **Database** | ChromaDB (vector store), HuggingFace Embeddings |
| **Proxy** | NGINX with SSL (Let's Encrypt) |
| **Monitoring** | Prometheus, Grafana, cAdvisor |
| **Containers** | Docker, Docker Compose |
| **Orchestration** | Kubernetes (Minikube) |
| **Cloud** | Huawei Cloud ECS, SWR, Security Groups |
| **CI/CD** | PowerShell/Bash deploy scripts |

---

## 👥 Team

**Powered by Asser Almasry | AI Engineer**

---

## 📄 License

This project was developed as part of the CSE 363 Cloud Computing course at Galala University.
