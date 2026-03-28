import json
import os
from typing import List, Dict, Any, Optional

class SignalPersistence:
    """
    Handles persisting and retrieving trading signals between sessions.
    Used to decouple heavy scanning (market close) from morning alerts (market open).
    """
    def __init__(self, storage_path: str = "data/pending_signals.json"):
        self.storage_path = storage_path
        self._ensure_storage()

    def _ensure_storage(self):
        """ Creates directory and file if they don't exist. """
        directory = os.path.dirname(self.storage_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump({}, f)

    def save_signals(self, pipeline: str, candidates: List[Dict[str, Any]]):
        """ Saves signals for a specific pipeline with timestamp. """
        from datetime import datetime
        data = self.load_all()
        data[pipeline.lower()] = {
            "timestamp": datetime.now().isoformat(),
            "candidates": candidates
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=4)

    def load_signals(self, pipeline: str) -> List[Dict[str, Any]]:
        """ Retrieves saved signals for a specific pipeline. """
        data = self.load_all()
        pipeline_data = data.get(pipeline.lower(), {})
        return pipeline_data.get("candidates", [])

    def load_all(self) -> Dict[str, Any]:
        """ Reads the entire persistence file. """
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def clear(self, pipeline: Optional[str] = None):
        """ Clears signals for one or all pipelines. """
        if pipeline:
            data = self.load_all()
            if pipeline.lower() in data:
                del data[pipeline.lower()]
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=4)
        else:
            with open(self.storage_path, 'w') as f:
                json.dump({}, f)
