import json
from typing import Dict, Any, List, Optional
from pathlib import Path

class DataLoader:
    """Loads and provides access to curriculum and candidate data"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.curriculum = None
        self.candidates = None
        self.load_data()
    
    def load_data(self):
        """Load both JSON files"""
        try:
            with open(self.data_dir / "curriculum.json", "r") as f:
                self.curriculum = json.load(f)
        except FileNotFoundError:
            print("Warning: curriculum.json not found")
            self.curriculum = {}
        
        try:
            with open(self.data_dir / "candidates.json", "r") as f:
                self.candidates = json.load(f)
        except FileNotFoundError:
            print("Warning: candidates.json not found")
            self.candidates = {"candidates": []}
    
    def get_candidate(self, candidate_id: str) -> Optional[Dict]:
        """Get a specific candidate by ID"""
        for candidate in self.candidates.get("candidates", []):
            if candidate.get("member", {}).get("id") == candidate_id:
                return candidate
        return None
    
    def get_all_candidates(self) -> List[Dict]:
        """Get all candidates"""
        return self.candidates.get("candidates", [])
    
    def get_day_details(self, day: int) -> Optional[Dict]:
        """Get details for a specific day from curriculum"""
        for day_data in self.curriculum.get("days", []):
            if day_data.get("day") == day:
                return day_data
        return None
    
    def get_topics_for_candidate(self, candidate_data: Dict) -> List[Dict]:
        """Get the topics a candidate completed"""
        missions = candidate_data.get("missions", [])
        topics = []
        
        for mission in missions:
            if mission.get("passed", False):
                day = mission.get("day")
                day_data = self.get_day_details(day)
                if day_data:
                    topics.append({
                        "day": day,
                        "title": mission.get("title"),
                        "attempts": mission.get("attempts", 0),
                        "objectives": day_data.get("objectives", []),
                        "tools": day_data.get("tools", [])
                    })
        
        return topics