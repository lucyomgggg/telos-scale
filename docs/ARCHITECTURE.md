# Telos-Scale Architecture

**Version 0.1 - March 2026**

## Overview

Telos-Scale is an autonomous AI agent platform built on the principle that **intelligence scales with experiment volume, not algorithm complexity**. This document describes the system architecture, component design, data flows, and scaling strategies.

## Design Principles

1. **Simplicity First**: Core implementation under 300 lines
2. **Scale Over Complexity**: Horizontal scaling prioritized over vertical optimization
3. **Optional Sharing**: Privacy-preserving opt-in knowledge exchange
4. **Safety by Isolation**: Docker sandboxing for all code execution
5. **Cost Awareness**: Real-time tracking and limits for sustainable operation

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     User/Developer                          │
└───────────────────────┬─────────────────────────────────────┘
                        │ (CLI Commands)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    CLI Interface (cli.py)                   │
│  • Command parsing and validation                           │
│  • Configuration management                                 │
│  • Logging and output formatting                            │
└───────────────────────┬─────────────────────────────────────┘
                        │ (API Calls)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              TelosScale Orchestrator (core.py)              │
│  • Main loop coordination                                  │
│  • Context aggregation and goal generation                 │
│  • Result processing and recording                         │
│  • Cost tracking and resource management                   │
└─────────────────┬──────────────┬──────────────┬────────────┘
                  │              │              │
                  ▼              ▼              ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ Local Memory │  │   LLM Client │  │   Sandbox    │
    │  (memory.py) │  │    (llm.py)  │  │ (sandbox.py) │
    └──────────────┘  └──────────────┘  └──────────────┘
          │                  │                  │
          │                  ▼                  │
          │        ┌──────────────────┐        │
          │        │ External LLM API │        │
          │        │ (OpenRouter, etc)│        │
          │        └──────────────────┘        │
          │                                    ▼
          │                        ┌──────────────────┐
          │                        │ Docker Engine    │
          │                        │ (Containers)     │
          │                        └──────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                Optional: Shared Client                      │
│                (shared.py)                                  │
│  • Trial upload to community knowledge base                │
│  • Similarity search across shared experiments             │
└───────────────────────┬─────────────────────────────────────┘
                        │ (HTTPS)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                Telos-Scale Shared Server                    │
│                (Community Knowledge Base)                   │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. TelosScale Orchestrator (`core.py`)

**Purpose**: Main coordination engine that executes the autonomous loop.

**Key Responsibilities**:
- Manage the five-step execution cycle
- Coordinate between memory, LLM, and sandbox components
- Track costs and enforce limits
- Handle errors and retries

**Implementation Details**:
- Single class: `TelosScale`
- Target: Under 300 lines of code
- Thread-safe for parallel execution
- Configurable via environment variables

**Methods**:
- `run_loop()`: Execute single autonomous cycle
- `run(loops, workers)`: Execute multiple loops
- `_get_context()`: Retrieve relevant past trials
- `_generate_goal()`: Create new objective using LLM
- `_execute_goal()`: Run goal in sandbox
- `_record()`: Store results locally

### 2. Docker Sandbox (`sandbox.py`)

**Purpose**: Secure isolated environment for code execution.

**Design**:
- Uses Docker SDK for Python
- Each execution gets fresh container or reused container
- Memory and CPU limits configurable
- Timeout protection for long-running operations

**Safety Features**:
- No network access (configurable)
- Read-only filesystem except `/workspace`
- Memory and process limits
- Automatic cleanup after execution

**Methods**:
- `start()`: Initialize container
- `execute_command()`: Run command and capture output
- `read_file()/write_file()`: File operations in container
- `stop()`: Clean shutdown

### 3. Local Memory (`memory.py`)

**Purpose**: Store and retrieve recent trial history.

**Data Structure**:
```python
{
    "goal": str,
    "result": str,
    "timestamp": float,
    "metadata": Dict[str, Any]
}
```

**Implementation**:
- In-memory FIFO buffer (configurable size)
- Simple keyword search (v0.1)
- Future: Vector embeddings for semantic search

**Methods**:
- `add()`: Store new trial
- `get_recent()`: Retrieve N most recent trials
- `search()`: Basic keyword matching
- `clear()`: Reset memory

### 4. LLM Client (`llm.py`)

**Purpose**: Interface with language models via LiteLLM.

**Supported Providers**:
- OpenRouter (primary)
- OpenAI, Anthropic, Google (via LiteLLM)
- Local models (via Ollama, etc.)

**Features**:
- Consistent interface across providers
- **Multi-provider API keys**: Dynamically detects `DEEPSEEK_API_KEY`, `GEMINI_API_KEY`, etc.
- **Fail-fast design**: No dummy fallbacks on connection errors
- Cost estimation based on real pricing data
- Token counting via LiteLLM

**Methods**:
- `complete()`: Generate LLM response
- `estimate_cost()`: Calculate approximate cost
- `count_tokens()`: Estimate token usage

### 5. Shared Client (`shared.py`)

**Purpose**: Optional integration with community knowledge base.

**Protocol**:
- HTTPS REST API
- JSON payloads
- Bearer token authentication (optional)

**Endpoints**:
- `POST /api/upload`: Submit trial results
- `GET /api/search`: Query similar trials

**Privacy**:
- Anonymous user hashing
- Opt-in only (disabled by default)
- No personal data collection

### 6. CLI Interface (`cli.py`)

**Purpose**: User-friendly command-line interface.

**Commands**:
- `run`: Execute autonomous loops
- `status`: Show system status
- `list`: Display past trials
- `export`: Save results to file
- `dashboard`: Launch web UI (planned)
- `demo`: Quick demonstration

**Configuration**:
- Environment variable priority
- Command-line argument overrides
- Sensible defaults

## Data Flow

### Autonomous Loop Sequence

```
1. INITIALIZATION & SETUP
   ├─ Run `./setup.sh` (Check Docker, venv, deps)
   └─ Configure `.env` with provider-specific key

2. EXECUTION (./run.sh)
   ├─ Activate virtual environment
   └─ Launch `telos-scale run`

3. CONTEXT RETRIEVAL
   ├─ Retrieve N most recent local trials
   ├─ (Optional) Query shared knowledge base
   └─ Combine and format for LLM prompt

3. GOAL GENERATION
   ├─ Construct prompt with context
   ├─ Call LLM with temperature ~0.7
   ├─ Validate and sanitize response
   └─ Parse into executable goal

4. SANDBOX EXECUTION
   ├─ Start/attach Docker container
   ├─ Execute goal-specific commands
   ├─ Capture stdout/stderr
   ├─ Check exit codes
   └─ Clean up resources

5. RESULT PROCESSING
   ├─ Classify success/failure
   ├─ Extract key insights
   ├─ Calculate metrics (time, tokens, cost)
   └─ Generate structured result

6. STORAGE & SHARING
   ├─ Store in local memory
   ├─ (Optional) Upload to shared server
   └─ Update cost tracking

7. ITERATION
   └─ Repeat from step 2 or exit
```

### Data Formats

#### Trial Record
```json
{
  "id": "auto-generated-uuid",
  "goal": "Create a Python script that scrapes Hacker News",
  "result": "Success: Created script scraping 100 posts with error handling",
  "execution": {
    "exit_code": 0,
    "stdout": "...",
    "stderr": "",
    "duration_ms": 4500
  },
  "llm": {
    "model": "gemini/gemini-flash-latest",
    "prompt_tokens": 1200,
    "completion_tokens": 1000,
    "temperature": 0.7
  },
  "cost": {
    "llm_usd": 0.001175,
    "compute_usd": 0.000100,
    "total_usd": 0.001275
  },
  "metadata": {
    "tags": ["web-scraping", "python", "success"],
    "user_hash": "a1b2c3d4",
    "sandbox_image": "python:3.11-slim"
  },
  "timestamp": "2026-03-27T15:30:00Z"
}
```

#### Shared API Payload
```json
{
  "goal": "goal text",
  "result": "result text",
  "embedding": [0.1, -0.2, 0.3, ...],  // 384-dimensional
  "metadata": {
    "model": "gemini/gemini-flash-latest",
    "tokens_used": 2200,
    "execution_time_ms": 4500,
    "cost_usd": 0.001175,
    "tags": ["category1", "category2"]
  }
}
```

## Configuration System

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `DEEPSEEK_API_KEY` | DeepSeek API key | (Optional) |
| `GEMINI_API_KEY` | Google Gemini API key | (Optional) |
| `OPENROUTER_API_KEY` | OpenRouter (generic fallback) | (Optional) |
| `TELOS_MODEL` | Default LLM model | `"gemini/gemini-flash-latest"` |
| `TELOS_MAX_TOKENS` | Max tokens per LLM call | `8000` |
| `TELOS_DOCKER_IMAGE` | Sandbox container image | `"python:3.11-slim"` |
| `TELOS_MEMORY_LIMIT` | Container memory limit | `"512m"` |
| `TELOS_TIMEOUT` | Command timeout (seconds) | `300` |
| `TELOS_SHARED_URL` | Shared server URL | `"https://api.telos.scale"` |
| `TELOS_SHARE_ENABLED` | Enable sharing | `"false"` |
| `TELOS_COST_LIMIT` | Maximum cost (USD) | `10.0` |
| `TELOS_DAILY_LOOPS` | Daily loop limit | `1000` |

### Priority Order
1. Command-line arguments
2. Environment variables  
3. Configuration files (future)
4. Default values

## Concurrency Model

### Parallel Execution Architecture

```
Main Process (Coordinator)
├── Worker Process 1
│   ├── TelosScale Instance 1
│   ├── Independent memory
│   └── Dedicated sandbox
├── Worker Process 2
│   ├── TelosScale Instance 2
│   ├── Independent memory  
│   └── Dedicated sandbox
└── Shared State
    ├── Cost tracker (thread-safe)
    ├── Global configuration
    └── (Optional) Shared memory pool
```

### Implementation Options

**v0.1**: Sequential execution only
**v0.2**: `multiprocessing.Pool` with isolated workers
**v0.3**: Distributed workers via Redis/Celery
**v1.0**: Kubernetes/Docker Swarm orchestration

### Resource Management
- Docker container pooling
- LLM API rate limiting
- Cost-based throttling
- Memory usage monitoring

## Security Considerations

### Sandbox Isolation
- **Network**: No external access by default
- **Filesystem**: Read-only base, tmpfs for `/workspace`
- **Resources**: Memory, CPU, process limits
- **Time**: Execution timeout enforcement

### Data Privacy
- **Anonymous contributions**: Hashed user IDs
- **No PII collection**: Only experiment data
- **Opt-in sharing**: Explicit user consent required
- **Data retention**: Configurable retention periods

### API Security
- **HTTPS only**: All external communications
- **API key rotation**: Regular key updates
- **Rate limiting**: Per-user and global limits
- **Input validation**: Sanitize all external inputs

## Scaling Strategies

### Horizontal Scaling
1. **Add more workers**: Linear scaling within single node
2. **Multi-node clusters**: Distributed execution
3. **Geographic distribution**: Reduce latency, increase redundancy

### Knowledge Sharing Scaling
1. **Local memory**: Fast access to recent trials
2. **Shared server**: Global knowledge base
3. **Peer-to-peer**: Direct node-to-node exchange (future)
4. **Federated learning**: Privacy-preserving aggregation (future)

### Cost Optimization
1. **Model selection**: Automatic cost/performance balancing
2. **Caching**: Reuse similar LLM responses
3. **Batch processing**: Group similar operations
4. **Spot instances**: Cloud cost optimization

## Monitoring & Observability

### Metrics Collection
- **Execution metrics**: Success rate, duration, cost
- **Resource usage**: Memory, CPU, disk I/O
- **LLM metrics**: Token usage, latency, errors
- **Business metrics**: Experiments/day, unique users

### Logging Strategy
- **Structured logging**: JSON format for machine parsing
- **Multiple levels**: DEBUG, INFO, WARNING, ERROR
- **Context preservation**: Correlation IDs across components
- **Log aggregation**: Centralized collection and analysis

### Health Checks
- **Component health**: Sandbox, LLM, memory, network
- **Dependency checks**: Docker, API connectivity
- **Resource alerts**: Cost thresholds, rate limits
- **Automated recovery**: Self-healing mechanisms

## Deployment Architecture

### Development Environment
```
Local Machine
├── Python virtual environment
├── Docker Desktop
├── Local configuration
└── Direct API access
```

### Production Deployment (Single Node)
```
Cloud VM / Bare Metal
├── Docker Engine
├── Python 3.11+
├── Systemd service
├── Log rotation
└── Backup configuration
```

### Production Deployment (Cluster)
```
Kubernetes Cluster
├── TelosScale Deployment
├── Redis for shared state
├── PostgreSQL for persistence
├── Prometheus for monitoring
└── NGINX ingress controller
```

### Shared Server Deployment
```
Microservices Architecture
├── API Gateway (FastAPI)
├── Vector Database (Qdrant/Pinecone)
├── Relational DB (PostgreSQL)
├── Cache Layer (Redis)
├── Object Storage (S3)
└── Message Queue (RabbitMQ)
```

## Extension Points

### Plugin System (Planned)
1. **Custom goal generators**: Domain-specific objective creation
2. **Alternative sandboxes**: Different isolation technologies
3. **Specialized memory**: Vector databases, SQL backends
4. **Custom evaluators**: Domain-specific success criteria

### Integration Hooks
- **Webhook notifications**: Notify external systems
- **Export formats**: CSV, JSON, Parquet, etc.
- **Dashboard plugins**: Custom visualizations
- **API extensions**: Additional endpoints

### Custom Execution Environments
- **Language support**: Python, JavaScript, Rust, etc.
- **Framework integration**: Jupyter, VS Code, etc.
- **Hardware acceleration**: GPU, TPU support
- **Specialized hardware**: Robotics, lab equipment

## Performance Characteristics

### Current (v0.1) Benchmarks
| Metric | Value | Notes |
|--------|-------|-------|
| Loop duration | 5-30 seconds | Depends on LLM latency |
| Success rate | ~70% | Simple coding tasks |
| Cost per loop | ~$0.001 | Gemini Flash model |
| Memory usage | ~500 MB/worker | Includes Docker overhead |
| Max parallelism | 5 workers/core | Limited by Docker/LLM |

### Scaling Projections
| Workers | Loops/Hour | Cost/Hour | Notes |
|---------|------------|-----------|-------|
| 1 | 120 | $0.12 | Sequential execution |
| 5 | 500 | $0.50 | Single node optimal |
| 20 | 1,800 | $1.80 | Multi-node cluster |
| 100 | 8,000 | $8.00 | Large-scale deployment |

### Bottleneck Analysis
1. **LLM latency**: Primary bottleneck (200-2000ms)
2. **Docker startup**: Secondary bottleneck (100-500ms)
3. **Network I/O**: Minimal impact with local Docker
4. **Memory bandwidth**: Not significant at current scale

## Failure Modes & Recovery

### Common Failures
1. **LLM API failures**: Rate limits, downtime, authentication
2. **Docker issues**: Daemon down, resource exhaustion
3. **Network problems**: Connectivity loss, latency spikes
4. **Resource exhaustion**: Memory, disk space, cost limits

### Recovery Strategies
- **Exponential backoff**: For transient API failures
- **Circuit breakers**: Prevent cascading failures
- **Graceful degradation**: Fallback to simpler operations
- **Checkpoint/restart**: Resume from last successful state

### Disaster Recovery
- **Regular backups**: Configuration and important data
- **Multi-region deployment**: Geographic redundancy
- **Data replication**: Across availability zones
- **Incident response**: Playbooks and automation

## Future Architecture Directions

### Short-term (v0.2-v0.3)
- **Vector search**: Semantic similarity for context retrieval
- **Advanced sandboxing**: gVisor, Firecracker, WASM
- **Plugin system**: Extensible architecture
- **Enhanced monitoring**: Real-time dashboards

### Medium-term (v0.4-v0.7)
- **Federated learning**: Privacy-preserving knowledge sharing
- **Multi-modal agents**: Image, audio, video processing
- **Hardware integration**: Robotics, lab equipment, IoT
- **Marketplace**: Experiment and model marketplace

### Long-term (v1.0+)
- **Autonomous research**: Self-directed scientific discovery
- **Cross-domain transfer**: Knowledge application across fields
- **Collective intelligence**: Emergent behaviors from mass interaction
- **Democratized AI**: Accessible to non-technical users

## Appendix

### Technology Stack
- **Language**: Python 3.11+
- **Containerization**: Docker
- **LLM Interface**: LiteLLM
- **Networking**: Requests, HTTPX
- **Concurrency**: Multiprocessing, asyncio (future)
- **Monitoring**: Prometheus, Grafana (planned)

### Dependencies
```txt
Core: docker, litellm, requests
Development: pytest, black, mypy, pre-commit
Optional: redis, postgresql, qdrant-client
```

### File Structure
```
telos-scale/
├── core.py              # Main orchestrator
├── cli.py               # Command-line interface
├── sandbox.py           # Docker execution environment
├── memory.py            # Local trial storage
├── llm.py               # LLM client wrapper
├── shared.py            # Community sharing client
├── utils.py             # Shared utilities
├── requirements.txt     # Python dependencies
├── Dockerfile.sandbox   # Sandbox container definition
├── docker-compose.yml   # Development environment
├── README.md            # Project overview
├── ARCHITECTURE.md      # This document
├── telos-scale-*.md     # Design documents
├── examples/            # Usage examples
├── tests/               # Test suite
└── telos_scale/         # Python package
```

### Related Documents
- [Philosophy](telos-scale-philosophy.md): Core beliefs and vision
- [Design Document](telos-scale-default-design.md): Detailed specifications
- [README.md](README.md): Quick start and user guide
- [Contributing Guide](CONTRIBUTING.md): Development instructions

---

*Last updated: March 2026 (v0.1)*  
*Architecture version: 1.0*  
*Maintainer: Telos-Scale Core Team*