# Telos-Scale

**Autonomous AI Agent Platform for Massive Parallel Experimentation**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)

> **Simple algorithms + Massive scale → Exponential intelligence explosion**

Telos-Scale is an open-source platform where simple autonomous AI agents perform millions of experiments, learn from failures, and share discoveries—accelerating collective intelligence evolution through scale rather than complexity.

## 🌟 Core Philosophy

Our fundamental question: **"What if AIs could set their own goals, experiment autonomously, and share results—without waiting for human instruction?"**

Instead of complex algorithms with limited trials, Telos-Scale embraces:
- **Simplicity**: Core implementation under 300 lines
- **Scale**: Parallel execution and distributed sharing
- **Openness**: Community-driven knowledge evolution

## 🚀 Quick Start

### Prerequisites
- **Docker** 20.10+
- **Python** 3.11+
- **OpenRouter API Key** (or other LLM provider)

### Installation & Setup

```bash
# 1. Clone repository
git clone https://github.com/telos-scale/telos-scale.git
cd telos-scale

# 2. Run automatic setup
./setup.sh                 # On Windows: setup.bat

# 3. Configure API Key
# Open the generated .env file and add your key:
# OPENROUTER_API_KEY="sk-or-..."
```

### Your First Autonomous Run

```bash
# Start the autonomous loop with one click
./run.sh                   # On Windows: run.bat

# (Optional) Customize settings in config.yml
# Or use the CLI for advanced control:
telos-scale run --loops 100 --workers 5
```


## 📖 How It Works

Telos-Scale operates on a simple five-step loop:

1. **Context Retrieval**: Learn from recent local and shared experiments
2. **Goal Generation**: LLM proposes novel, achievable coding tasks
3. **Sandbox Execution**: Safe Docker environment runs the code
4. **Result Recording**: Store outcomes in local memory
5. **Optional Sharing**: Contribute discoveries to global knowledge base

### Example Autonomous Loop

```python
from telos_scale import TelosScale

agent = TelosScale()
result = agent.run_loop()

print(f"Goal: {result['goal']}")
print(f"Result: {result['result'][:200]}...")
```

## 🏗️ Architecture Overview

### Core Components

| Component | Purpose | Lines |
|-----------|---------|-------|
| **`TelosScale`** | Main orchestrator | <300 |
| **`DockerSandbox`** | Safe code execution | ~100 |
| **`LocalMemory`** | Recent trial storage | ~50 |
| **`LLMClient`** | LiteLLM wrapper | ~50 |
| **`SharedClient`** | Optional community sharing | ~40 |

### System Flow

```
User Command
    ↓
CLI Parser (cli.py)
    ↓
TelosScale Orchestrator (core.py)
    ├─ 1. Get Context (memory.py + shared.py)
    ├─ 2. Generate Goal (llm.py)
    ├─ 3. Execute in Sandbox (sandbox.py)
    ├─ 4. Record Results (memory.py)
    └─ 5. Share Discovery (shared.py)
```

## 🔧 Advanced Usage

### Configuration via Environment Variables

```bash
# LLM Configuration
export TELOS_MODEL="gemini/gemini-flash-latest"
export OPENROUTER_API_KEY="sk-or-..."

# Sandbox Settings
export TELOS_DOCKER_IMAGE="python:3.11-slim"
export TELOS_MEMORY_LIMIT="512m"
export TELOS_TIMEOUT="300"

# Sharing Options
export TELOS_SHARED_URL="https://api.telos.scale"
export TELOS_SHARE_ENABLED="true"

# Cost Management
export TELOS_COST_LIMIT="10.0"
export TELOS_DAILY_LOOPS="1000"
```

### Programmatic Integration

```python
from telos_scale import TelosScale

# Custom configuration
agent = TelosScale(
    shared_url="https://api.telos.scale",
    model="gemini/gemini-flash-latest",
    sandbox_image="python:3.11-slim",
    sandbox_memory_limit="1g",
)

# Batch execution
for i in range(1000):
    print(f"Loop {i+1}/1000")
    result = agent.run_loop()
    if "error" in result['result'].lower():
        print(f"  Failed: {result['goal'][:50]}...")
```

### CLI Reference

```bash
# Main commands
telos-scale run [--loops 10] [--workers 1] [--share]
telos-scale status                    # Show current status
telos-scale list                      # List past trials
telos-scale export --output results.json
telos-scale dashboard                 # Web dashboard (coming soon)
telos-scale demo                      # Quick demonstration

# Run options
--loops INTEGER       Number of autonomous loops (default: 10)
--workers INTEGER     Parallel workers (default: 1)
--model TEXT          LLM model (default: "gemini/gemini-flash-latest")
--share               Enable community sharing
--shared-url TEXT     Shared server URL
--verbose             Detailed logging
```

## 🌐 Community & Sharing

### Why Share?

When you enable sharing:
- Your discoveries help others avoid similar failures
- You benefit from thousands of experiments you didn't run
- Collective intelligence emerges from distributed learning

### Privacy & Security

- **Opt-in only**: Sharing disabled by default
- **Anonymous contributions**: User ID hashed, no personal data
- **Transparent protocols**: All APIs documented and open-source

### Shared Knowledge Protocol

```json
{
  "goal": "Create a Python script that scrapes Hacker News",
  "result": "Success: scraped 100 posts with error handling",
  "embedding": [0.12, -0.45, 0.78, ...],
  "metadata": {
    "model": "gemini/gemini-flash-latest",
    "tokens_used": 2200,
    "execution_time_ms": 4500,
    "cost_usd": 0.001175,
    "tags": ["web-scraping", "python", "success"]
  }
}
```

## 📊 Performance & Scaling

### Current Capabilities
- **Single node**: ~100 loops/hour (sequential)
- **Parallel**: ~500 loops/hour (5 workers)
- **Cost**: ~$0.001 per loop (Gemini Flash)

### Scaling Strategy
1. **Horizontal scaling**: Add more worker nodes
2. **Knowledge sharing**: Reduce redundant experiments
3. **Cost optimization**: Smart model selection

### Resource Management
- Docker container isolation per execution
- Real-time cost tracking and limits
- Automatic rate limiting for API providers

## 🧪 Testing & Validation

```bash
# Unit tests
pytest tests/ -v

# Integration tests (requires Docker)
pytest tests/integration/ -v

# Run a quick validation
python -m telos_scale.core  # Single loop test
```

## 🤝 Contributing

We welcome contributions! Telos-Scale thrives on community involvement:

1. **Report bugs** or suggest features via GitHub Issues
2. **Submit pull requests** for improvements
3. **Share your experiments** with the community
4. **Improve documentation** for new users

### Development Setup

```bash
# Clone with development dependencies
git clone https://github.com/telos-scale/telos-scale.git
cd telos-scale
pip install -e ".[dev]"
pre-commit install
```

### Code Standards
- **Simplicity first**: Avoid unnecessary complexity
- **Type hints**: Required for all public functions
- **Documentation**: Clear docstrings for public APIs
- **Tests**: Maintain >80% coverage

## 📈 Roadmap

### Phase 1: Core Implementation (v0.1) ✅
- [x] Under 300-line core orchestrator
- [x] Basic CLI interface
- [x] Docker sandbox safety
- [x] Local memory system

### Phase 2: Scaling & Sharing (v0.2) 🚧
- [ ] Parallel execution optimization
- [ ] Shared knowledge base
- [ ] Cost tracking dashboard
- [ ] Plugin system

### Phase 3: Community Platform (v0.3)
- [ ] Public shared server
- [ ] Contributor incentive program
- [ ] Advanced visualization tools
- [ ] Enterprise features

### Phase 4: Distributed Network (v1.0)
- [ ] Peer-to-peer knowledge exchange
- [ ] Cross-instance coordination
- [ ] Research institution integration
- [ ] Global experiment marketplace

## 🏆 Why Telos-Scale?

### For Developers
**"Low-cost AI research assistant that evolves with the community"**
- Run thousands of experiments for <$1/month
- Leverage collective discoveries
- Generate reusable code and tools

### For Researchers
**"Large-scale distributed experimentation platform"**
- Hypothesis testing at unprecedented scale
- Reproducible experimental environment
- Collaborative knowledge building

### For Organizations
**"Continuous AI evolution infrastructure"**
- Domain-specific agent training
- Secure internal knowledge sharing
- Competitive AI capability development

### For Humanity
**"Democratizing intelligence evolution"**
- Open, transparent AI advancement
- Reduced geographic/economic barriers
- Collective intelligence amplification

## 📚 Learn More

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**: Detailed system design
- **[Philosophy](docs/telos-scale-philosophy.md)**: Core beliefs and vision
- **[Design Doc](docs/telos-scale-default-design.md)**: Technical specifications

## 🔗 Links

- **GitHub**: [github.com/telos-scale/telos-scale](https://github.com/telos-scale/telos-scale)
- **Documentation**: [docs.telos.scale](https://docs.telos.scale)
- **Community**: [Discord](https://discord.gg/telos-scale)
- **Twitter**: [@telos_scale](https://twitter.com/telos_scale)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original Telos project contributors
- OpenRouter and LLM providers
- Docker container technology
- Our amazing community of contributors

---

**"Intelligence doesn't scale with algorithm complexity—it scales with experiment volume."**

Join us in building the platform for exponential intelligence evolution. 🚀