"""
Unit tests for Telos-Scale core functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from telos_scale.core import TelosScale


class TestTelosScale(unittest.TestCase):
    """Test the TelosScale class."""

    def setUp(self):
        """Set up mocks for dependencies."""
        self.mock_memory = Mock()
        self.mock_sandbox = Mock()
        self.mock_llm = Mock()
        self.mock_shared = Mock()
        
        with patch('telos_scale.core.LocalMemory', return_value=self.mock_memory):
            with patch('telos_scale.core.DockerSandbox', return_value=self.mock_sandbox):
                with patch('telos_scale.core.LLMClient', return_value=self.mock_llm):
                    with patch('telos_scale.core.SharedClient', return_value=self.mock_shared):
                        self.agent = TelosScale(shared_url=None)

    def test_initialization(self):
        """Test that TelosScale initializes correctly."""
        self.assertIsNotNone(self.agent.memory)
        self.assertIsNotNone(self.agent.sandbox)
        self.assertIsNotNone(self.agent.llm)
        self.assertIsNone(self.agent.shared)

    def test_get_context_local_only(self):
        """Test context retrieval when no shared client."""
        self.agent.shared = None
        self.mock_memory.get_recent.return_value = [
            {"goal": "test1", "result": "result1"},
            {"goal": "test2", "result": "result2"},
        ]
        context = self.agent._get_context(num_examples=2)
        self.assertEqual(len(context), 2)
        self.mock_memory.get_recent.assert_called_once_with(2)

    def test_get_context_with_shared(self):
        """Test context retrieval with shared client."""
        self.agent.shared = self.mock_shared
        self.mock_memory.get_recent.return_value = [{"goal": "local", "result": "local"}]
        self.mock_shared.search.return_value = [{"goal": "shared", "result": "shared"}]
        context = self.agent._get_context(num_examples=3)
        self.assertEqual(len(context), 2)
        self.mock_shared.search.assert_called_once_with(query="", limit=3)

    def test_generate_goal(self):
        """Test goal generation."""
        context = []
        self.mock_llm.complete.return_value = "Write a Python script"
        goal = self.agent._generate_goal(context)
        self.assertEqual(goal, "Write a Python script")
        self.mock_llm.complete.assert_called_once()

    def test_generate_goal_fallback(self):
        """Test fallback when LLM returns empty."""
        self.mock_llm.complete.return_value = ""
        goal = self.agent._generate_goal([])
        self.assertIn("Hello, World", goal)

    def test_execute_goal_success(self):
        """Test goal execution with success."""
        self.mock_sandbox.start.return_value = None
        self.mock_sandbox.execute_command.return_value = (0, "Success output")
        self.mock_sandbox.stop.return_value = None
        result = self.agent._execute_goal("some goal")
        self.assertTrue(result.startswith("Success:"))
        self.mock_sandbox.execute_command.assert_called_once()

    def test_execute_goal_failure(self):
        """Test goal execution with failure."""
        self.mock_sandbox.execute_command.return_value = (1, "Error output")
        result = self.agent._execute_goal("goal")
        self.assertIn("Error", result)

    def test_record(self):
        """Test recording a trial."""
        self.agent._record("goal", "result")
        self.mock_memory.add.assert_called_once_with("goal", "result")

    def test_run_loop(self):
        """Test a full loop execution."""
        # Mock internal methods
        self.agent._get_context = Mock(return_value=[])
        self.agent._generate_goal = Mock(return_value="test goal")
        self.agent._execute_goal = Mock(return_value="test result")
        self.agent._record = Mock()
        self.agent.shared = None
        
        result = self.agent.run_loop()
        self.assertEqual(result["goal"], "test goal")
        self.assertEqual(result["result"], "test result")
        self.agent._record.assert_called_once_with("test goal", "test result")
        self.assertEqual(self.agent.loop_count, 1)

    def test_run_loop_with_shared(self):
        """Test loop with shared client."""
        self.agent.shared = self.mock_shared
        self.agent._get_context = Mock(return_value=[])
        self.agent._generate_goal = Mock(return_value="goal")
        self.agent._execute_goal = Mock(return_value="result")
        self.agent._record = Mock()
        
        self.agent.run_loop()
        self.mock_shared.upload.assert_called_once_with("goal", "result")

    def test_run_sequential(self):
        """Test running multiple loops sequentially."""
        self.agent.run_loop = Mock()
        self.agent.run(loops=3, workers=1)
        self.assertEqual(self.agent.run_loop.call_count, 3)

    def test_run_parallel_not_implemented(self):
        """Test that parallel execution warns and falls back."""
        self.agent.run_loop = Mock()
        with self.assertLogs(level="WARNING") as cm:
            self.agent.run(loops=5, workers=10)
        self.assertTrue(any("Parallel execution not yet implemented" in log for log in cm.output))
        # Should have called run_loop 5 times (since falls back to sequential)
        self.assertEqual(self.agent.run_loop.call_count, 5)


if __name__ == "__main__":
    unittest.main()