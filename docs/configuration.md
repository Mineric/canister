# Configuration Guide

Comprehensive configuration guide for the Canister Agent, covering development, production, and enterprise deployment scenarios.

## 🎯 **Overview**

The Canister Agent supports flexible configuration for different deployment scenarios:
- **Development**: Local development with in-memory services
- **Production**: Google Cloud with Vertex AI integration
- **Enterprise**: Full-scale deployment with advanced features
- **Hybrid**: Mixed local and cloud capabilities

## ⚙️ **Configuration Structure**

### **Memory Configuration**

```python
from agent.tools.memory_engine import MemoryConfig, MemoryMode

@dataclass
class MemoryConfig:
    # Operation mode
    mode: MemoryMode = MemoryMode.DEVELOPMENT
    
    # Google Cloud settings
    project_id: Optional[str] = None
    location: str = "us-central1"
    rag_corpus_name: Optional[str] = None
    
    # Local storage
    cache_dir: str = ".memory_cache"
    session_retention_days: int = 30
    memory_retention_days: int = 90
    
    # Performance tuning
    max_context_tokens: int = 32000
    similarity_threshold: float = 0.7
    max_memory_results: int = 10
    
    # Feature flags
    enable_codebase_integration: bool = True
    enable_conversation_memory: bool = True
    enable_cross_session_learning: bool = True
```

### **Agent Configuration**

```python
# agent/config.py
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class AgentConfig:
    # Model configuration
    model_name: str = "gpt-4"
    api_key: Optional[str] = None
    
    # Tool configuration
    enabled_tools: List[str] = None  # None = all tools
    tool_timeout: int = 300
    
    # Memory configuration
    memory_config: MemoryConfig = None
    
    # Logging configuration
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Performance configuration
    max_concurrent_tools: int = 5
    request_timeout: int = 60
```

## 🔧 **Environment-Specific Configurations**

### **Development Configuration**

```python
# config/development.py
from agent.tools.memory_engine import MemoryConfig, MemoryMode

DEVELOPMENT_CONFIG = MemoryConfig(
    mode=MemoryMode.DEVELOPMENT,
    cache_dir=".dev_memory",
    session_retention_days=7,
    memory_retention_days=30,
    max_context_tokens=16000,
    max_memory_results=5,
    enable_codebase_integration=True,
    enable_conversation_memory=True,
    enable_cross_session_learning=False
)

# Agent configuration
AGENT_CONFIG = AgentConfig(
    model_name="gpt-3.5-turbo",
    memory_config=DEVELOPMENT_CONFIG,
    log_level="DEBUG",
    max_concurrent_tools=3
)
```

### **Production Configuration**

```python
# config/production.py
import os
from agent.tools.memory_engine import MemoryConfig, MemoryMode

PRODUCTION_CONFIG = MemoryConfig(
    mode=MemoryMode.PRODUCTION,
    project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
    rag_corpus_name=os.getenv("RAG_CORPUS_NAME"),
    cache_dir="/app/memory_cache",
    session_retention_days=90,
    memory_retention_days=365,
    max_context_tokens=32000,
    similarity_threshold=0.8,
    max_memory_results=20,
    enable_codebase_integration=True,
    enable_conversation_memory=True,
    enable_cross_session_learning=True
)

AGENT_CONFIG = AgentConfig(
    model_name="gpt-4",
    api_key=os.getenv("OPENAI_API_KEY"),
    memory_config=PRODUCTION_CONFIG,
    log_level="INFO",
    log_file="/app/logs/agent.log",
    max_concurrent_tools=10,
    request_timeout=120
)
```

### **Enterprise Configuration**

```python
# config/enterprise.py
ENTERPRISE_CONFIG = MemoryConfig(
    mode=MemoryMode.HYBRID,
    project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
    rag_corpus_name=os.getenv("RAG_CORPUS_NAME"),
    cache_dir="/enterprise/memory_cache",
    session_retention_days=180,
    memory_retention_days=730,  # 2 years
    max_context_tokens=64000,
    similarity_threshold=0.75,
    max_memory_results=50,
    enable_codebase_integration=True,
    enable_conversation_memory=True,
    enable_cross_session_learning=True
)

AGENT_CONFIG = AgentConfig(
    model_name="gpt-4",
    memory_config=ENTERPRISE_CONFIG,
    log_level="INFO",
    max_concurrent_tools=20,
    request_timeout=300
)
```

## 🌍 **Environment Variables**

### **Required Variables**

```bash
# Google Cloud Configuration (Production/Enterprise)
export GOOGLE_CLOUD_PROJECT=your-gcp-project
export GOOGLE_CLOUD_LOCATION=us-central1
export RAG_CORPUS_NAME=projects/your-project/locations/us-central1/ragCorpora/your-corpus

# API Keys
export OPENAI_API_KEY=your-openai-api-key
export GOOGLE_API_KEY=your-google-api-key

# Authentication
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

### **Optional Variables**

```bash
# Memory Configuration
export MEMORY_MODE=production
export CACHE_DIR=/app/memory_cache
export SESSION_RETENTION_DAYS=90
export MEMORY_RETENTION_DAYS=365

# Performance Tuning
export MAX_CONTEXT_TOKENS=32000
export SIMILARITY_THRESHOLD=0.8
export MAX_MEMORY_RESULTS=20
export MAX_CONCURRENT_TOOLS=10

# Logging
export LOG_LEVEL=INFO
export LOG_FILE=/app/logs/agent.log

# Feature Flags
export ENABLE_CODEBASE_INTEGRATION=true
export ENABLE_CONVERSATION_MEMORY=true
export ENABLE_CROSS_SESSION_LEARNING=true
```

## 📁 **Configuration Files**

### **Configuration Directory Structure**

```
config/
├── __init__.py
├── base.py          # Base configuration
├── development.py   # Development settings
├── production.py    # Production settings
├── enterprise.py    # Enterprise settings
├── testing.py       # Test configuration
└── local.py         # Local overrides (gitignored)
```

### **Base Configuration**

```python
# config/base.py
from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class BaseConfig:
    """Base configuration with common settings."""
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # API Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Google Cloud
    gcp_project: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    gcp_location: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    # Paths
    cache_dir: str = os.getenv("CACHE_DIR", ".memory_cache")
    log_dir: str = os.getenv("LOG_DIR", "logs")
    
    # Performance
    max_context_tokens: int = int(os.getenv("MAX_CONTEXT_TOKENS", "32000"))
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "60"))
```

### **Configuration Factory**

```python
# config/__init__.py
import os
from .base import BaseConfig
from .development import DevelopmentConfig
from .production import ProductionConfig
from .enterprise import EnterpriseConfig

def get_config():
    """Get configuration based on environment."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "enterprise": EnterpriseConfig,
        "testing": DevelopmentConfig  # Use dev config for testing
    }
    
    config_class = config_map.get(env, DevelopmentConfig)
    return config_class()

# Global config instance
config = get_config()
```

## 🚀 **Deployment Configurations**

### **Docker Configuration**

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV ENVIRONMENT=production
ENV PYTHONPATH=/app
ENV CACHE_DIR=/app/memory_cache
ENV LOG_DIR=/app/logs

# Create directories
RUN mkdir -p /app/memory_cache /app/logs

# Copy application
COPY . /app
WORKDIR /app

# Install dependencies
RUN pip install -r requirements.txt

# Run agent
CMD ["python", "-m", "agent.main"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  canister-agent:
    build: .
    environment:
      - ENVIRONMENT=production
      - GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - RAG_CORPUS_NAME=${RAG_CORPUS_NAME}
    volumes:
      - ./memory_cache:/app/memory_cache
      - ./logs:/app/logs
      - ./service-account-key.json:/app/service-account-key.json
    ports:
      - "8080:8080"
```

### **Kubernetes Configuration**

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: canister-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: canister-agent
  template:
    metadata:
      labels:
        app: canister-agent
    spec:
      containers:
      - name: canister-agent
        image: canister-agent:latest
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: GOOGLE_CLOUD_PROJECT
          valueFrom:
            secretKeyRef:
              name: gcp-credentials
              key: project-id
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai-api-key
        volumeMounts:
        - name: memory-cache
          mountPath: /app/memory_cache
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: memory-cache
        persistentVolumeClaim:
          claimName: memory-cache-pvc
      - name: logs
        persistentVolumeClaim:
          claimName: logs-pvc
```

## 🔧 **Tool Configuration**

### **Selective Tool Enabling**

```python
# Enable specific tools only
ENABLED_TOOLS = [
    "get_current_time",
    "calculator",
    "file_management",
    "memory_search",
    "codebase_indexer"
]

def create_agent_with_tools(enabled_tools=None):
    """Create agent with specific tools."""
    all_tools = {
        "get_current_time": get_current_time_tool(),
        "calculator": calculator_tool(),
        "text_analyzer": text_analyzer_tool(),
        "file_management": file_management_tool(),
        "memory_search": memory_search_tool(),
        "codebase_indexer": codebase_indexer_tool(),
        # ... other tools
    }
    
    if enabled_tools:
        tools = [all_tools[name] for name in enabled_tools if name in all_tools]
    else:
        tools = list(all_tools.values())
    
    return LlmAgent(
        model=LiteLlm(model="gpt-4"),
        tools=tools
    )
```

### **Tool-Specific Configuration**

```python
# Tool configuration
TOOL_CONFIG = {
    "codebase_indexer": {
        "cache_dir": ".codebase_cache",
        "max_file_size": 1024 * 1024,  # 1MB
        "exclude_patterns": ["__pycache__", "*.pyc", ".git"],
        "include_patterns": ["*.py"]
    },
    "memory_search": {
        "max_results": 20,
        "similarity_threshold": 0.8,
        "include_codebase": True
    },
    "ast_merger": {
        "backup_enabled": True,
        "conflict_resolution": "interactive",
        "preserve_formatting": True
    }
}
```

## 📊 **Monitoring Configuration**

### **Logging Configuration**

```python
# logging_config.py
import logging
import os

def setup_logging(config):
    """Setup logging configuration."""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # File handler (if specified)
    handlers = [console_handler]
    if config.log_file:
        file_handler = logging.FileHandler(config.log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        handlers=handlers
    )
    
    # Configure specific loggers
    logging.getLogger("agent").setLevel(logging.INFO)
    logging.getLogger("memory").setLevel(logging.DEBUG)
    logging.getLogger("codebase").setLevel(logging.INFO)
```

### **Metrics Configuration**

```python
# metrics_config.py
METRICS_CONFIG = {
    "enabled": True,
    "endpoint": "/metrics",
    "port": 9090,
    "collectors": [
        "tool_usage",
        "memory_stats",
        "performance_metrics",
        "error_rates"
    ]
}
```

## 🛡️ **Security Configuration**

### **Authentication Configuration**

```python
# security_config.py
SECURITY_CONFIG = {
    "authentication": {
        "required": True,
        "methods": ["api_key", "oauth2"],
        "api_key_header": "X-API-Key",
        "oauth2_scopes": ["read", "write"]
    },
    "authorization": {
        "enabled": True,
        "roles": ["user", "admin", "developer"],
        "permissions": {
            "user": ["read"],
            "developer": ["read", "write"],
            "admin": ["read", "write", "admin"]
        }
    },
    "rate_limiting": {
        "enabled": True,
        "requests_per_minute": 60,
        "burst_size": 10
    }
}
```

## 🎯 **Best Practices**

### **Configuration Management**
1. **Environment separation**: Different configs for each environment
2. **Secret management**: Use environment variables for sensitive data
3. **Validation**: Validate configuration on startup
4. **Documentation**: Document all configuration options

### **Security**
1. **Never commit secrets**: Use .env files and .gitignore
2. **Use strong defaults**: Secure by default configuration
3. **Regular rotation**: Rotate API keys and credentials
4. **Access control**: Limit configuration access

### **Performance**
1. **Resource limits**: Set appropriate limits for your environment
2. **Caching**: Configure caching for optimal performance
3. **Monitoring**: Monitor configuration impact on performance
4. **Tuning**: Regularly review and tune configuration

---

**Next**: Explore [API Reference](./api-reference.md) for detailed API documentation.
