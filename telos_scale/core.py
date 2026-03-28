"""
Telos-Scale Core Module - v0.1
Main orchestrator class implementing the autonomous AI agent loop.
Target: under 300 lines of code.
"""

import os
import time
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from .memory import LocalMemory
from .sandbox import DockerSandbox
from .llm import LLMClient
from .shared import SharedClient


class TelosScale:
    """Main orchestrator - target under 300 lines."""

    def __init__(
        self,
        shared_url: Optional[str] = None,
        model: str = "gemini/gemini-flash-latest",
        max_memory_size: int = 1000,
        sandbox_image: str = "python:3.11-slim",
        sandbox_memory_limit: str = "512m",
    ):
        self.memory = LocalMemory(max_size=max_memory_size)
        self.shared = SharedClient(shared_url) if shared_url else None
        self.sandbox = DockerSandbox(image=sandbox_image, memory_limit=sandbox_memory_limit)
        self.llm = LLMClient(model=model)
        self.logger = self._setup_logger()
        self.cost_tracker = 0.0
        self.loop_count = 0

    def _setup_logger(self) -> logging.Logger:
        """Configure basic logging."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def run_loop(self) -> Dict[str, Any]:
        """Execute a single autonomous loop."""
        self.logger.info(f"Starting loop {self.loop_count + 1}")
        # 1. Get context from past trials
        context = self._get_context(num_examples=3)
        # 2. Generate goal using LLM
        goal = self._generate_goal(context)
        # 3. Execute goal in sandbox
        result = self._execute_goal(goal)
        # 4. Record locally
        self._record(goal, result)
        # 5. Optionally share
        if self.shared:
            self.shared.upload(goal, result)
        self.loop_count += 1
        self.logger.info(f"Completed loop {self.loop_count}")
        return {"goal": goal, "result": result}

    def _get_context(self, num_examples: int) -> List[Dict]:
        """Build context from recent local and shared memories."""
        local = self.memory.get_recent(num_examples)
        if self.shared:
            shared = self.shared.search(query="", limit=num_examples)
            return local + shared
        return local

    def _generate_goal(self, context: List[Dict]) -> str:
        """Generate a new goal based on context using LLM."""
        prompt = self._build_goal_prompt(context)
        try:
            response = self.llm.complete(prompt, max_tokens=500)
            goal = response.strip()
            if not goal:
                raise ValueError("LLM returned an empty goal.")
            return goal
        except Exception as e:
            self.logger.error(f"Failed to generate goal: {e}")
            raise  # Re-raise to stop the loop or caller handling

    def _build_goal_prompt(self, context: List[Dict]) -> str:
        """Construct prompt for goal generation."""
        examples = ""
        for i, trial in enumerate(context[-3:]):  # use at most 3 examples
            examples += f"Example {i+1}:\nGoal: {trial.get('goal', 'N/A')}\nResult: {trial.get('result', 'N/A')}\n\n"
        prompt = f"""You are an autonomous AI agent that learns by trying things.
Your task is to propose a new small coding task that can be executed in a Docker container.
The task should be simple, achievable, and potentially build upon previous attempts.

Previous trials:
{examples}
Propose a new coding task (goal) that is interesting and can be completed in a few minutes.
Respond with only the goal description, no extra text."""
        return prompt

    def _execute_goal(self, goal: str) -> str:
        """Execute the goal in Docker sandbox and capture result."""
        if not goal or goal.startswith("Error"):
            return f"Invalid goal: {goal}"
            
        try:
            self.sandbox.start()
            # For now, a simple implementation: run a command based on goal
            cmd = f"echo 'Goal: {goal}' && python -c \"print('Executing...')\""
            exit_code, output = self.sandbox.execute_command(cmd)
            
            # Simple token counting for cost estimation
            prompt_tokens = self.llm.count_tokens(goal)
            completion_tokens = self.llm.count_tokens(output)
            self.cost_tracker += self.llm.estimate_cost(prompt_tokens, completion_tokens)
            
            if exit_code == 0:
                result = f"Success: {output[:200]}"
            else:
                result = f"Error (exit {exit_code}): {output[:200]}"
            self.sandbox.stop(cleanup=True)
            return result
        except Exception as e:
            self.logger.error(f"Sandbox execution failed: {e}")
            return f"Sandbox execution failed: {str(e)}"

    def _record(self, goal: str, result: str):
        """Store trial in local memory."""
        self.memory.add(goal, result)
        # Cost is now tracked in _execute_goal using real estimations

    def run(self, loops: int = 10, workers: int = 1):
        """Run multiple loops, optionally in parallel."""
        if workers > 1:
            self._run_parallel(loops, workers)
        else:
            try:
                for i in range(loops):
                    self.run_loop()
            except Exception as e:
                self.logger.critical(f"Aborting run due to critical error: {e}")
                return

    def _run_parallel(self, loops: int, workers: int):
        """Parallel execution using multiprocessing (placeholder)."""
        # For v0.1, we'll just run sequentially; parallel implementation later.
        self.logger.warning("Parallel execution not yet implemented, running sequentially.")
        self.run(loops=loops, workers=1)


if __name__ == "__main__":
    # Quick test
    agent = TelosScale()
    result = agent.run_loop()
    print(f"Goal: {result['goal']}")
    print(f"Result: {result['result']}")