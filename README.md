# DA-BOT: AI Agent Platform

A sophisticated AI agent platform with multiple phases of development, featuring safety controls, guardrails, and autonomous operation capabilities.

## Project Overview

This platform is designed to be built in phases, starting with a solid foundation and progressively adding more advanced features. See `overview/project_overview.txt` for the complete roadmap.

## Current Status

- ✅ **Phase 0**: Ground rules & success criteria
- 🚧 **Phase 1**: Skeleton platform (in progress)
- ⏳ **Phase 2**: Perception + Operator
- ⏳ **Phase 3**: Memory management
- ⏳ **Phase 4**: Planning loop with guardrails
- ⏳ **Phase 5**: First end-to-end workflow
- ⏳ **Phase 6**: Browser micro-agent
- ⏳ **Phase 7**: Autonomy hardening
- ⏳ **Phase 8**: Safety & containment
- ⏳ **Phase 9**: "Runs itself" certification
- ⏳ **Phase 10**: Evolution hooks

## Quick Start

### 1. Test GPT-OSS-20B Model
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test the model
python tests/unit/test_gpt_oss.py
```

### 2. Run the AI Agent Platform
```bash
# Run with a goal
python main.py --goal "check this computer's window resolution" --debug

# Run with retry logic
python main.py --goal "your goal here" --retries 3

# Run in dev mode (bypasses safety)
DISABLE_KILLSWITCH=1 python main.py --goal "your goal here" --debug
```

### 3. Control the System
```bash
# Stop the system
./bin/stop

# Pause the system
./bin/pause

# Toggle dry-run mode
./bin/dryrun on
./bin/dryrun off
```

## Directory Structure

```
DA-BOT/
├── config/                 # Configuration files
│   ├── policies.yml       # Safety policies and limits
│   ├── mode.json         # Runtime mode settings
│   └── agent_prompts.yml # Agent system prompts
├── control/               # Control files (runtime)
│   └── .gitkeep
├── runtime/               # Runtime state and artifacts
│   ├── goals.json        # Goal tracking
│   ├── plans.json        # Plan storage
│   ├── memory.json       # Memory entries
│   ├── important_memory.json # Persistent memory
│   └── run_state.json    # Current state
├── artifacts/             # Generated artifacts
│   ├── quarantine/        # Downloaded files
│   ├── screenshots/       # UI screenshots
│   └── logs/             # System logs
├── bin/                   # Control scripts
│   ├── stop              # Emergency stop
│   ├── pause             # Pause system
│   └── dryrun            # Toggle dry-run mode
├── tools/                 # Core system components
│   ├── agents/           # Base agent classes
│   │   ├── base_agent.py # Abstract base agent
│   │   └── gpt_oss_agent.py # GPT-OSS-20B agent
│   ├── memory/           # Memory system
│   │   └── memory.py     # Goals, plans, memory management
│   ├── models/           # Model management
│   │   └── model_manager.py # Singleton model manager
│   ├── safety/           # Safety and failsafes
│   │   └── failsafes.py  # Killswitch, budget limits
│   ├── overseer/         # Main coordination system
│   │   ├── overseer.py   # Main overseer class
│   │   └── overseer_agent.py # Planning agent
│   ├── perception/       # Vision and analysis
│   │   └── perception_agent.py # Screenshot analysis
│   ├── operator/         # Action execution
│   │   └── operator_agent.py # Mouse, keyboard, navigation
│   ├── router/           # Tool routing and safety
│   └── utils/            # Utilities
│       └── redact.py     # Safe logging utilities
├── agents/                # Agent interface (imports from tools/)
│   └── __init__.py       # Agent exports
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   │   ├── test_gpt_oss.py
│   │   ├── test_memory_system.py
│   │   ├── test_model_manager.py
│   │   └── test_*.py     # Other unit tests
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
├── docs/                  # Documentation
│   ├── api/              # API documentation
│   ├── deployment/       # Deployment guides
│   └── user_guide/       # User documentation
├── overview/              # Project overview and roadmap
├── main.py               # Main entry point
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Architecture

The platform is built with a modular architecture:

### Core Components (`tools/`)
- **Memory System** (`tools/memory/`): Goals, plans, and persistent memory management
- **Model Manager** (`tools/models/`): Singleton pattern for LLM model management
- **Safety System** (`tools/safety/`): Killswitch, budget limits, and failsafes
- **Base Agents** (`tools/agents/`): Abstract base classes and GPT-OSS-20B integration

### Specialized Agents (`tools/`)
- **Overseer** (`tools/overseer/`): Main coordination and planning
- **Perception** (`tools/perception/`): Screenshot analysis and UI detection
- **Operator** (`tools/operator/`): Action execution (mouse, keyboard, navigation)
- **Router** (`tools/router/`): Tool routing and safety validation

### Agent Interface (`agents/`)
The `agents/` package provides a clean interface that imports from the `tools/` implementations, maintaining backward compatibility.

## Safety Features

- **Killswitch**: Instant stop via `control/killswitch.on`
- **Pause**: Graceful pause via `control/pause.on`
- **Dry-run mode**: Safe testing without real actions
- **Budget limits**: Time, steps, and resource constraints
- **Scope gates**: Restricted file system and network access
- **Loop detection**: Prevents infinite loops
- **Circuit breakers**: Automatic failure handling
- **Dev mode**: `DISABLE_KILLSWITCH=1` for development

## Development

This project follows a phased development approach with each phase building upon the previous one. Each phase includes specific safety controls and acceptance criteria.

## License

[Add your license here]
