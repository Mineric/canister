#!/usr/bin/env python3
"""
Test script for Professional SWE-Level Capabilities
Demonstrates the advanced code comprehension and intelligent merging capabilities
that match the sophistication of professional software engineering agents.
"""

import tempfile
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agent.tools.code_comprehension import code_comprehension_tool
from agent.tools.intelligent_merger import intelligent_merger_tool


def test_code_comprehension():
    """Test code comprehension capabilities."""
    print("🧠 Testing Code Comprehension")
    print("=" * 45)
    
    try:
        comprehension_tool = code_comprehension_tool()
        
        # Analyze the current project
        project_root_str = str(Path(__file__).parent.parent)
        result = comprehension_tool.func(
            root_path=project_root_str,
            include_patterns=True,
            include_quality=True,
            include_refactoring=True
        )
        
        print("✅ Advanced Code Comprehension Results:")
        print(result)
        print()
        
    except Exception as e:
        print(f"❌ Advanced comprehension test failed: {e}")
        print()


def test_intelligent_merger():
    """Test intelligent merger capabilities."""
    print("🎓 Testing Intelligent Merger")
    print("=" * 45)
    
    # Create a complex test scenario
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a sophisticated codebase structure
        create_sophisticated_test_codebase(temp_path)
        
        # Test file to merge into
        target_file = temp_path / "services" / "user_service.py"
        
        # Complex AI-generated code that tests various aspects
        complex_ai_code = '''
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass

@dataclass
class UserPreferences:
    """User preference configuration."""
    theme: str = "light"
    notifications: bool = True
    language: str = "en"
    timezone: str = "UTC"

class UserService:
    """Enhanced user service with advanced features."""
    
    def __init__(self, database_manager, cache_service, notification_service):
        self.db = database_manager
        self.cache = cache_service
        self.notifications = notification_service
        self.logger = logging.getLogger(__name__)
        self._user_sessions = {}
    
    async def create_user_with_preferences(
        self, 
        user_data: Dict[str, Any], 
        preferences: Optional[UserPreferences] = None
    ) -> Dict[str, Any]:
        """Create a new user with optional preferences."""
        try:
            # Validate user data
            if not self._validate_user_data(user_data):
                raise ValueError("Invalid user data provided")
            
            # Set default preferences if none provided
            if preferences is None:
                preferences = UserPreferences()
            
            # Create user in database
            user_id = await self.db.create_user(user_data)
            
            # Store preferences
            await self.db.store_user_preferences(user_id, preferences)
            
            # Cache user data
            await self.cache.set(f"user:{user_id}", user_data, ttl=3600)
            
            # Send welcome notification
            await self.notifications.send_welcome_email(user_data["email"])
            
            self.logger.info(f"Created user {user_id} with preferences")
            
            return {
                "user_id": user_id,
                "preferences": preferences,
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create user: {e}")
            raise
    
    def _validate_user_data(self, user_data: Dict[str, Any]) -> bool:
        """Validate user data before creation."""
        required_fields = ["email", "username", "password"]
        
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                return False
        
        # Email validation (simplified)
        if "@" not in user_data["email"]:
            return False
        
        # Password strength check (simplified)
        if len(user_data["password"]) < 8:
            return False
        
        return True
    
    async def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user analytics."""
        try:
            # Check cache first
            cached_analytics = await self.cache.get(f"analytics:{user_id}")
            if cached_analytics:
                return cached_analytics
            
            # Gather analytics from multiple sources
            user_data = await self.db.get_user(user_id)
            activity_data = await self.db.get_user_activity(user_id)
            preference_data = await self.db.get_user_preferences(user_id)
            
            analytics = {
                "user_id": user_id,
                "total_sessions": len(activity_data.get("sessions", [])),
                "last_login": activity_data.get("last_login"),
                "preferences": preference_data,
                "engagement_score": self._calculate_engagement_score(activity_data),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Cache analytics
            await self.cache.set(f"analytics:{user_id}", analytics, ttl=1800)
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Failed to get analytics for user {user_id}: {e}")
            return {}
    
    def _calculate_engagement_score(self, activity_data: Dict[str, Any]) -> float:
        """Calculate user engagement score based on activity."""
        sessions = activity_data.get("sessions", [])
        if not sessions:
            return 0.0
        
        # Simple engagement calculation
        total_duration = sum(session.get("duration", 0) for session in sessions)
        avg_session_duration = total_duration / len(sessions)
        
        # Normalize to 0-1 scale
        return min(avg_session_duration / 3600, 1.0)  # Max 1 hour = score 1.0
'''
        
        try:
            # Test professional merger
            professional_tool = intelligent_merger_tool()
            
            # Test different strategies
            strategies = ["conservative", "intelligent", "architectural"]
            
            for strategy in strategies:
                print(f"\n🔧 Testing {strategy.title()} Strategy:")
                print("-" * 40)
                
                result = professional_tool.func(
                    file_path=str(target_file),
                    ai_generated_code=complex_ai_code,
                    strategy_type=strategy,
                    dry_run=True,  # Always dry run for testing
                    preserve_patterns=True,
                    maintain_quality=True
                )
                
                print(result)
                print()
        
        except Exception as e:
            print(f"❌ Professional merger test failed: {e}")
            print()


def create_sophisticated_test_codebase(temp_path: Path):
    """Create a sophisticated test codebase with various patterns."""
    
    # Create directory structure
    (temp_path / "models").mkdir(parents=True)
    (temp_path / "services").mkdir(parents=True)
    (temp_path / "repositories").mkdir(parents=True)
    (temp_path / "controllers").mkdir(parents=True)
    (temp_path / "utils").mkdir(parents=True)
    
    # Create model files
    (temp_path / "models" / "__init__.py").write_text("")
    (temp_path / "models" / "user_model.py").write_text('''
"""User model definition."""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class User:
    """User data model."""
    id: str
    username: str
    email: str
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    
    def to_dict(self) -> dict:
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "is_active": self.is_active
        }
''')
    
    # Create service files
    (temp_path / "services" / "__init__.py").write_text("")
    (temp_path / "services" / "user_service.py").write_text('''
"""User service for business logic."""

from typing import Dict, Any, Optional
from models.user_model import User
from repositories.user_repository import UserRepository

class UserService:
    """Service for user-related operations."""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository
    
    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user."""
        # Basic validation
        if not user_data.get("email") or not user_data.get("username"):
            raise ValueError("Email and username are required")
        
        # Create user through repository
        return await self.user_repo.create(user_data)
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return await self.user_repo.get_by_id(user_id)
    
    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> User:
        """Update user information."""
        return await self.user_repo.update(user_id, updates)
''')
    
    # Create repository files
    (temp_path / "repositories" / "__init__.py").write_text("")
    (temp_path / "repositories" / "user_repository.py").write_text('''
"""User repository for data access."""

from typing import Dict, Any, Optional, List
from models.user_model import User
from datetime import datetime

class UserRepository:
    """Repository for user data access."""
    
    def __init__(self, database_connection):
        self.db = database_connection
    
    async def create(self, user_data: Dict[str, Any]) -> User:
        """Create a new user in the database."""
        user_id = await self.db.insert("users", user_data)
        return User(
            id=user_id,
            username=user_data["username"],
            email=user_data["email"],
            created_at=datetime.utcnow()
        )
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        data = await self.db.select("users", {"id": user_id})
        if data:
            return User(**data)
        return None
    
    async def update(self, user_id: str, updates: Dict[str, Any]) -> User:
        """Update user data."""
        await self.db.update("users", {"id": user_id}, updates)
        return await self.get_by_id(user_id)
    
    async def delete(self, user_id: str) -> bool:
        """Delete user."""
        return await self.db.delete("users", {"id": user_id})
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        data = await self.db.select("users", {"email": email})
        if data:
            return User(**data)
        return None
''')
    
    # Create controller files
    (temp_path / "controllers" / "__init__.py").write_text("")
    (temp_path / "controllers" / "user_controller.py").write_text('''
"""User controller for handling HTTP requests."""

from typing import Dict, Any
from services.user_service import UserService

class UserController:
    """Controller for user-related endpoints."""
    
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    async def create_user_endpoint(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user creation request."""
        try:
            user = await self.user_service.create_user(request_data)
            return {"success": True, "user": user.to_dict()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_user_endpoint(self, user_id: str) -> Dict[str, Any]:
        """Handle get user request."""
        user = await self.user_service.get_user(user_id)
        if user:
            return {"success": True, "user": user.to_dict()}
        return {"success": False, "error": "User not found"}
''')


if __name__ == "__main__":
    print("🚀 Professional SWE-Level Capabilities Test Suite")
    print("=" * 55)
    print()
    
    # Test code comprehension
    test_code_comprehension()

    # Test intelligent merger
    test_intelligent_merger()
    
    print("🎉 Professional SWE-Level Test Suite Completed!")
