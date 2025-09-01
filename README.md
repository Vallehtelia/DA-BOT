# DA-BOT: AI Agent Platform

A sophisticated AI agent platform with multiple phases of development, featuring safety controls, guardrails, and autonomous operation capabilities. The ultimate goal is to create a system that can operate a computer completely unattended, develop itself by writing and testing new functionalities and agents, and continuously improve its own code through self-modification and learning.

## Project Overview

DA-BOT is a sophisticated AI agent platform designed for autonomous task execution with comprehensive safety controls and guardrails. The platform uses GPT-OSS-20B for intelligent planning and decision-making, while maintaining strict safety boundaries through multiple layers of protection.

### **🎯 Core Philosophy**
- **Safety First**: Every component includes failsafes, budget limits, and kill switches
- **Modular Design**: Clean separation of concerns with pluggable agents
- **Phased Development**: Incremental complexity with validation at each step
- **Real-World Ready**: Built for actual task automation, not just demos
- **Self-Improving**: Designed to evolve, learn, and enhance its own capabilities
- **Autonomous Operation**: Ultimate goal of complete unattended computer operation

### **🧠 AI-Powered Intelligence**
- **GPT-OSS-20B Integration**: OpenAI's open-weight model for reasoning and planning
- **Harmony Response Format**: Structured JSON responses for reliable parsing
- **Configurable Reasoning**: Low/Medium/High reasoning levels for different tasks
- **Context-Aware**: Rich context injection for better decision making

### **🛡️ Multi-Layer Safety System**
- **Killswitch**: Instant stop via file-based controls
- **Budget Limits**: Time, steps, screenshots, and request constraints
- **Scope Gates**: Restricted file system and network access
- **Loop Detection**: Prevents infinite loops and stuck states
- **Circuit Breakers**: Automatic failure handling and recovery
- **Dev Mode**: Override safety for development and testing

### **🏗️ Architecture Highlights**
- **Memory System**: Persistent storage of goals, plans, and important information
- **Agent Coordination**: Overseer orchestrates perception → planning → operation workflow
- **Model Management**: Singleton pattern prevents multiple model loading
- **Atomic Checkpointing**: Crash-safe state persistence and recovery
- **Safe Logging**: Automatic redaction of sensitive information

### **🚀 Long-Term Vision**
- **Complete Autonomy**: Operate computers without human intervention
- **Self-Development**: Write, test, and deploy new agents and functionalities
- **Code Evolution**: Improve its own codebase through analysis and modification
- **Learning System**: Continuously learn from successes and failures
- **Adaptive Intelligence**: Evolve capabilities based on encountered challenges
- **Self-Monitoring**: Maintain and upgrade its own systems and safety mechanisms

## Current Status

- ✅ **Phase 0**: Ground rules & success criteria
- ✅ **Phase 1**: Skeleton platform (COMPLETED)
  - ✅ Core memory system with goals, plans, and checkpoints
  - ✅ Comprehensive failsafe system (killswitch, pause, budget limits)
  - ✅ Base agent architecture with GPT-OSS-20B integration
  - ✅ Overseer coordination system
  - ✅ Perception, Operator, and Router agents (simulated)
  - ✅ Configuration management and control scripts
  - ✅ JSON validation and error handling
  - ✅ Model manager with singleton pattern
  - ✅ Safe logging with sensitive data redaction
- 🚧 **Phase 2**: Perception + Operator (in progress)
  - ✅ Agent implementations with LLM integration
  - ⏳ Real screenshot capture and UI analysis
  - ⏳ Actual mouse/keyboard input simulation
- ⏳ **Phase 3**: Memory management (partially complete)
  - ✅ Basic memory system implemented
  - ✅ Important memory with persistence
  - ⏳ Advanced memory optimization and token limits
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

## Current Capabilities

### ✅ **What's Working Now**
- **AI-Powered Planning**: GPT-OSS-20B generates intelligent, goal-specific plans
- **Memory System**: Persistent storage of goals, plans, and important information
- **Safety Controls**: Killswitch, pause, budget limits, and failsafe systems
- **Agent Coordination**: Overseer orchestrates perception → planning → operation workflow
- **JSON Validation**: Robust parsing and validation of LLM responses
- **Model Management**: Singleton pattern prevents multiple model loading
- **Debug Mode**: Comprehensive logging with sensitive data redaction
- **Retry Logic**: Configurable retry attempts for goal execution
- **Checkpointing**: Atomic state saves and recovery

### 🚧 **Currently Simulated**
- **Screenshot Analysis**: Perception agent simulates UI element detection
- **Input Actions**: Operator agent simulates mouse/keyboard operations
- **Real UI Interaction**: Actual screenshot capture and input simulation pending

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

## Recent Improvements

### **🔧 Latest Fixes & Enhancements**
- **JSON Validation**: Fixed type errors and improved dict/string handling
- **Plan Generation**: AI now creates goal-specific plans instead of generic fallbacks
- **Memory System**: Enhanced with important memory persistence and context injection
- **Debug Logging**: Safe redaction of sensitive information (passwords, keys, emails)
- **Agent Context**: Rich context injection for better decision making
- **Error Handling**: Robust retry logic and graceful failure recovery
- **Project Structure**: Reorganized into logical `tools/` subfolders
- **Import Paths**: Updated all imports for new structure
- **Git Ignore**: Added runtime files to prevent accidental commits

### **🎯 Key Features Working**
- **Intelligent Planning**: GPT-OSS-20B generates structured, actionable plans
- **Memory Persistence**: Important information saved across sessions
- **Safety First**: Comprehensive failsafe system from day one
- **Modular Design**: Clean separation of concerns and easy extensibility
- **Developer Friendly**: Debug mode, dev killswitch override, comprehensive logging

## Technical Architecture

### **🏗️ Design Principles**
- **Modular Architecture**: Each component has a single responsibility
- **Safety by Design**: Failsafes integrated at every level
- **Extensibility**: Easy to add new agents and capabilities
- **Observability**: Comprehensive logging and monitoring
- **Testability**: Unit tests, integration tests, and end-to-end validation

### **🔄 Execution Flow**
1. **Goal Setting**: User provides high-level objective
2. **Planning**: Overseer creates detailed step-by-step plan
3. **Execution**: Perception → Planning → Operation → Validation loop
4. **Memory**: Important information persisted across sessions
5. **Safety**: Continuous monitoring and failsafe activation

### **🧩 Component Interaction**
```
User Goal → Overseer → Plan Creation → Step Execution
    ↓           ↓           ↓              ↓
Memory ← Context ← Agents ← Validation ← Safety
    ↓           ↓           ↓              ↓
Persistence ← Logging ← Monitoring ← Failsafes
```

## Development

This project follows a phased development approach with each phase building upon the previous one. Each phase includes specific safety controls and acceptance criteria.

## Development Roadmap

### **Phase 0: Ground Rules & Success Criteria** ✅
- **Policy Framework**: Budget limits, allowlists, and safety thresholds
- **Control System**: Killswitch, pause, and dry-run modes
- **Stop Conditions**: Success criteria, budget exceeded, or killswitch activated

### **Phase 1: Skeleton Platform** ✅ **COMPLETED**
- **Core Systems**: Memory, failsafes, base agents, and overseer
- **Safety Integration**: Signal handlers, budget enforcement, and heartbeat monitoring
- **Agent Architecture**: GPT-OSS-20B integration with JSON validation
- **Configuration**: Policies, modes, and agent prompts
- **Control Scripts**: Emergency stop, pause, and dry-run toggles

### **Phase 2: Perception + Operator** 🚧 **IN PROGRESS**
- **Real UI Interaction**: Actual screenshot capture and input simulation
- **Confidence Gates**: Perception threshold validation and re-scan requests
- **Loop Detection**: Tool signature tracking and automatic replanning
- **Pixel-Diff Guards**: Change detection after actions

### **Phase 3: Memory Management** ⏳ **PARTIALLY COMPLETE**
- **Token-Aware Memory**: Intelligent memory optimization and compression
- **Redaction Filters**: Automatic removal of secrets and sensitive data
- **Crash-Safe Rollover**: Memory rotation and cleanup
- **Rate Limiting**: Prevent runaway disk usage

### **Phase 4: Planning Loop with Guardrails** ⏳
- **Critic Agent**: Loop detection, scope validation, and prerequisite checking
- **Circuit Breakers**: Per-tool failure tracking and automatic recovery
- **Rollback Hooks**: Browser back, file cleanup, and state restoration
- **Advanced Planning**: Multi-step validation and risk assessment

### **Phase 5: First End-to-End Workflow** ⏳
- **Dry-Run Mode**: Complete workflow testing without real actions
- **Approval Gates**: File-based approval system for sensitive operations
- **Workflow Validation**: End-to-end task completion testing
- **Error Recovery**: Graceful handling of workflow failures

### **Phase 6: Browser Micro-Agent** ⏳
- **Web Browsing**: Full browser automation with safety controls
- **Network Allowlists**: Domain-based access control
- **Popup Handling**: Automatic consent and banner management
- **Content Analysis**: Web page understanding and interaction

### **Phase 7: Autonomy Hardening** ⏳
- **Self-Healing**: Automatic recovery from stuck states
- **Timeline Viewer**: Visual debugging and monitoring interface
- **StuckCard System**: Compact state snapshots for analysis
- **Observability**: Comprehensive logging and monitoring

### **Phase 8: Safety & Containment** ⏳
- **Isolation**: Least-privilege execution and sandboxing
- **Secrets Management**: Secure credential handling and vaulting
- **Quarantine System**: Safe file handling and provenance tracking
- **Container Support**: Optional Docker-based isolation

### **Phase 9: "Runs Itself" Certification** ⏳
- **Safety Regression Suite**: Comprehensive guardrail testing
- **Autonomous Operation**: Unattended task execution validation
- **Performance Benchmarks**: Success rate and efficiency metrics
- **Certification Process**: Formal validation of autonomous capabilities

### **Phase 10: Evolution Hooks** ⏳
- **Plugin System**: Dynamic agent registration and management
- **Shadow Mode**: Safe testing of new agents alongside existing ones
- **Upgrade Policy**: Gradual rollout with rollback capabilities
- **Golden Tests**: Validation suite for new agent registration

### **Next Immediate Steps**
1. **Real UI Interaction**: Replace simulated actions with actual screenshot capture and input simulation
2. **Browser Integration**: Add web browsing capabilities with safety controls
3. **Advanced Memory**: Implement token-aware memory management and optimization
4. **Circuit Breakers**: Add failure detection and automatic recovery mechanisms
5. **End-to-End Workflows**: Complete real-world task automation testing

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses

This project uses the following third-party components:

- **GPT-OSS-20B Model**: Licensed under Apache 2.0 by OpenAI
- **Hugging Face Transformers**: Licensed under Apache 2.0
- **PyTorch**: Licensed under BSD-3-Clause
- **Other dependencies**: See `requirements.txt` for individual package licenses

### Usage Rights

- ✅ **Commercial use**: Allowed
- ✅ **Modification**: Allowed  
- ✅ **Distribution**: Allowed
- ✅ **Private use**: Allowed
- ⚠️ **Liability**: No warranty provided
- ⚠️ **Patent use**: Subject to Apache 2.0 terms

For the full license text, see the [LICENSE].
