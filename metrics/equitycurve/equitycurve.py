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
def resample_equity_curve(
    equity_curve: pd.DataFrame,
    freq: str = "D"
) -> pd.DataFrame:
    """
    Resample equity curve to a different time frequency.
    
    This is useful for calculating daily/weekly/monthly returns
    from a trade-by-trade equity curve.
    
    Args:
        equity_curve: Output from to_equity_curve()
        freq: Pandas frequency string:
              'D' = daily, 'W' = weekly, 'M' = monthly
              
    Returns:
        Resampled equity curve with period returns
        
    Example:
        >>> daily_equity = resample_equity_curve(equity, freq="D")
        >>> monthly_equity = resample_equity_curve(equity, freq="M")
    """
    if len(equity_curve) == 0:
        return equity_curve
    
    # Set timestamp as index for resampling
    df = equity_curve.set_index("timestamp")
    
    # Resample to desired frequency, taking the last balance of each period
    resampled = df.resample(freq).agg({
        "balance": "last",
        "pnl": "sum",  # Sum all PnL within the period
        "returns": lambda x: ((1 + x/100).prod() - 1) * 100  # Compound returns
    })
    
    # Forward fill missing periods (days with no trades)
    resampled["balance"] = resampled["balance"].ffill()
    resampled["pnl"] = resampled["pnl"].fillna(0)
    
    # Recalculate returns based on period balance changes
    resampled["period_returns"] = resampled["balance"].pct_change() * 100
    
    # Calculate cumulative returns for the resampled curve
    starting_balance = equity_curve["balance"].iloc[0] - equity_curve["pnl"].iloc[0]
    resampled["cumulative_returns"] = (
        (resampled["balance"] - starting_balance) / starting_balance * 100
    )
    
    return resampled.reset_index()