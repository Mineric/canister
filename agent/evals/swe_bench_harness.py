#!/usr/bin/env python3
"""
SWE-bench evaluation harness for Canister Agent.

This module provides the core evaluation harness that integrates with the official
SWE-bench evaluation system to run comprehensive evaluations.
"""

import os
import json
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

from .swe_bench_eval import SWEBenchEvaluator, SWEBenchResult


@dataclass
class SWEBenchHarnessConfig:
    """Configuration for SWE-bench harness evaluation."""
    dataset_name: str = "princeton-nlp/SWE-bench_Lite"
    max_workers: int = 1
    timeout: int = 1800  # 30 minutes per instance
    max_instances: Optional[int] = None
    run_id: str = "canister_agent_eval"
    use_docker: bool = True
    namespace: str = ""  # Empty for ARM systems to build locally


class SWEBenchHarness:
    """
    Core evaluation harness that integrates Canister agent with official SWE-bench evaluation.
    
    This harness:
    1. Runs the agent on SWE-bench instances to generate patches
    2. Uses the official SWE-bench Docker evaluation to test patches
    3. Provides comprehensive metrics and reporting
    """
    
    def __init__(self, config: SWEBenchHarnessConfig = None):
        """Initialize the harness with configuration."""
        self.config = config or SWEBenchHarnessConfig()
        self.evaluator = SWEBenchEvaluator()
        self.temp_dir = None
        
    def setup_evaluation_environment(self) -> Path:
        """Set up temporary environment for evaluation."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="swe_bench_harness_"))
        
        # Create directories for evaluation
        (self.temp_dir / "predictions").mkdir()
        (self.temp_dir / "logs").mkdir()
        (self.temp_dir / "results").mkdir()
        
        return self.temp_dir
    
    def cleanup_environment(self):
        """Clean up evaluation environment."""
        if self.temp_dir and self.temp_dir.exists():
            import shutil
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None
    
    def generate_predictions(self) -> Path:
        """Generate predictions using the Canister agent."""
        print("🤖 Generating predictions with Canister agent...")
        
        # Load instances and generate predictions
        instances = self.evaluator.load_dataset(
            self.config.dataset_name, 
            max_instances=self.config.max_instances
        )
        
        results = self.evaluator.evaluate_instances(instances)
        
        # Convert results to SWE-bench prediction format
        predictions = {}
        for result in results:
            predictions[result.instance_id] = result.generated_patch
        
        # Save predictions file
        predictions_file = self.temp_dir / "predictions" / "predictions.json"
        with open(predictions_file, 'w') as f:
            json.dump(predictions, f, indent=2)
            
        print(f"📄 Predictions saved to: {predictions_file}")
        return predictions_file
    
    def run_official_evaluation(self, predictions_file: Path) -> Dict[str, Any]:
        """Run the official SWE-bench evaluation harness."""
        print("🔍 Running official SWE-bench evaluation...")
        
        # Prepare evaluation command
        cmd = [
            "python", "-m", "swebench.harness.run_evaluation",
            "--dataset_name", self.config.dataset_name,
            "--predictions_path", str(predictions_file),
            "--max_workers", str(self.config.max_workers),
            "--run_id", self.config.run_id
        ]
        
        # Add namespace for ARM systems
        if self.config.namespace == "":
            cmd.extend(["--namespace", ""])
        
        # Set working directory to temp dir for logs
        eval_dir = self.temp_dir / "evaluation"
        eval_dir.mkdir(exist_ok=True)
        
        try:
            print(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                cwd=eval_dir,
                capture_output=True,
                text=True,
                timeout=self.config.timeout * (self.config.max_instances or 10)
            )
            
            if result.returncode != 0:
                print(f"❌ Evaluation failed with return code {result.returncode}")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                return {"success": False, "error": result.stderr}
            
            print("✅ Official evaluation completed successfully")
            
            # Look for results file
            results_dir = eval_dir / "evaluation_results"
            if results_dir.exists():
                result_files = list(results_dir.glob("*.json"))
                if result_files:
                    with open(result_files[0], 'r') as f:
                        official_results = json.load(f)
                    return {"success": True, "results": official_results}
            
            return {"success": True, "results": {"message": "Evaluation completed but results file not found"}}
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Evaluation timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def calculate_comprehensive_metrics(self, agent_results: List[SWEBenchResult], 
                                      official_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive evaluation metrics."""
        metrics = {
            "agent_metrics": {
                "total_instances": len(agent_results),
                "patches_generated": sum(1 for r in agent_results if r.generated_patch.strip()),
                "generation_success_rate": sum(1 for r in agent_results if r.generated_patch.strip()) / len(agent_results),
                "average_generation_time": sum(r.execution_time for r in agent_results) / len(agent_results),
                "errors": sum(1 for r in agent_results if r.error_message)
            }
        }
        
        # Add official SWE-bench metrics if available
        if official_results.get("success") and "results" in official_results:
            official_data = official_results["results"]
            if isinstance(official_data, dict):
                resolved_instances = []
                for instance_id, result in official_data.items():
                    if isinstance(result, dict) and result.get("resolved", False):
                        resolved_instances.append(instance_id)
                
                metrics["official_metrics"] = {
                    "resolved_instances": len(resolved_instances),
                    "resolve_rate": len(resolved_instances) / len(agent_results) if agent_results else 0,
                    "resolved_instance_ids": resolved_instances
                }
        
        return metrics
    
    def run_comprehensive_evaluation(self) -> Dict[str, Any]:
        """Run comprehensive SWE-bench evaluation with both agent and official metrics."""
        try:
            # Setup environment
            self.setup_evaluation_environment()
            
            print("🎯 Starting comprehensive SWE-bench evaluation")
            print(f"Dataset: {self.config.dataset_name}")
            print(f"Max instances: {self.config.max_instances or 'All'}")
            print(f"Run ID: {self.config.run_id}")
            
            # Step 1: Generate predictions with agent
            predictions_file = self.generate_predictions()
            
            # Get agent results for metrics
            instances = self.evaluator.load_dataset(
                self.config.dataset_name,
                max_instances=self.config.max_instances
            )
            agent_results = self.evaluator.evaluate_instances(instances)
            
            # Step 2: Run official evaluation
            official_results = self.run_official_evaluation(predictions_file)
            
            # Step 3: Calculate comprehensive metrics
            metrics = self.calculate_comprehensive_metrics(agent_results, official_results)
            
            # Step 4: Create comprehensive report
            report = {
                "evaluation_config": asdict(self.config),
                "timestamp": self.evaluator.agent_interface.agent.run("get_current_time_tool()") if hasattr(self.evaluator.agent_interface.agent, 'run') else "unknown",
                "agent_results": [asdict(r) for r in agent_results],
                "official_evaluation": official_results,
                "comprehensive_metrics": metrics,
                "summary": {
                    "total_instances": len(agent_results),
                    "patches_generated": metrics["agent_metrics"]["patches_generated"],
                    "generation_success_rate": f"{metrics['agent_metrics']['generation_success_rate']:.1%}",
                    "official_resolve_rate": f"{metrics.get('official_metrics', {}).get('resolve_rate', 0):.1%}",
                    "average_time_per_instance": f"{metrics['agent_metrics']['average_generation_time']:.2f}s"
                }
            }
            
            return report
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "evaluation_config": asdict(self.config)
            }
        finally:
            self.cleanup_environment()
    
    def save_evaluation_report(self, report: Dict[str, Any], output_path: Optional[str] = None):
        """Save comprehensive evaluation report."""
        if not output_path:
            import time
            timestamp = int(time.time())
            output_path = f"swe_bench_comprehensive_evaluation_{timestamp}.json"
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📄 Comprehensive report saved to: {output_path}")
        return output_path


def create_evaluation_config(dataset: str = "lite", max_instances: int = None, 
                           timeout: int = 1800) -> SWEBenchHarnessConfig:
    """Create evaluation configuration with common presets."""
    dataset_mapping = {
        "lite": "princeton-nlp/SWE-bench_Lite",
        "verified": "princeton-nlp/SWE-bench_Verified", 
        "full": "princeton-nlp/SWE-bench"
    }
    
    return SWEBenchHarnessConfig(
        dataset_name=dataset_mapping.get(dataset, dataset),
        max_instances=max_instances,
        timeout=timeout,
        run_id=f"canister_agent_{dataset}_{max_instances or 'all'}"
    )


def main():
    """Run SWE-bench harness evaluation."""
    print("🎯 Canister Agent SWE-bench Harness Evaluation")
    print("=" * 60)
    
    # Create configuration for a small test run
    config = create_evaluation_config(
        dataset="lite",
        max_instances=3,  # Small test run
        timeout=600  # 10 minutes per instance
    )
    
    # Run evaluation
    harness = SWEBenchHarness(config)
    report = harness.run_comprehensive_evaluation()
    
    # Print summary
    if report.get("success", True):  # Default to True if not specified
        print(f"\n📊 Evaluation Summary:")
        summary = report.get("summary", {})
        for key, value in summary.items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
    else:
        print(f"❌ Evaluation failed: {report.get('error', 'Unknown error')}")
    
    # Save report
    harness.save_evaluation_report(report)


if __name__ == "__main__":
    main()
