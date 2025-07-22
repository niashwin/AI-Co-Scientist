import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import aiofiles

class StorageManager:
    def __init__(self, data_dir: str = None, cache_dir: str = None):
        self.data_dir = Path(data_dir or os.getenv("DATA_DIR", "./data"))
        self.cache_dir = Path(cache_dir or os.getenv("CACHE_DIR", "./cache"))
        
        # Create directories
        self.data_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Subdirectories
        (self.data_dir / "sessions").mkdir(exist_ok=True)
        (self.data_dir / "hypotheses").mkdir(exist_ok=True)
        (self.cache_dir / "literature").mkdir(exist_ok=True)
    
    async def save_research_session(self, session_data: Dict[str, Any]) -> str:
        """Save a research session to storage"""
        session_id = session_data.get("id")
        if not session_id:
            raise ValueError("Session must have an ID")
        
        # Add timestamp
        session_data["last_updated"] = datetime.now().isoformat()
        
        file_path = self.data_dir / "sessions" / f"{session_id}.json"
        
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(json.dumps(session_data, indent=2, default=str))
        
        return str(file_path)
    
    async def load_research_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load a research session from storage"""
        file_path = self.data_dir / "sessions" / f"{session_id}.json"
        
        if not file_path.exists():
            return None
        
        try:
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
                return json.loads(content)
        except (json.JSONDecodeError, IOError):
            return None
    
    async def save_hypothesis(self, hypothesis_data: Dict[str, Any]) -> str:
        """Save a hypothesis to storage"""
        hypothesis_id = hypothesis_data.get("id")
        if not hypothesis_id:
            raise ValueError("Hypothesis must have an ID")
        
        # Add timestamp
        hypothesis_data["last_updated"] = datetime.now().isoformat()
        
        file_path = self.data_dir / "hypotheses" / f"{hypothesis_id}.json"
        
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(json.dumps(hypothesis_data, indent=2, default=str))
        
        return str(file_path)
    
    async def load_hypothesis(self, hypothesis_id: str) -> Optional[Dict[str, Any]]:
        """Load a hypothesis from storage"""
        file_path = self.data_dir / "hypotheses" / f"{hypothesis_id}.json"
        
        if not file_path.exists():
            return None
        
        try:
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
                return json.loads(content)
        except (json.JSONDecodeError, IOError):
            return None
    
    async def cache_literature_search(self, query: str, results: List[Dict[str, Any]]) -> None:
        """Cache literature search results"""
        # Create a safe filename from the query
        safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_query = safe_query.replace(' ', '_')[:50]  # Limit length
        
        cache_data = {
            "query": query,
            "results": results,
            "cached_at": datetime.now().isoformat(),
            "count": len(results)
        }
        
        file_path = self.cache_dir / "literature" / f"{safe_query}.json"
        
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(json.dumps(cache_data, indent=2, default=str))
    
    async def get_cached_literature(self, query: str, max_age_hours: int = 24) -> Optional[List[Dict[str, Any]]]:
        """Retrieve cached literature search results"""
        safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_query = safe_query.replace(' ', '_')[:50]
        
        file_path = self.cache_dir / "literature" / f"{safe_query}.json"
        
        if not file_path.exists():
            return None
        
        try:
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
                cache_data = json.loads(content)
            
            # Check if cache is still valid
            cached_at = datetime.fromisoformat(cache_data["cached_at"])
            age_hours = (datetime.now() - cached_at).total_seconds() / 3600
            
            if age_hours <= max_age_hours:
                return cache_data["results"]
            else:
                # Cache expired, remove file
                try:
                    file_path.unlink()
                except:
                    pass
                return None
                
        except (json.JSONDecodeError, IOError, KeyError):
            return None
    
    async def list_sessions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List all research sessions"""
        sessions = []
        session_dir = self.data_dir / "sessions"
        
        session_files = list(session_dir.glob("*.json"))
        # Sort by modification time, newest first
        session_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        for file_path in session_files[:limit]:
            try:
                async with aiofiles.open(file_path, 'r') as f:
                    content = await f.read()
                    session_data = json.loads(content)
                    sessions.append(session_data)
            except (json.JSONDecodeError, IOError):
                continue
        
        return sessions
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a research session"""
        file_path = self.data_dir / "sessions" / f"{session_id}.json"
        
        if file_path.exists():
            try:
                file_path.unlink()
                return True
            except:
                return False
        return False
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        sessions_count = len(list((self.data_dir / "sessions").glob("*.json")))
        hypotheses_count = len(list((self.data_dir / "hypotheses").glob("*.json")))
        cache_count = len(list((self.cache_dir / "literature").glob("*.json")))
        
        return {
            "sessions_count": sessions_count,
            "hypotheses_count": hypotheses_count,
            "cached_literature_count": cache_count,
            "data_directory": str(self.data_dir),
            "cache_directory": str(self.cache_dir)
        }
    
    def cleanup_old_cache(self, max_age_days: int = 7) -> int:
        """Clean up old cache files"""
        count = 0
        cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 3600)
        
        for file_path in (self.cache_dir / "literature").glob("*.json"):
            if file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink()
                    count += 1
                except:
                    pass
        
        return count

# Global storage instance
storage = StorageManager() 