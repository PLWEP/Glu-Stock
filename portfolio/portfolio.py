from typing import Dict, Optional

class Portfolio:
    """
    Manages active positions, cash balance, and calculates equity and PnL.
    """

    def __init__(self, initial_cash: float = 100000.0):
        self.cash = initial_cash
        self.positions: Dict[str, Dict[str, float]] = {}
        self.realized_pnl = 0.0

    def update_position(self, ticker: str, shares: float, price: float, action: str) -> bool:
        """
        Updates the portfolio based on a trade action (BUY/SELL).
        """
        action = action.upper()
        if action == "BUY":
            cost = shares * price
            if cost > self.cash:
                print(f"Insufficient cash for {ticker}: {self.cash} < {cost}")
                return False
            
            # Update Position
            if ticker not in self.positions:
                self.positions[ticker] = {"shares": 0.0, "avg_cost": 0.0}
            
            current = self.positions[ticker]
            new_shares = current["shares"] + shares
            new_avg_cost = ((current["shares"] * current["avg_cost"]) + (shares * price)) / new_shares
            
            self.positions[ticker]["shares"] = new_shares
            self.positions[ticker]["avg_cost"] = new_avg_cost
            self.cash -= cost
            return True

        elif action == "SELL":
            if ticker not in self.positions or self.positions[ticker]["shares"] < shares:
                print(f"Insufficient shares to sell {ticker}")
                return False
            
            current = self.positions[ticker]
            # Calculate Realized PnL
            sale_gain = shares * (price - current["avg_cost"])
            self.realized_pnl += sale_gain
            
            # Update Position
            self.positions[ticker]["shares"] -= shares
            self.cash += (shares * price)
            
            if self.positions[ticker]["shares"] == 0:
                del self.positions[ticker]
            return True
            
        return False

    def get_equity(self, current_prices: Dict[str, float]) -> float:
        """ Calculates total equity (cash + market value). """
        position_value = 0.0
        for ticker, pos in self.positions.items():
            if ticker in current_prices:
                position_value += pos["shares"] * current_prices[ticker]
        return self.cash + position_value

    def get_unrealized_pnl(self, current_prices: Dict[str, float]) -> float:
        """ Calculates total unrealized PnL based on current prices. """
        upnl = 0.0
        for ticker, pos in self.positions.items():
            if ticker in current_prices:
                upnl += pos["shares"] * (current_prices[ticker] - pos["avg_cost"])
        return upnl

    def get_total_pnl(self, current_prices: Dict[str, float]) -> float:
        """ Sum of realized and unrealized PnL. """
        return self.realized_pnl + self.get_unrealized_pnl(current_prices)

if __name__ == "__main__":
    # Sanity check
    p = Portfolio(10000)
    p.update_position("AAPL", 10, 150, "BUY")
    print(f"Cash after BUY: {p.cash}")
    print(f"Equity: {p.get_equity({'AAPL': 160})}")
    print(f"PnL: {p.get_total_pnl({'AAPL': 160})}")
    p.update_position("AAPL", 5, 170, "SELL")
    print(f"Realized PnL: {p.realized_pnl}")
    print(f"Cash after SELL: {p.cash}")
