import math

class RiskManager:
    """
    Handles risk management including position sizing, stop losses, and drawdown triggers.
    """

    def __init__(self, risk_per_trade: float = 0.02, max_drawdown_limit: float = 0.10):
        self.risk_per_trade = risk_per_trade
        self.max_drawdown_limit = max_drawdown_limit

    def calculate_position_size(self, equity: float, price: float, stop_loss_pct: float) -> int:
        """
        Calculates number of shares using the fixed percentage risk rule.
        Risk Amount = Equity * 0.02
        Risk Per Share = Price * StopLossPct
        Shares = Risk Amount / Risk Per Share
        """
        if price <= 0 or stop_loss_pct <= 0:
            return 0
            
        risk_amount = equity * self.risk_per_trade
        risk_per_share = price * stop_loss_pct
        
        shares = risk_amount / risk_per_share
        return math.floor(shares)

    def is_stop_loss_triggered(self, avg_cost: float, current_price: float, stop_loss_pct: float) -> bool:
        """ Checks if the current price dropped below the stop loss level. """
        if avg_cost <= 0:
            return False
        sl_price = avg_cost * (1 - stop_loss_pct)
        return current_price < sl_price

    def check_drawdown_halt(self, current_equity: float, peak_equity: float) -> bool:
        """ Checks if trading should halt due to excessive drawdown from peak. """
        if peak_equity <= 0:
            return False
            
        drawdown = (peak_equity - current_equity) / peak_equity
        return drawdown >= self.max_drawdown_limit

if __name__ == "__main__":
    # Test sizing
    rm = RiskManager()
    equity = 100000
    price = 200
    sl_pct = 0.05 # 5% SL
    # Risk = 2000. Risk per share = 10. Shares = 200.
    print(f"Shares to buy: {rm.calculate_position_size(equity, price, sl_pct)}")
    
    # Test SL
    print(f"SL Triggered: {rm.is_stop_loss_triggered(200, 189, 0.05)}") # 190 is SL
    
    # Test Halt
    print(f"Halt Trading: {rm.check_drawdown_halt(89000, 100000)}") # 11% DD
