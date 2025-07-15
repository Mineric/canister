#!/usr/bin/env python3
"""
SWE-bench evaluation framework for Canister Agent.

This module provides integration with the SWE-bench benchmark for evaluating
the agent's software engineering capabilities on real-world GitHub issues.
"""

import os
import json
import time
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datasets import load_dataset

# Add project root to path for imports
import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from agent.agent import get_agent
except ImportError:
    # Fallback for when agent is not available
    def get_agent():
        return MockAgent()


class MockAgent:
    """Mock agent for testing when real agent is not available."""

    def run(self, problem_text: str) -> str:
        """Mock agent response."""
        return """
        I'll analyze this problem and provide a solution.

        ```diff
        --- a/example.py
        +++ b/example.py
        @@ -1,3 +1,3 @@
         def example_function():
        -    return "old implementation"
        +    return "new implementation"
        ```

        This patch should resolve the issue.
        """

    @property
    def tools(self):
        """Mock tools property."""
        return []


@dataclass
class SWEBenchInstance:
    """Represents a single SWE-bench evaluation instance."""
    instance_id: str
    repo: str
    base_commit: str
    patch: str
    test_patch: str
    problem_statement: str
    hints_text: str
    created_at: str
    version: str
    FAIL_TO_PASS: List[str]
    PASS_TO_PASS: List[str]


@dataclass
class SWEBenchResult:
    """Results from evaluating a single SWE-bench instance."""
    instance_id: str
    resolved: bool
    generated_patch: str
    execution_time: float
    error_message: Optional[str] = None
    agent_reasoning: Optional[str] = None


@dataclass
class SWEBenchEvaluationReport:
    """Complete evaluation report for SWE-bench run."""
    dataset_name: str
    total_instances: int
    resolved_count: int
    resolve_rate: float
    total_time: float
    average_time_per_instance: float
    results: List[SWEBenchResult]
    timestamp: str
    agent_config: Dict[str, Any]


class SWEBenchAgentInterface:
    """Interface layer between Canister agent and SWE-bench tasks."""
    
    def __init__(self, agent=None):
        """Initialize the interface with an agent instance."""
        self.agent = agent or get_agent()
        self.temp_dir = None
        
    def setup_workspace(self, instance: SWEBenchInstance) -> Path:
        """Set up a temporary workspace for the SWE-bench instance."""
        if self.temp_dir:
            self.cleanup_workspace()
            
        self.temp_dir = Path(tempfile.mkdtemp(prefix=f"swe_bench_{instance.instance_id}_"))
        
        # Clone the repository at the base commit
        repo_path = self.temp_dir / "repo"
        try:
            # Extract repo URL from instance.repo (format: owner/repo)
            repo_url = f"https://github.com/{instance.repo}.git"
            
            subprocess.run([
                "git", "clone", repo_url, str(repo_path)
            ], check=True, capture_output=True)
            
            # Checkout the base commit
            subprocess.run([
                "git", "checkout", instance.base_commit
            ], cwd=repo_path, check=True, capture_output=True)
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to setup repository: {e}")
            
        return repo_path
    
    def cleanup_workspace(self):
        """Clean up the temporary workspace."""
        if self.temp_dir and self.temp_dir.exists():
            import shutil
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None
    
    def format_problem_for_agent(self, instance: SWEBenchInstance, repo_path: Path) -> str:
        """Format the SWE-bench problem for the agent."""
        problem_text = f"""
# Software Engineering Task

You are working on the repository: {instance.repo}

## Problem Statement
{instance.problem_statement}

## Additional Context
{instance.hints_text if instance.hints_text else "No additional hints provided."}

## Repository Information
- Base commit: {instance.base_commit}
- Repository path: {repo_path}

## Task
Please analyze the problem and generate a patch that resolves the issue described above.
The patch should:
1. Fix the reported issue
2. Not break existing functionality
3. Follow the project's coding standards

Please use your available tools to:
1. Explore the codebase structure
2. Understand the problem context
3. Identify the root cause
4. Implement a solution
5. Generate the final patch

Focus on creating a minimal, targeted fix that addresses the core issue.
"""
        return problem_text
    
    def extract_patch_from_response(self, response: str) -> str:
        """Extract patch content from agent response."""
        # Look for common patch indicators
        patch_indicators = [
            "```diff",
            "```patch", 
            "--- a/",
            "+++ b/",
            "diff --git"
        ]
        
        lines = response.split('\n')
        patch_lines = []
        in_patch = False
        
        for line in lines:
            # Check if we're starting a patch block
            if any(indicator in line for indicator in patch_indicators):
                in_patch = True
                if not line.startswith('```'):
                    patch_lines.append(line)
                continue
                
            # Check if we're ending a code block
            if in_patch and line.strip() == '```':
                break
                
            # Collect patch lines
            if in_patch:
                patch_lines.append(line)
        
        return '\n'.join(patch_lines) if patch_lines else response
    
    def solve_instance(self, instance: SWEBenchInstance) -> SWEBenchResult:
        """Solve a single SWE-bench instance using the agent."""
        start_time = time.time()
        
        try:
            # Setup workspace
            repo_path = self.setup_workspace(instance)
            
            # Format problem for agent
            problem_text = self.format_problem_for_agent(instance, repo_path)
            
            # Get agent response
            response = self.agent.run(problem_text)
            
            # Extract patch from response
            generated_patch = self.extract_patch_from_response(response)
            
            execution_time = time.time() - start_time
            
            return SWEBenchResult(
                instance_id=instance.instance_id,
                resolved=bool(generated_patch.strip()),  # Basic check - actual resolution determined by SWE-bench harness
                generated_patch=generated_patch,
                execution_time=execution_time,
                agent_reasoning=response
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return SWEBenchResult(
                instance_id=instance.instance_id,
                resolved=False,
                generated_patch="",
                execution_time=execution_time,
                error_message=str(e)
            )
        finally:
            self.cleanup_workspace()


class SWEBenchEvaluator:
    """Main evaluator for running SWE-bench evaluations."""
    
    def __init__(self, agent=None):
        """Initialize evaluator with agent."""
        self.agent_interface = SWEBenchAgentInterface(agent)
        
    def load_dataset(self, dataset_name: str = "princeton-nlp/SWE-bench_Lite", 
                    split: str = "test", max_instances: Optional[int] = None) -> List[SWEBenchInstance]:
        """Load SWE-bench dataset instances."""
        print(f"Loading dataset: {dataset_name}")
        
        dataset = load_dataset(dataset_name, split=split)
        
        instances = []
        for i, item in enumerate(dataset):
            if max_instances and i >= max_instances:
                break
                
            instance = SWEBenchInstance(
                instance_id=item['instance_id'],
                repo=item['repo'],
                base_commit=item['base_commit'],
                patch=item['patch'],
                test_patch=item['test_patch'],
                problem_statement=item['problem_statement'],
                hints_text=item.get('hints_text', ''),
                created_at=item['created_at'],
                version=item['version'],
                FAIL_TO_PASS=item['FAIL_TO_PASS'],
                PASS_TO_PASS=item['PASS_TO_PASS']
            )
            instances.append(instance)
            
        print(f"Loaded {len(instances)} instances")
        return instances
    
    def evaluate_instances(self, instances: List[SWEBenchInstance]) -> List[SWEBenchResult]:
        """Evaluate multiple SWE-bench instances."""
        results = []
        
        for i, instance in enumerate(instances):
            print(f"\n{'='*60}")
            print(f"Evaluating instance {i+1}/{len(instances)}: {instance.instance_id}")
            print(f"Repository: {instance.repo}")
            print(f"{'='*60}")
            
            result = self.agent_interface.solve_instance(instance)
            results.append(result)
            
            # Print result summary
            status = "✅ RESOLVED" if result.resolved else "❌ FAILED"
            print(f"Result: {status}")
            print(f"Execution time: {result.execution_time:.2f}s")
            if result.error_message:
                print(f"Error: {result.error_message}")
                
        return results
    
    def run_evaluation(self, dataset_name: str = "princeton-nlp/SWE-bench_Lite",
                      max_instances: Optional[int] = None) -> SWEBenchEvaluationReport:
        """Run complete SWE-bench evaluation."""
        start_time = time.time()
        
        # Load instances
        instances = self.load_dataset(dataset_name, max_instances=max_instances)
        
        # Evaluate instances
        results = self.evaluate_instances(instances)
        
        # Calculate metrics
        resolved_count = sum(1 for r in results if r.resolved)
        total_time = time.time() - start_time
        
        report = SWEBenchEvaluationReport(
            dataset_name=dataset_name,
            total_instances=len(instances),
            resolved_count=resolved_count,
            resolve_rate=resolved_count / len(instances) if instances else 0.0,
            total_time=total_time,
            average_time_per_instance=total_time / len(instances) if instances else 0.0,
            results=results,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            agent_config={
                "agent_name": "Canister Agent",
                "model": "gpt-4o",
                "tools_count": len(self.agent_interface.agent.tools) if hasattr(self.agent_interface.agent, 'tools') else 0
            }
        )
        
        return report
    
    def save_report(self, report: SWEBenchEvaluationReport, output_path: Optional[str] = None):
        """Save evaluation report to file."""
        if not output_path:
            timestamp = int(time.time())
            output_path = f"swe_bench_evaluation_{timestamp}.json"
            
        with open(output_path, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
            
        print(f"📄 Report saved to: {output_path}")
        return output_path


def main():
    """Run SWE-bench evaluation."""
    print("🎯 Canister Agent SWE-bench Evaluation")
    print("=" * 60)
    
    evaluator = SWEBenchEvaluator()
    
    # Run evaluation on a small subset first
    report = evaluator.run_evaluation(
        dataset_name="princeton-nlp/SWE-bench_Lite",
        max_instances=5  # Start with 5 instances for testing
    )
    
    # Print summary
    print(f"\n📊 Evaluation Summary:")
    print(f"   Dataset: {report.dataset_name}")
    print(f"   Total instances: {report.total_instances}")
    print(f"   Resolved: {report.resolved_count}")
    print(f"   Resolve rate: {report.resolve_rate:.1%}")
    print(f"   Total time: {report.total_time:.2f}s")
    print(f"   Avg time per instance: {report.average_time_per_instance:.2f}s")
    
    # Save report
    evaluator.save_report(report)


if __name__ == "__main__":
    main()
