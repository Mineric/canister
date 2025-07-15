#!/usr/bin/env python3
"""
SWE-bench configuration and customization for Canister Agent.

This module provides configuration options for different SWE-bench evaluation
modes, parameters, and customization settings.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict, field
from enum import Enum


class SWEBenchDataset(Enum):
    """Available SWE-bench datasets."""
    LITE = "princeton-nlp/SWE-bench_Lite"
    VERIFIED = "princeton-nlp/SWE-bench_Verified"
    FULL = "princeton-nlp/SWE-bench"
    MULTIMODAL = "princeton-nlp/SWE-bench_Multimodal"


class EvaluationMode(Enum):
    """Evaluation modes for different use cases."""
    QUICK_TEST = "quick_test"  # Small subset for testing
    DEVELOPMENT = "development"  # Medium subset for development
    BENCHMARK = "benchmark"  # Full evaluation for benchmarking
    CUSTOM = "custom"  # Custom configuration


class DifficultyLevel(Enum):
    """Difficulty levels for filtering instances."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    ALL = "all"


@dataclass
class AgentConfiguration:
    """Configuration for the agent behavior during evaluation."""
    model: str = "openai/gpt-4o"
    max_reasoning_steps: int = 10
    enable_self_reflection: bool = True
    use_codebase_indexing: bool = True
    enable_memory_context: bool = True
    timeout_per_step: int = 300  # 5 minutes per reasoning step
    max_patch_size: int = 5000  # Maximum patch size in characters


@dataclass
class EvaluationConfiguration:
    """Main configuration for SWE-bench evaluation."""
    # Dataset configuration
    dataset: SWEBenchDataset = SWEBenchDataset.LITE
    max_instances: Optional[int] = None
    instance_filter: Optional[List[str]] = None  # Specific instance IDs
    repository_filter: Optional[List[str]] = None  # Specific repositories
    difficulty_level: DifficultyLevel = DifficultyLevel.ALL
    
    # Evaluation settings
    mode: EvaluationMode = EvaluationMode.DEVELOPMENT
    max_workers: int = 1
    timeout_per_instance: int = 1800  # 30 minutes
    enable_docker_evaluation: bool = True
    docker_namespace: str = ""  # Empty for ARM systems
    
    # Agent configuration
    agent_config: AgentConfiguration = field(default_factory=AgentConfiguration)
    
    # Output configuration
    run_id: str = "canister_agent_eval"
    output_directory: str = "swe_bench_results"
    save_intermediate_results: bool = True
    generate_detailed_reports: bool = True
    
    # Advanced options
    enable_parallel_processing: bool = False
    retry_failed_instances: bool = True
    max_retries: int = 2
    enable_progressive_evaluation: bool = False  # Start with easier instances


@dataclass
class RepositoryConfiguration:
    """Configuration for specific repository handling."""
    repo_name: str
    custom_setup_commands: List[str] = field(default_factory=list)
    environment_variables: Dict[str, str] = field(default_factory=dict)
    timeout_multiplier: float = 1.0
    difficulty_override: Optional[DifficultyLevel] = None


class SWEBenchConfigurationManager:
    """Manages SWE-bench evaluation configurations."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize configuration manager."""
        self.config_dir = Path(config_dir) if config_dir else Path.cwd() / "swe_bench_configs"
        self.config_dir.mkdir(exist_ok=True)
        
        # Load default configurations
        self.preset_configs = self._create_preset_configurations()
        self.repository_configs = self._load_repository_configurations()
    
    def _create_preset_configurations(self) -> Dict[str, EvaluationConfiguration]:
        """Create preset configurations for common use cases."""
        return {
            "quick_test": EvaluationConfiguration(
                dataset=SWEBenchDataset.LITE,
                mode=EvaluationMode.QUICK_TEST,
                max_instances=5,
                timeout_per_instance=600,  # 10 minutes
                run_id="quick_test",
                agent_config=AgentConfiguration(
                    max_reasoning_steps=5,
                    timeout_per_step=120  # 2 minutes
                )
            ),
            
            "development": EvaluationConfiguration(
                dataset=SWEBenchDataset.LITE,
                mode=EvaluationMode.DEVELOPMENT,
                max_instances=50,
                timeout_per_instance=1200,  # 20 minutes
                run_id="development",
                enable_docker_evaluation=True,
                save_intermediate_results=True
            ),
            
            "lite_benchmark": EvaluationConfiguration(
                dataset=SWEBenchDataset.LITE,
                mode=EvaluationMode.BENCHMARK,
                max_instances=None,  # All instances
                timeout_per_instance=1800,  # 30 minutes
                run_id="lite_benchmark",
                enable_docker_evaluation=True,
                generate_detailed_reports=True,
                retry_failed_instances=True
            ),
            
            "verified_benchmark": EvaluationConfiguration(
                dataset=SWEBenchDataset.VERIFIED,
                mode=EvaluationMode.BENCHMARK,
                max_instances=None,
                timeout_per_instance=2400,  # 40 minutes
                run_id="verified_benchmark",
                enable_docker_evaluation=True,
                generate_detailed_reports=True,
                max_workers=2
            ),
            
            "full_benchmark": EvaluationConfiguration(
                dataset=SWEBenchDataset.FULL,
                mode=EvaluationMode.BENCHMARK,
                max_instances=None,
                timeout_per_instance=3600,  # 1 hour
                run_id="full_benchmark",
                enable_docker_evaluation=True,
                generate_detailed_reports=True,
                max_workers=4,
                enable_parallel_processing=True
            ),
            
            "difficulty_progressive": EvaluationConfiguration(
                dataset=SWEBenchDataset.LITE,
                mode=EvaluationMode.CUSTOM,
                max_instances=100,
                enable_progressive_evaluation=True,
                difficulty_level=DifficultyLevel.EASY,
                run_id="progressive_eval"
            )
        }
    
    def _load_repository_configurations(self) -> Dict[str, RepositoryConfiguration]:
        """Load repository-specific configurations."""
        # Common repository configurations
        return {
            "django/django": RepositoryConfiguration(
                repo_name="django/django",
                custom_setup_commands=[
                    "pip install -e .",
                    "python -m django check"
                ],
                environment_variables={"DJANGO_SETTINGS_MODULE": "test_settings"},
                timeout_multiplier=1.5,
                difficulty_override=DifficultyLevel.HARD
            ),
            
            "scikit-learn/scikit-learn": RepositoryConfiguration(
                repo_name="scikit-learn/scikit-learn",
                custom_setup_commands=[
                    "pip install -e .",
                    "python -c 'import sklearn; print(sklearn.__version__)'"
                ],
                timeout_multiplier=2.0,
                difficulty_override=DifficultyLevel.HARD
            ),
            
            "sympy/sympy": RepositoryConfiguration(
                repo_name="sympy/sympy",
                custom_setup_commands=[
                    "pip install -e .",
                    "python -c 'import sympy; print(sympy.__version__)'"
                ],
                timeout_multiplier=1.2,
                difficulty_override=DifficultyLevel.MEDIUM
            ),
            
            "matplotlib/matplotlib": RepositoryConfiguration(
                repo_name="matplotlib/matplotlib",
                custom_setup_commands=[
                    "pip install -e .",
                    "python -c 'import matplotlib; print(matplotlib.__version__)'"
                ],
                environment_variables={"MPLBACKEND": "Agg"},
                timeout_multiplier=1.3
            )
        }
    
    def get_preset_config(self, preset_name: str) -> EvaluationConfiguration:
        """Get a preset configuration by name."""
        if preset_name not in self.preset_configs:
            available = list(self.preset_configs.keys())
            raise ValueError(f"Unknown preset '{preset_name}'. Available: {available}")
        
        return self.preset_configs[preset_name]
    
    def create_custom_config(self, base_preset: str = "development", **overrides) -> EvaluationConfiguration:
        """Create a custom configuration based on a preset with overrides."""
        base_config = self.get_preset_config(base_preset)
        
        # Apply overrides
        config_dict = asdict(base_config)
        for key, value in overrides.items():
            if '.' in key:
                # Handle nested keys like 'agent_config.model'
                keys = key.split('.')
                current = config_dict
                for k in keys[:-1]:
                    current = current[k]
                current[keys[-1]] = value
            else:
                config_dict[key] = value
        
        # Reconstruct configuration
        return EvaluationConfiguration(**config_dict)
    
    def filter_instances_by_difficulty(self, instances: List[Dict], 
                                     difficulty: DifficultyLevel) -> List[Dict]:
        """Filter instances by difficulty level."""
        if difficulty == DifficultyLevel.ALL:
            return instances
        
        # Simple heuristic for difficulty based on repository and problem characteristics
        difficulty_scores = []
        for instance in instances:
            score = self._calculate_instance_difficulty(instance)
            difficulty_scores.append((instance, score))
        
        # Sort by difficulty
        difficulty_scores.sort(key=lambda x: x[1])
        
        # Filter based on difficulty level
        total = len(difficulty_scores)
        if difficulty == DifficultyLevel.EASY:
            return [inst for inst, _ in difficulty_scores[:total//3]]
        elif difficulty == DifficultyLevel.MEDIUM:
            return [inst for inst, _ in difficulty_scores[total//3:2*total//3]]
        elif difficulty == DifficultyLevel.HARD:
            return [inst for inst, _ in difficulty_scores[2*total//3:]]
        
        return instances
    
    def _calculate_instance_difficulty(self, instance: Dict) -> float:
        """Calculate difficulty score for an instance."""
        score = 0.0
        
        # Repository-based difficulty
        repo_name = instance.get('repo', '')
        if repo_name in self.repository_configs:
            repo_config = self.repository_configs[repo_name]
            if repo_config.difficulty_override:
                if repo_config.difficulty_override == DifficultyLevel.EASY:
                    score += 0.2
                elif repo_config.difficulty_override == DifficultyLevel.MEDIUM:
                    score += 0.5
                elif repo_config.difficulty_override == DifficultyLevel.HARD:
                    score += 0.8
        
        # Problem statement complexity
        problem_statement = instance.get('problem_statement', '')
        if len(problem_statement) > 1000:
            score += 0.2
        if 'complex' in problem_statement.lower() or 'difficult' in problem_statement.lower():
            score += 0.1
        
        # Test complexity
        fail_to_pass = instance.get('FAIL_TO_PASS', [])
        if len(fail_to_pass) > 5:
            score += 0.2
        
        return min(score, 1.0)  # Cap at 1.0
    
    def save_config(self, config: EvaluationConfiguration, name: str):
        """Save configuration to file."""
        config_file = self.config_dir / f"{name}.json"
        with open(config_file, 'w') as f:
            json.dump(asdict(config), f, indent=2, default=str)
        print(f"Configuration saved to: {config_file}")
    
    def load_config(self, name: str) -> EvaluationConfiguration:
        """Load configuration from file."""
        config_file = self.config_dir / f"{name}.json"
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            config_dict = json.load(f)
        
        return EvaluationConfiguration(**config_dict)
    
    def list_available_configs(self) -> Dict[str, List[str]]:
        """List all available configurations."""
        return {
            "presets": list(self.preset_configs.keys()),
            "saved": [f.stem for f in self.config_dir.glob("*.json")],
            "repositories": list(self.repository_configs.keys())
        }
    
    def validate_config(self, config: EvaluationConfiguration) -> List[str]:
        """Validate configuration and return any warnings."""
        warnings = []
        
        if config.max_instances and config.max_instances > 1000:
            warnings.append("Large number of instances may take very long to evaluate")
        
        if config.timeout_per_instance < 300:
            warnings.append("Short timeout may cause premature failures")
        
        if config.max_workers > 8:
            warnings.append("High worker count may overwhelm system resources")
        
        if not config.enable_docker_evaluation and config.mode == EvaluationMode.BENCHMARK:
            warnings.append("Docker evaluation recommended for benchmark mode")
        
        return warnings


def create_evaluation_config(preset: str = "development", **kwargs) -> EvaluationConfiguration:
    """Convenience function to create evaluation configuration."""
    manager = SWEBenchConfigurationManager()
    return manager.create_custom_config(preset, **kwargs)


def main():
    """Demo configuration management."""
    print("⚙️ SWE-bench Configuration Management Demo")
    print("="*50)
    
    manager = SWEBenchConfigurationManager()
    
    # List available configurations
    configs = manager.list_available_configs()
    print(f"Available presets: {configs['presets']}")
    
    # Show a sample configuration
    config = manager.get_preset_config("development")
    print(f"\nSample 'development' configuration:")
    print(f"  Dataset: {config.dataset.value}")
    print(f"  Max instances: {config.max_instances}")
    print(f"  Timeout: {config.timeout_per_instance}s")
    print(f"  Agent model: {config.agent_config.model}")


if __name__ == "__main__":
    main()
