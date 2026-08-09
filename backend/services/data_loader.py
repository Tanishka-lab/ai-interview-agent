"""
data_loader.py
---------------
Loads curriculum.json and candidates.json once at app startup.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class DataLoader:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.curriculum: Dict[str, Any] = {}
        self.candidates: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        try:
            with open(self.data_dir / "curriculum.json", "r") as f:
                self.curriculum = json.load(f)
        except FileNotFoundError:
            print(f"Warning: curriculum.json not found in {self.data_dir}/")
            self.curriculum = {"days": [], "modules": []}

        try:
            with open(self.data_dir / "candidates.json", "r") as f:
                self.candidates = json.load(f).get("candidates", [])
        except FileNotFoundError:
            print(f"Warning: candidates.json not found in {self.data_dir}/")
            self.candidates = []

    def get_all_candidates(self) -> List[Dict[str, Any]]:
        return self.candidates

    def get_candidate(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        for c in self.candidates:
            if c.get("member", {}).get("id") == candidate_id:
                return c
        return None