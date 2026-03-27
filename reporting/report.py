import os
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from typing import Dict, Any

class ReportGenerator:
    """
    Generates visual and tabular performance reports.
    Exports to premium HTML with modern styling.
    """

    def __init__(self, output_dir: str = "reporting/exports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        # Use a non-interactive backend for matplotlib
        plt.switch_backend('Agg')

    def generate_equity_curve(self, equity_series: pd.Series) -> str:
        """ Plots equity curve and returns it as a base64 string. """
        plt.figure(figsize=(12, 6))
        plt.style.use('dark_background')
        
        plt.plot(equity_series, label='Total Equity', color='#00f2ff', linewidth=2)
        plt.fill_between(equity_series.index, equity_series, alpha=0.1, color='#00f2ff')
        
        plt.title('Equity Curve Performance', fontsize=16, color='white', pad=20)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Equity ($)', fontsize=12)
        plt.grid(True, alpha=0.2, linestyle='--')
        plt.legend()
        
        # Save to buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        
        return base64.b64encode(buf.getvalue()).decode('utf-8')

    def generate_html_report(self, metrics: Dict[str, Any], trade_log: pd.DataFrame, equity_series: pd.Series, filename: str = "report.html"):
        """ Generates a premium standalone HTML report. """
        plot_b64 = self.generate_equity_curve(equity_series)
        
        # UI Styling (Glassmorphism / Dark Mode)
        css = """
        :root {
            --bg: #0b0e14;
            --surface: #161b22;
            --accent: #00f2ff;
            --text-primary: #e6edf3;
            --text-secondary: #8b949e;
            --success: #3fb950;
            --error: #f85149;
            --glass: rgba(22, 27, 34, 0.7);
        }
        body {
            background-color: var(--bg);
            color: var(--text-primary);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            margin: 0;
            padding: 40px;
            line-height: 1.6;
        }
        .container {
            max-width: 1100px;
            margin: 0 auto;
        }
        header {
            margin-bottom: 40px;
            text-align: center;
        }
        h1 { font-weight: 300; letter-spacing: 2px; color: var(--accent); }
        .card {
            background: var(--glass);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        .metric-item {
            text-align: center;
        }
        .metric-value {
            font-size: 24px;
            font-weight: 700;
            color: var(--accent);
            display: block;
        }
        .metric-label {
            font-size: 12px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .plot-container img {
            width: 100%;
            border-radius: 12px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th {
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding: 12px;
            color: var(--text-secondary);
            font-weight: 500;
            font-size: 13px;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            font-size: 14px;
        }
        .status-success { color: var(--success); }
        .status-error { color: var(--error); }
        """

        # Build Metrics HTML
        metrics_html = "".join([
            f'<div class="metric-item"><span class="metric-value">{v}</span><span class="metric-label">{k.replace("_", " ")}</span></div>'
            for k, v in metrics.items()
        ])

        # Build Trade Log HTML
        trades_html = ""
        if not trade_log.empty:
            trades_html = trade_log.to_html(classes='trade-table', border=0, index=False)
            # Custom status coloring
            trades_html = trades_html.replace('SUCCESS', '<span class="status-success">SUCCESS</span>')
            trades_html = trades_html.replace('FAILED', '<span class="status-error">FAILED</span>')

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Glu-Stock Performance Report</title>
            <style>{css}</style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>GLU-STOCK TRADING REPORT</h1>
                    <p style="color: var(--text-secondary)">Performance Analytics & Trade History</p>
                </header>
                
                <div class="card metrics-grid">
                    {metrics_html}
                </div>
                
                <div class="card plot-container">
                    <img src="data:image/png;base64,{plot_b64}" alt="Equity Curve">
                </div>
                
                <div class="card">
                    <h3 style="margin-top: 0; font-weight: 400; color: var(--accent)">Recent Trade History</h3>
                    <div style="overflow-x: auto;">
                        {trades_html}
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        output_path = os.path.join(self.output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"ReportGenerator: HTML report generated at {output_path}")

if __name__ == "__main__":
    # Quick sanity check
    rg = ReportGenerator()
    dummy_equity = pd.Series([100, 110, 105, 120, 115, 130])
    dummy_metrics = {"Total_Return": "30%", "Sharpe_Ratio": "1.8", "Max_Drawdown": "5%"}
    dummy_trades = pd.DataFrame({
        "timestamp": ["2024-01-01", "2024-01-02"],
        "ticker": ["AAPL", "TSLA"],
        "action": ["BUY", "SELL"],
        "status": ["SUCCESS", "SUCCESS"]
    })
    rg.generate_html_report(dummy_metrics, dummy_trades, dummy_equity)
