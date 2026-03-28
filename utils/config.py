import yaml
import os
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

class ConfigLoader:
    """
    Handles loading, parsing, and validating YAML configuration files.
    Ensures trading parameters like capital and risk follow safety constraints.
    """

    DEFAULT_CONFIG = {
        "trading": {
            "capital": 100000000.0,
            "risk_per_trade": 0.02,
            "tickers": ["BBCA.JK", "TLKM.JK"]
        },
        "debug_mode": True
    }

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load()
        self.validate()

    def _load(self) -> Dict[str, Any]:
        """ Reads the YAML file or returns defaults if missing. """
        if not os.path.exists(self.config_path):
            print(f"ConfigLoader: {self.config_path} not found. Using defaults.")
            return self.DEFAULT_CONFIG
            
        with open(self.config_path, 'r') as f:
            try:
                data = yaml.safe_load(f)
                return data if data else self.DEFAULT_CONFIG
            except yaml.YAMLError as e:
                print(f"ConfigLoader: Error parsing YAML: {str(e)}. Using defaults.")
                return self.DEFAULT_CONFIG

    def validate(self):
        """ Enforces constraints on trading parameters. """
        trading = self.config.get("trading", {})
        
        capital = trading.get("capital")
        if not isinstance(capital, (int, float)) or capital <= 0:
            raise ValueError(f"ConfigLoader: Capital must be a positive number. Got: {capital}")
            
        risk = trading.get("risk_per_trade")
        if not isinstance(risk, (int, float)) or not (0 < risk < 1):
            raise ValueError(f"ConfigLoader: Risk per trade must be between 0 and 1. Got: {risk}")
            
        tickers = trading.get("tickers")
        if not isinstance(tickers, list) or len(tickers) == 0:
            raise ValueError("ConfigLoader: Tickers list must be provided and non-empty.")

    def get_trading_params(self) -> Dict[str, Any]:
        """ Returns the trading section of the configuration. """
        return self.config.get("trading", self.DEFAULT_CONFIG["trading"])

    def get_config(self) -> Dict[str, Any]:
        """ Returns the full configuration dictionary. """
        return self.config

if __name__ == "__main__":
    # Test loader
    loader = ConfigLoader()
    print(loader.get_trading_params())
