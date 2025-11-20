import pandas as pd
from pathlib import Path

def to_equity_curve(df, starting_balance: float = 10000.0) -> pd.DataFrame:
        """
        Convert trade log to equity curve for metric calculations.
        
        Args:
            df: Validated trade log DataFrame with at least 'timestamp_exit' and 'pnl' columns
            starting_balance: Initial account balance
            
        Returns:
            DataFrame with columns:
                - timestamp: Exit timestamp of each trade
                - balance: Cumulative balance after each trade
                - pnl: P&L of each trade
                - returns: Percentage return of each trade
        """
        # Sort by exit time to build chronological equity curve
        df_sorted = df.sort_values("timestamp_exit").reset_index(drop=True)
        
        # Calculate cumulative balance
        cumulative_pnl = df_sorted["pnl"].cumsum()
        balance = starting_balance + cumulative_pnl
        
        # Calculate returns (percentage change in balance)
        prev_balance = starting_balance + cumulative_pnl.shift(1).fillna(0)
        returns = (df_sorted["pnl"] / prev_balance) * 100
        
        equity_curve = pd.DataFrame({
            "timestamp": df_sorted["timestamp_exit"],
            "balance": balance,
            "pnl": df_sorted["pnl"],
            "returns": returns
        })
        
        return equity_curve