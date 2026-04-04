import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
from typing import List, Dict, Any, Optional
import os

class FirebaseHandler:
    """
    Unified handler for Firebase Realtime Database.
    Replaces TradingDatabase and HistoryManager for cloud synchronization.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._initialize_firebase()
        self.root_ref = db.reference("glu_stock")

    def _initialize_firebase(self):
        """Initializes Firebase Admin SDK."""
        if not firebase_admin._apps:
            cert_path = self.config.get("service_account_path", "firebase_key.json")
            if not os.path.exists(cert_path):
                # Fallback to dummy or raise error in production
                print(f"[WARNING] Firebase key {cert_path} not found. Using local mock/offline mode.")
                # For now, we assume the user will provide the key.
            
            cred = credentials.Certificate(cert_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': self.config.get("database_url")
            })

    # --- TradingDatabase Interface ---
    def insert_trade(self, trade_data: Dict[str, Any]):
        trade_data['status'] = 'OPEN'
        if 'entry_date' not in trade_data:
            trade_data['entry_date'] = datetime.now().isoformat()
        self.root_ref.child("trades").push(trade_data)

    def update_trade_close(self, ticker: str, exit_price: float, pnl: float):
        trades = self.root_ref.child("trades").get()
        if not trades: return
        
        for tid, data in trades.items():
            if data.get('ticker') == ticker and data.get('status') == 'OPEN':
                self.root_ref.child(f"trades/{tid}").update({
                    'exit_price': exit_price,
                    'exit_date': datetime.now().isoformat(),
                    'pnl': pnl,
                    'status': 'CLOSED'
                })
                break

    def get_all_trades(self) -> List[Dict[str, Any]]:
        trades = self.root_ref.child("trades").get()
        if not trades: return []
        # Convert dict to list and sort by entry_date
        trade_list = [dict(v, id=k) for k, v in trades.items()]
        return sorted(trade_list, key=lambda x: x.get('entry_date', ''), reverse=True)

    def record_portfolio_snapshot(self, equity: float, cash: float, positions_value: float):
        snapshot = {
            'date': datetime.now().isoformat(),
            'equity': equity,
            'cash': cash,
            'positions_value': positions_value
        }
        self.root_ref.child("portfolio/history").push(snapshot)
        self.root_ref.child("portfolio/state").update({'cash': cash, 'equity': equity})

    # --- HistoryManager Interface ---
    def log_event(self, strategy: str, phase: str, ticker: str = "SYSTEM", 
                  metric: float = 0.0, status: str = "INFO", details: str = ""):
        event = {
            'timestamp': datetime.now().isoformat(),
            'strategy': strategy.lower(),
            'phase': phase.upper(),
            'ticker': ticker,
            'metric_value': metric,
            'status': status.upper(),
            'details': details
        }
        self.root_ref.child("history").push(event)

    def query_history(self, strategy: Optional[str] = None, 
                      ticker: Optional[str] = None, 
                      limit: int = 10) -> List[Dict[str, Any]]:
        history = self.root_ref.child("history").order_by_child("timestamp").limit_to_last(limit * 2).get()
        if not history: return []
        
        results = []
        for k, v in history.items():
            if strategy and v.get('strategy') != strategy.lower(): continue
            if ticker and v.get('ticker') != ticker.upper(): continue
            results.append(dict(v, id=k))
        
        return sorted(results, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.query_history(limit=limit)

    def count_open_positions(self) -> int:
        trades = self.root_ref.child("trades").get()
        if not trades: return 0
        return sum(1 for t in trades.values() if t.get('status') == 'OPEN')
