import pandas as pd
import numpy as np
from typing import Dict, Optional

def sharpe_ratio(
    equity_curve: pd.DataFrame,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252
) -> float:
    """
    Calculate the Sharpe Ratio (risk-adjusted return).
    
    Sharpe Ratio = (Average Return - Risk Free Rate) / Standard Deviation of Returns
    
    Measures return per unit of volatility. Higher is better.
    - < 1.0: Poor
    - 1.0 - 2.0: Good
    - 2.0 - 3.0: Very Good
    - > 3.0: Excellent
    
    Args:
        equity_curve: DataFrame from to_equity_curve()
        risk_free_rate: Annual risk-free rate as decimal (e.g., 0.04 for 4%)
        periods_per_year: Trading periods per year (252 for daily, 52 for weekly)
        
    Returns:
        Annualized Sharpe ratio
        
    Example:
        >>> sharpe = sharpe_ratio(equity, risk_free_rate=0.02)
        >>> print(f"Sharpe Ratio: {sharpe:.2f}")
    """
    if len(equity_curve) == 0:
        return 0.0
    
    returns = equity_curve['returns'].dropna()
    
    if len(returns) == 0 or returns.std() == 0:
        return 0.0
    
    # Convert risk-free rate to per-period rate
    rf_per_period = (1 + risk_free_rate) ** (1 / periods_per_year) - 1
    rf_per_period_pct = rf_per_period * 100
    
    # Calculate excess returns
    excess_returns = returns - rf_per_period_pct
    
    # Annualize
    avg_excess_return = excess_returns.mean()
    std_return = returns.std()
    
    sharpe = (avg_excess_return / std_return) * np.sqrt(periods_per_year)
    
    return sharpe


def sortino_ratio(
    equity_curve: pd.DataFrame,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
    target_return: Optional[float] = None
) -> float:
    """
    Calculate the Sortino Ratio (downside risk-adjusted return).
    
    Sortino Ratio = (Average Return - Target Return) / Downside Deviation
    
    Similar to Sharpe but only penalizes downside volatility, not upside.
    This is often more meaningful for traders since upside volatility is good.
    
    Args:
        equity_curve: DataFrame from to_equity_curve()
        risk_free_rate: Annual risk-free rate as decimal
        periods_per_year: Trading periods per year
        target_return: Minimum acceptable return (defaults to risk_free_rate)
        
    Returns:
        Annualized Sortino ratio
        
    Example:
        >>> sortino = sortino_ratio(equity)
        >>> print(f"Sortino Ratio: {sortino:.2f}")
    """
    if len(equity_curve) == 0:
        return 0.0
    
    returns = equity_curve['returns'].dropna()
    
    if len(returns) == 0:
        return 0.0
    
    # Use risk-free rate as target if not specified
    if target_return is None:
        rf_per_period = (1 + risk_free_rate) ** (1 / periods_per_year) - 1
        target_return = rf_per_period * 100
    
    # Calculate downside deviation (only negative returns)
    downside_returns = returns[returns < target_return]
    
    if len(downside_returns) == 0:
        return float('inf') if returns.mean() > target_return else 0.0
    
    downside_deviation = np.sqrt(((downside_returns - target_return) ** 2).mean())
    
    if downside_deviation == 0:
        return float('inf') if returns.mean() > target_return else 0.0
    
    # Annualize
    avg_return = returns.mean()
    sortino = ((avg_return - target_return) / downside_deviation) * np.sqrt(periods_per_year)
    
    return sortino


def calmar_ratio(
    equity_curve: pd.DataFrame,
    periods_per_year: int = 252
) -> float:
    """
    Calculate the Calmar Ratio (Annual Return / Maximum Drawdown).
    
    Measures return per unit of drawdown risk. Higher is better.
    - < 1.0: Poor
    - 1.0 - 3.0: Good
    - 3.0 - 5.0: Very Good
    - > 5.0: Excellent
    
    Args:
        equity_curve: DataFrame from to_equity_curve()
        periods_per_year: Number of trading periods per year
        
    Returns:
        Calmar ratio as a float
        
    Example:
        >>> calmar = calmar_ratio(equity)
        >>> print(f"Calmar Ratio: {calmar:.2f}")
    """
    if len(equity_curve) == 0:
        return 0.0
    
    # Calculate annualized return
    starting_balance = equity_curve['balance'].iloc[0] - equity_curve['pnl'].iloc[0]
    ending_balance = equity_curve['balance'].iloc[-1]
    total_return = (ending_balance - starting_balance) / starting_balance
    
    num_periods = len(equity_curve)
    years = num_periods / periods_per_year
    
    if years <= 0:
        return 0.0
    
    annualized_return = (1 + total_return) ** (1 / years) - 1
    
    # Calculate max drawdown
    from metrics import maximum_drawdown
    max_dd = maximum_drawdown(equity_curve)
    max_dd_pct = abs(max_dd['max_drawdown_pct'])
    
    if max_dd_pct == 0:
        return float('inf') if annualized_return > 0 else 0.0
    
    return (annualized_return * 100) / max_dd_pct


def recovery_factor(equity_curve: pd.DataFrame) -> float:
    """
    Calculate Recovery Factor (Net Profit / Maximum Drawdown).
    
    Measures how many times the strategy recovered from its worst drawdown.
    Higher is better.
    - < 1.0: Poor (lost more than gained)
    - 1.0 - 2.0: Acceptable
    - 2.0 - 3.0: Good
    - > 3.0: Excellent
    
    Args:
        equity_curve: DataFrame from to_equity_curve()
        
    Returns:
        Recovery factor as a float
        
    Example:
        >>> rf = recovery_factor(equity)
        >>> print(f"Recovery Factor: {rf:.2f}")
    """
    if len(equity_curve) == 0:
        return 0.0
    
    net_profit = equity_curve['pnl'].sum()
    
    from metrics import maximum_drawdown
    max_dd = maximum_drawdown(equity_curve)
    max_dd_amount = abs(max_dd['max_drawdown_amount'])
    
    if max_dd_amount == 0:
        return float('inf') if net_profit > 0 else 0.0
    
    return net_profit / max_dd_amount