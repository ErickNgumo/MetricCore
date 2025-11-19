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


def _compute_streaks(series: pd.Series) -> list:
    """
    Helper function to compute consecutive streaks in a boolean series.
    
    Args:
        series: Boolean series (True = win, False = loss)
        
    Returns:
        List of streak lengths
    """
    if len(series) == 0:
        return []
    
    # Convert to numpy for efficient computation
    arr = series.values
    
    # Find where values change
    changes = np.concatenate(([True], arr[1:] != arr[:-1], [True]))
    change_indices = np.where(changes)[0]
    
    # Calculate streak lengths
    streaks = np.diff(change_indices)
    
    # Get the actual values at streak starts
    streak_values = arr[change_indices[:-1]]
    
    return list(zip(streak_values, streaks))


def longest_win_streak(df: pd.DataFrame) -> int:
    """
    Return the longest consecutive series of winning trades.
    
    Args:
        df: Validated trade log DataFrame with 'pnl' column
        
    Returns:
        Maximum number of consecutive winning trades
        
    Example:
        >>> longest_win_streak(df)
        7  # Had 7 wins in a row at best
    """
    if len(df) == 0:
        return 0
    
    # Sort by exit timestamp to get chronological order
    if 'timestamp_exit' in df.columns:
        df_sorted = df.sort_values('timestamp_exit')
    else:
        df_sorted = df
    
    # Drop breakeven trades for win streak calculation    
    filtered = df_sorted[df_sorted['pnl'] != 0]
    if len(filtered) == 0:
        return 0
    
    is_win = df_sorted['pnl'] > 0
    streaks = _compute_streaks(is_win)
    
    win_streaks = [length for is_w, length in streaks if is_w]
    
    return max(win_streaks) if win_streaks else 0


def longest_loss_streak(df: pd.DataFrame) -> int:
    """
    Return the longest consecutive series of losing trades.
    
    This is your "emotional drawdown" metric — how many losses in a row
    you need to stomach before the next win arrives.
    
    Args:
        df: Validated trade log DataFrame with 'pnl' column
        
    Returns:
        Maximum number of consecutive losing trades
        
    Example:
        >>> longest_loss_streak(df)
        5  # Worst streak was 5 losses in a row
    """
    if len(df) == 0:
        return 0
    
    # Sort by exit timestamp to get chronological order
    if 'timestamp_exit' in df.columns:
        df_sorted = df.sort_values('timestamp_exit')
    else:
        df_sorted = df
    
    #Drop breakeven trades for loss streak calculation    
    filtered = df_sorted[df_sorted['pnl'] != 0]
    if len(filtered) == 0:
        return 0
    
    is_loss = df_sorted['pnl'] < 0
    streaks = _compute_streaks(is_loss)
    
    loss_streaks = [length for is_l, length in streaks if is_l]
    
    return max(loss_streaks) if loss_streaks else 0


def streak_distribution(df: pd.DataFrame) -> Dict[str, Dict[int, int]]:
    """
    Get the distribution of win and loss streaks.
    
    This shows how often you experience streaks of different lengths.
    
    Args:
        df: Validated trade log DataFrame with 'pnl' column
        
    Returns:
        Dictionary with 'wins' and 'losses' keys, each containing
        a dictionary mapping streak length to frequency
        
    Example:
        >>> streak_distribution(df)
        {
            'wins': {1: 15, 2: 8, 3: 4, 5: 1},  # Had one 5-win streak
            'losses': {1: 12, 2: 5, 3: 2}
        }
    """
    if len(df) == 0:
        return {'wins': {}, 'losses': {}}
    
    # Sort by exit timestamp
    if 'timestamp_exit' in df.columns:
        df_sorted = df.sort_values('timestamp_exit')
    else:
        df_sorted = df
    
    # remove breakevens
    filtered = df_sorted[df_sorted['pnl'] != 0]
    if len(filtered) == 0:
        return {'wins': {}, 'losses': {}}
    
    is_win = df_sorted['pnl'] > 0
    streaks = _compute_streaks(is_win)
    
    win_streaks = [length for is_w, length in streaks if is_w]
    loss_streaks = [length for is_w, length in streaks if not is_w]
    
    # Count frequencies
    win_dist = pd.Series(win_streaks).value_counts().to_dict() if win_streaks else {}
    loss_dist = pd.Series(loss_streaks).value_counts().to_dict() if loss_streaks else {}
    
    return {
        'wins': dict(sorted(win_dist.items())),
        'losses': dict(sorted(loss_dist.items()))
    }


def win_loss_ratio(df: pd.DataFrame) -> float:
    """
    Ratio of average win to absolute average loss.
    
    Also known as the payoff ratio or reward-to-risk ratio.
    
    Args:
        df: Validated trade log DataFrame with 'pnl' column
        
    Returns:
        Ratio of avg_win / abs(avg_loss). Returns inf if no losses.
        
    Example:
        >>> win_loss_ratio(df)
        2.0  # Average win is 2x the size of average loss
    """
    avg_w = average_win(df)
    avg_l = average_loss(df)
    
    if avg_l == 0:
        return float('inf') if avg_w > 0 else 0.0
    
    return avg_w / abs(avg_l)


def summary(df: pd.DataFrame) -> Dict[str, float]:
    """
    Generate a comprehensive win/loss summary report.
    
    Args:
        df: Validated trade log DataFrame with 'pnl' column
        
    Returns:
        Dictionary containing all key win/loss metrics
        
    Example:
        >>> summary(df)
        {
            'total_trades': 100,
            'win_rate': 0.60,
            'loss_rate': 0.35,
            'breakeven_rate': 0.05,
            'average_win': 250.0,
            'average_loss': -150.0,
            'expectancy': 97.5,
            'profit_factor': 2.14,
            'win_loss_ratio': 1.67,
            'longest_win_streak': 8,
            'longest_loss_streak': 5
        }
    """
    return {
        'total_trades': len(df),
        'win_rate': win_rate(df),
        'loss_rate': loss_rate(df),
        'breakeven_rate': breakeven_rate(df),
        'average_win': average_win(df),
        'average_loss': average_loss(df),
        'expectancy': expectancy(df),
        'profit_factor': profit_factor(df),
        'win_loss_ratio': win_loss_ratio(df),
        'longest_win_streak': longest_win_streak(df),
        'longest_loss_streak': longest_loss_streak(df)
    }