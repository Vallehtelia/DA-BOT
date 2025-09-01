"""
Core memory system for the AI agent platform.
Handles goals, plans, runtime state, and checkpointing.
"""

import json
import time
import hashlib
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

@dataclass
class Goal:
    """Represents a goal to be accomplished."""
    id: str
    description: str
    created_at: float
    status: str  # "pending", "in_progress", "complete", "failed"
    priority: int = 1
    metadata: Dict[str, Any] = None

@dataclass
class Plan:
    """Represents a plan to achieve a goal."""
    id: str
    goal_id: str
    steps: List[Any]  # Can be strings or dictionaries
    current_step: int = 0
    status: str = "pending"  # "pending", "executing", "complete", "failed"
    created_at: float = None
    updated_at: float = None

@dataclass
class MemoryEntry:
    """Represents a memory entry for the system."""
    id: str
    timestamp: float
    agent: str
    action: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    success: bool
    metadata: Dict[str, Any] = None

@dataclass
class ImportantMemory:
    """Represents important information that should be permanently remembered."""
    id: str
    timestamp: float
    agent: str
    action: str
    important_info: List[str]
    description: str
    priority: str  # "high", "medium", "low"
    context: Dict[str, Any] = None
    tags: List[str] = None

class Memory:
    """Core memory system for the AI agent platform."""
    
    def __init__(self, base_path: str = "runtime"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        
        # Initialize storage paths
        self.goals_path = self.base_path / "goals.json"
        self.plans_path = self.base_path / "plans.json"
        self.memory_path = self.base_path / "memory.json"
        self.important_memory_path = self.base_path / "important_memory.json"
        self.state_path = self.base_path / "run_state.json"
        
        # In-memory storage
        self.goals: Dict[str, Goal] = {}
        self.plans: Dict[str, Plan] = {}
        self.memory: List[MemoryEntry] = []
        self.important_memory: List[ImportantMemory] = []
        self.current_state: Dict[str, Any] = {}
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load existing data
        self._load_data()
    
    def _load_data(self):
        """Load existing data from disk."""
        try:
            if self.goals_path.exists():
                with open(self.goals_path, 'r') as f:
                    goals_data = json.load(f)
                    self.goals = {k: Goal(**v) for k, v in goals_data.items()}
            
            if self.plans_path.exists():
                with open(self.plans_path, 'r') as f:
                    plans_data = json.load(f)
                    self.plans = {k: Plan(**v) for k, v in plans_data.items()}
            
            if self.memory_path.exists():
                with open(self.memory_path, 'r') as f:
                    memory_data = json.load(f)
                    self.memory = [MemoryEntry(**entry) for entry in memory_data]
            
            if self.state_path.exists():
                with open(self.state_path, 'r') as f:
                    self.current_state = json.load(f)
            
            if self.important_memory_path.exists():
                with open(self.important_memory_path, 'r') as f:
                    important_memory_data = json.load(f)
                    self.important_memory = [ImportantMemory(**entry) for entry in important_memory_data]
                    
        except Exception as e:
            self.logger.warning(f"Failed to load existing data: {e}")
    
    def _save_data(self):
        """Save data to disk."""
        try:
            # Save goals
            with open(self.goals_path, 'w') as f:
                goals_data = {k: asdict(v) for k, v in self.goals.items()}
                json.dump(goals_data, f, indent=2)
            
            # Save plans
            with open(self.plans_path, 'w') as f:
                plans_data = {k: asdict(v) for k, v in self.plans.items()}
                json.dump(plans_data, f, indent=2)
            
            # Save memory (keep only last 1000 entries)
            with open(self.memory_path, 'w') as f:
                recent_memory = self.memory[-1000:] if len(self.memory) > 1000 else self.memory
                memory_data = [asdict(entry) for entry in recent_memory]
                json.dump(memory_data, f, indent=2)
            
            # Save current state
            with open(self.state_path, 'w') as f:
                json.dump(self.current_state, f, indent=2)
            
            # Save important memory
            with open(self.important_memory_path, 'w') as f:
                important_memory_data = [asdict(entry) for entry in self.important_memory]
                json.dump(important_memory_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save data: {e}")
    
    def add_goal(self, description: str, priority: int = 1) -> str:
        """Add a new goal."""
        goal_id = hashlib.md5(f"{description}{time.time()}".encode()).hexdigest()[:8]
        goal = Goal(
            id=goal_id,
            description=description,
            created_at=time.time(),
            status="pending",
            priority=priority,
            metadata={}
        )
        self.goals[goal_id] = goal
        self._save_data()
        self.logger.info(f"Added goal: {goal_id} - {description}")
        return goal_id
    
    def get_goal(self, goal_id: str) -> Optional[Goal]:
        """Get a goal by ID."""
        return self.goals.get(goal_id)
    
    def update_goal_status(self, goal_id: str, status: str):
        """Update goal status."""
        if goal_id in self.goals:
            self.goals[goal_id].status = status
            self._save_data()
            self.logger.info(f"Updated goal {goal_id} status to: {status}")
    
    def create_plan(self, goal_id: str, steps: List[str]) -> str:
        """Create a plan for a goal."""
        plan_id = hashlib.md5(f"{goal_id}{time.time()}".encode()).hexdigest()[:8]
        plan = Plan(
            id=plan_id,
            goal_id=goal_id,
            steps=steps,
            created_at=time.time(),
            updated_at=time.time()
        )
        self.plans[plan_id] = plan
        self._save_data()
        self.logger.info(f"Created plan: {plan_id} for goal: {goal_id}")
        return plan_id
    
    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Get a plan by ID."""
        return self.plans.get(plan_id)
    
    def update_plan_step(self, plan_id: str, current_step: int, status: str = None):
        """Update plan progress."""
        if plan_id in self.plans:
            self.plans[plan_id].current_step = current_step
            if status:
                self.plans[plan_id].status = status
            self.plans[plan_id].updated_at = time.time()
            self._save_data()
    
    def add_memory_entry(self, agent: str, action: str, input_data: Dict[str, Any], 
                        output_data: Dict[str, Any], success: bool, metadata: Dict[str, Any] = None):
        """Add a memory entry."""
        entry = MemoryEntry(
            id=hashlib.md5(f"{agent}{action}{time.time()}".encode()).hexdigest()[:8],
            timestamp=time.time(),
            agent=agent,
            action=action,
            input_data=input_data,
            output_data=output_data,
            success=success,
            metadata=metadata or {}
        )
        self.memory.append(entry)
        self._save_data()
        self.logger.info(f"Added memory entry: {entry.id} from {agent}")
    
    def get_recent_memory(self, limit: int = 100) -> List[MemoryEntry]:
        """Get recent memory entries."""
        return self.memory[-limit:] if len(self.memory) > limit else self.memory
    
    def add_important_memory(self, agent: str, action: str, important_info: List[str], 
                            description: str, priority: str = "medium", context: Dict[str, Any] = None,
                            tags: List[str] = None) -> str:
        """Add important information to permanent memory."""
        entry = ImportantMemory(
            id=hashlib.md5(f"{agent}{action}{time.time()}".encode()).hexdigest()[:8],
            timestamp=time.time(),
            agent=agent,
            action=action,
            important_info=important_info,
            description=description,
            priority=priority,
            context=context or {},
            tags=tags or []
        )
        self.important_memory.append(entry)
        self._save_data()
        self.logger.info(f"Added important memory: {entry.id} - {description} (priority: {priority})")
        return entry.id
    
    def get_important_memory(self, tags: List[str] = None, priority: str = None, 
                           limit: int = 100) -> List[ImportantMemory]:
        """Get important memory entries with optional filtering."""
        results = self.important_memory
        
        # Filter by tags if specified
        if tags:
            results = [entry for entry in results if any(tag in entry.tags for tag in tags)]
        
        # Filter by priority if specified
        if priority:
            results = [entry for entry in results if entry.priority == priority]
        
        # Return limited results
        return results[-limit:] if len(results) > limit else results
    
    def search_important_memory(self, query: str) -> List[ImportantMemory]:
        """Search important memory by description or tags."""
        query_lower = query.lower()
        results = []
        
        for entry in self.important_memory:
            # Search in description
            if query_lower in entry.description.lower():
                results.append(entry)
                continue
            
            # Search in tags
            if any(query_lower in tag.lower() for tag in entry.tags):
                results.append(entry)
                continue
            
            # Search in important_info
            if any(query_lower in info.lower() for info in entry.important_info):
                results.append(entry)
                continue
        
        return results
    
    def process_agent_response_for_memory(self, agent: str, action: str, response: Dict[str, Any]) -> bool:
        """Process agent response and extract memory information if present."""
        if not isinstance(response, dict):
            return False
        
        memory_data = response.get("memory")
        if not memory_data:
            return False
        
        try:
            # Extract memory fields
            important_info = memory_data.get("important_info", [])
            description = memory_data.get("description", "")
            priority = memory_data.get("priority", "medium")
            
            # Validate required fields
            if not important_info or not description:
                self.logger.warning(f"Invalid memory data from {agent}: missing required fields")
                return False
            
            # Add to important memory
            self.add_important_memory(
                agent=agent,
                action=action,
                important_info=important_info,
                description=description,
                priority=priority,
                context={"response": response},
                tags=[]  # Do NOT set important_info as tags to prevent secret leakage
            )
            
            self.logger.info(f"Processed memory from {agent}: {description}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to process memory from {agent}: {e}")
            return False
    
    def get_memory_context_for_agent(self, agent: str, action: str, query: str = None) -> Dict[str, Any]:
        """Get relevant memory context for an agent's action."""
        context = {
            "recent_important_memory": [],
            "relevant_memory": [],
            "total_memory_count": len(self.important_memory)
        }
        
        # Get recent high-priority memory
        high_priority = self.get_important_memory(priority="high", limit=5)
        context["recent_important_memory"] = [asdict(entry) for entry in high_priority]
        
        # Search for relevant memory if query provided
        if query:
            relevant = self.search_important_memory(query)
            context["relevant_memory"] = [asdict(entry) for entry in relevant[:10]]
        
        return context
    
    def update_state(self, key: str, value: Any):
        """Update current runtime state."""
        self.current_state[key] = value
        self.current_state["last_updated"] = time.time()
        self._save_data()
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get current runtime state value."""
        return self.current_state.get(key, default)
    
    def checkpoint(self):
        """Create a checkpoint of current state."""
        checkpoint_path = self.base_path / f"checkpoint_{int(time.time())}.json"
        checkpoint_data = {
            "timestamp": time.time(),
            "goals": {k: asdict(v) for k, v in self.goals.items()},
            "plans": {k: asdict(v) for k, v in self.plans.items()},
            "current_state": self.current_state,
            "memory_count": len(self.memory),
            "important_memory_count": len(self.important_memory)
        }
        
        try:
            with open(checkpoint_path, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            self.logger.info(f"Created checkpoint: {checkpoint_path}")
        except Exception as e:
            self.logger.error(f"Failed to create checkpoint: {e}")
    
    def cleanup_old_checkpoints(self, keep_count: int = 5):
        """Clean up old checkpoints, keeping only the most recent ones."""
        checkpoint_files = sorted(self.base_path.glob("checkpoint_*.json"))
        if len(checkpoint_files) > keep_count:
            files_to_delete = checkpoint_files[:-keep_count]
            for file_path in files_to_delete:
                try:
                    file_path.unlink()
                    self.logger.info(f"Deleted old checkpoint: {file_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to delete checkpoint {file_path}: {e}")
