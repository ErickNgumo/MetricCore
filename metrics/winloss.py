import pandas as pd
import numpy as np
from typing import Dict, Optional

def win_rate(df: pd.DataFrame) -> float:
    """
    Return the fraction of trades with pnl > 0.
    
    Args:
        df: Validated trade log DataFrame with 'pnl' column
        
    Returns:
        Win rate as a decimal (0.0 to 1.0)
        
    Example:
        >>> win_rate(df)  # 60% win rate
        0.60
    """
    if len(df) == 0:
        return 0.0
    
    winning_trades = (df['pnl'] > 0).sum()
    return winning_trades / len(df)


def loss_rate(df: pd.DataFrame) -> float:
    """
    Return the fraction of trades with pnl < 0.
    
    Args:
        df: Validated trade log DataFrame with 'pnl' column
        
    Returns:
        Loss rate as a decimal (0.0 to 1.0)
        
    Example:
        >>> loss_rate(df)  # 35% loss rate
        0.35
    """
    if len(df) == 0:
        return 0.0
    
    losing_trades = (df['pnl'] < 0).sum()
    return losing_trades / len(df)


def breakeven_rate(df: pd.DataFrame) -> float:
    """
    Return the fraction of trades with pnl == 0.
    
    Args:
        df: Validated trade log DataFrame with 'pnl' column
        
    Returns:
        Breakeven rate as a decimal (0.0 to 1.0)
    """
    if len(df) == 0:
        return 0.0
    
    breakeven_trades = (df['pnl'] == 0).sum()
    return breakeven_trades / len(df)


def average_win(df: pd.DataFrame) -> float:
    """
    Mean PnL of winning trades only.
    
    Args:
        df: Validated trade log DataFrame with 'pnl' column
        
    Returns:
        Average profit of winning trades. Returns 0.0 if no winning trades.
        
    Example:
        >>> average_win(df)
        250.75
    """
    wins = df[df['pnl'] > 0]['pnl']
    
    if len(wins) == 0:
        return 0.0
    
    return wins.mean()


def average_loss(df: pd.DataFrame) -> float:
    """
    Mean PnL of losing trades only.
    
    Args:
        df: Validated trade log DataFrame with 'pnl' column
        
    Returns:
        Average loss of losing trades (negative number). 
        Returns 0.0 if no losing trades.
        
    Example:
        >>> average_loss(df)
        -125.50
    """
    losses = df[df['pnl'] < 0]['pnl']
    
    if len(losses) == 0:
        return 0.0
    
    return losses.mean()


def expectancy(df: pd.DataFrame) -> float:
    """
    Expected profit per trade.
    
    This is the theoretical average profit you'd expect from any random trade,
    accounting for both win rate and the asymmetry between wins and losses.
    
    Formula: (win_rate * avg_win) + (loss_rate * avg_loss)
    
    Args:
        df: Validated trade log DataFrame with 'pnl' column
        
    Returns:
        Expected profit per trade in account currency
        
    Example:
        >>> expectancy(df)  # Expect to make $45 per trade on average
        45.25
    """
    if len(df) == 0:
        return 0.0
    
    wr = win_rate(df)
    lr = loss_rate(df)
    avg_w = average_win(df)
    avg_l = average_loss(df)
    
    return (wr * avg_w) + (lr * avg_l)


def profit_factor(df: pd.DataFrame) -> float:
    """
    Profit Factor = total winning PnL / absolute total losing PnL.
    
    A profit factor > 1.0 means the strategy is profitable.
    - PF = 1.0: Breakeven
    - PF > 1.0: Profitable (e.g., 2.0 = wins are 2x the size of losses)
    - PF < 1.0: Unprofitable
    
    Args:
        df: Validated trade log DataFrame with 'pnl' column
        
    Returns:
        Profit factor as a ratio. Returns inf if no losing trades,
        and 0.0 if no winning trades.
        
    Example:
        >>> profit_factor(df)
        1.85  # Wins are 1.85x larger than losses
    """
    total_wins = df[df['pnl'] > 0]['pnl'].sum()
    total_losses = df[df['pnl'] < 0]['pnl'].sum()
    
    # Edge cases
    if total_losses == 0:
        return float('inf') if total_wins > 0 else 0.0
    
    if total_wins == 0:
        return 0.0
    
    return total_wins / abs(total_losses)
