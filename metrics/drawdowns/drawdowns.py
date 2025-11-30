import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional

def calculate_drawdown_series(equity_curve: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the drawdown series from an equity curve.
    
    Drawdown measures how far the balance has fallen from its previous peak.
    This is one of the most important risk metrics for trading strategies.
    
    Args:
        equity_curve: DataFrame from to_equity_curve() with 'balance' column
        
    Returns:
        DataFrame with additional columns:
            - peak: Running maximum balance
            - drawdown: Current drawdown from peak (negative %)
            - drawdown_pct: Drawdown as percentage
            - underwater: Boolean flag if currently in drawdown
            
    Example:
        >>> from metrics import to_equity_curve
        >>> from metrics import calculate_drawdown_series
        >>> 
        >>> equity = to_equity_curve(trades_df)
        >>> dd_series = calculate_drawdown_series(equity)
        >>> print(f"Max DD: {dd_series['drawdown_pct'].min():.2f}%")
    """
    
    df = equity_curve.copy()
    
    # Calculate running maximum (peak balance)
    df['peak'] = df['balance'].cummax()
    
    # Calculate drawdown in absolute terms
    df['drawdown'] = df['balance'] - df['peak']
    
    # Calculate drawdown as percentage from peak
    df['drawdown_pct'] = (df['drawdown'] / df['peak']) * 100
    
    # Flag if currently underwater (in drawdown)
    df['underwater'] = df['balance'] < df['peak']
    
    return df


def identify_drawdown_periods(equity_curve: pd.DataFrame) -> List[Dict]:
    """
    Identify individual drawdown periods from peak to recovery.
    
    A drawdown period starts when balance falls below the previous peak
    and ends when balance recovers to a new peak.
    
    Args:
        equity_curve: DataFrame from to_equity_curve()
        
    Returns:
        List of dictionaries, each containing:
            - start_idx: Index where drawdown started
            - end_idx: Index where drawdown ended (or None if ongoing)
            - start_date: Timestamp when drawdown started
            - end_date: Timestamp when recovered (or None)
            - peak_balance: Balance at the peak
            - trough_balance: Lowest balance during drawdown
            - max_drawdown: Maximum drawdown amount
            - max_drawdown_pct: Maximum drawdown percentage
            - duration: Number of trades in drawdown
            - recovered: Boolean if drawdown has recovered
            
    Example:
        >>> periods = identify_drawdown_periods(equity)
        >>> worst = max(periods, key=lambda x: abs(x['max_drawdown_pct']))
        >>> print(f"Worst DD: {worst['max_drawdown_pct']:.2f}% "
        ...       f"lasting {worst['duration']} trades")
    """
    dd_series = calculate_drawdown_series(equity_curve)
    
    periods = []
    in_drawdown = False
    current_period: = None

    
    for idx, row in dd_series.iterrows():
        if row['underwater'] and not in_drawdown:
            # Start of a new drawdown period
            in_drawdown = True
            current_period = {
                'start_idx': idx,
                'start_date': row['timestamp'],
                'peak_balance': row['peak'],
                'trough_balance': row['balance'],
                'max_drawdown': row['drawdown'],
                'max_drawdown_pct': row['drawdown_pct'],
            }
        
        elif row['underwater'] and in_drawdown:
            # Continuing drawdown - update if this is worse
            if row['drawdown'] < current_period['max_drawdown']:
                current_period['max_drawdown'] = row['drawdown']
                current_period['max_drawdown_pct'] = row['drawdown_pct']
                current_period['trough_balance'] = row['balance']
        
        elif not row['underwater'] and in_drawdown:
            # End of drawdown - recovered to new peak
            in_drawdown = False
            current_period['end_idx'] = idx
            current_period['end_date'] = row['timestamp']
            current_period['duration'] = idx - current_period['start_idx']
            current_period['recovered'] = True
            periods.append(current_period)
            current_period = None
    
    # If still in drawdown at the end
    if in_drawdown and current_period is not None:
        current_period['end_idx'] = None
        current_period['end_date'] = None
        current_period['duration'] = len(dd_series) - current_period['start_idx']
        current_period['recovered'] = False
        periods.append(current_period)
    
    return periods

def maximum_drawdown(equity_curve: pd.DataFrame) -> Dict:
    """
    Calculate the maximum drawdown and related statistics.
    
    Args:
        equity_curve: DataFrame from to_equity_curve()
        
    Returns:
        Dictionary with:
            - max_drawdown_pct: Maximum drawdown percentage
            - max_drawdown_amount: Maximum drawdown in account currency
            - peak_balance: Balance at the peak before max drawdown
            - trough_balance: Balance at the lowest point
            - peak_date: Date of the peak
            - trough_date: Date of the trough
            - recovery_date: Date of recovery (None if not recovered)
            - duration_to_trough: Trades from peak to trough
            - duration_to_recovery: Total trades to recover (None if ongoing)
            - currently_in_drawdown: Boolean if still in this drawdown
            
    Example:
        >>> max_dd = maximum_drawdown(equity)
        >>> print(f"Max DD: {max_dd['max_drawdown_pct']:.2f}%")
        >>> print(f"Took {max_dd['duration_to_recovery']} trades to recover")
    """
    dd_series = calculate_drawdown_series(equity_curve)
    
    # Find the point of maximum drawdown
    max_dd_idx = dd_series['drawdown_pct'].idxmin()
    max_dd_row = dd_series.loc[max_dd_idx]
    
    # Find the peak that led to this drawdown
    peak_mask = (dd_series.index < max_dd_idx) & (dd_series['balance'] == max_dd_row['peak'])
    if peak_mask.any():
        peak_idx = dd_series[peak_mask].index[-1]
        peak_row = dd_series.loc[peak_idx]
    else:
        peak_idx = dd_series.index[0]
        peak_row = dd_series.iloc[0]
    
    # Find recovery point (when balance reaches peak again)
    recovery_mask = (dd_series.index > max_dd_idx) & (dd_series['balance'] >= max_dd_row['peak'])
    if recovery_mask.any():
        recovery_idx = dd_series[recovery_mask].index[0]
        recovery_row = dd_series.loc[recovery_idx]
        recovery_date = recovery_row['timestamp']
        duration_to_recovery = recovery_idx - peak_idx
        currently_in_dd = False
    else:
        recovery_date = None
        duration_to_recovery = None
        currently_in_dd = True
    
    return {
        'max_drawdown_pct': max_dd_row['drawdown_pct'],
        'max_drawdown_amount': max_dd_row['drawdown'],
        'peak_balance': max_dd_row['peak'],
        'trough_balance': max_dd_row['balance'],
        'peak_date': peak_row['timestamp'] if 'timestamp' in peak_row else None,
        'trough_date': max_dd_row['timestamp'] if 'timestamp' in max_dd_row else None,
        'recovery_date': recovery_date,
        'duration_to_trough': max_dd_idx - peak_idx,
        'duration_to_recovery': duration_to_recovery,
        'currently_in_drawdown': currently_in_dd
    }


def average_drawdown(equity_curve: pd.DataFrame) -> float:
    """
    Calculate the average drawdown across all drawdown periods.
    
    This gives a sense of typical drawdown magnitude, not just the worst case.
    
    Args:
        equity_curve: DataFrame from to_equity_curve()
        
    Returns:
        Average drawdown percentage across all periods
        
    Example:
        >>> avg_dd = average_drawdown(equity)
        >>> print(f"Typical drawdown: {avg_dd:.2f}%")
    """
    periods = identify_drawdown_periods(equity_curve)
    
    if not periods:
        return 0.0
    
    drawdowns = [abs(p['max_drawdown_pct']) for p in periods]
    return np.mean(drawdowns)


def drawdown_duration_stats(equity_curve: pd.DataFrame) -> Dict:
    """
    Calculate statistics about drawdown durations.
    
    Args:
        equity_curve: DataFrame from to_equity_curve()
        
    Returns:
        Dictionary with:
            - avg_duration: Average number of trades in drawdown
            - max_duration: Longest drawdown duration
            - median_duration: Median drawdown duration
            - total_periods: Number of drawdown periods
            - currently_underwater: Boolean if currently in drawdown
            
    Example:
        >>> duration_stats = drawdown_duration_stats(equity)
        >>> print(f"Average time in drawdown: {duration_stats['avg_duration']} trades")
    """
    periods = identify_drawdown_periods(equity_curve)
    
    if not periods:
        return {
            'avg_duration': 0,
            'max_duration': 0,
            'median_duration': 0,
            'total_periods': 0,
            'currently_underwater': False
        }
    
    durations = [p['duration'] for p in periods]
    
    return {
        'avg_duration': np.mean(durations),
        'max_duration': np.max(durations),
        'median_duration': np.median(durations),
        'total_periods': len(periods),
        'currently_underwater': not periods[-1]['recovered'] if periods else False
    }

def underwater_time(equity_curve: pd.DataFrame) -> Dict:
    """
    Calculate the percentage of time spent in drawdown.
    
    Args:
        equity_curve: DataFrame from to_equity_curve()
        
    Returns:
        Dictionary with:
            - underwater_trades: Number of trades in drawdown
            - total_trades: Total number of trades
            - underwater_pct: Percentage of time underwater
            
    Example:
        >>> underwater = underwater_time(equity)
        >>> print(f"Spent {underwater['underwater_pct']:.1f}% of time in drawdown")
    """
    dd_series = calculate_drawdown_series(equity_curve)
    
    underwater_trades = dd_series['underwater'].sum()
    total_trades = len(dd_series)
    
    return {
        'underwater_trades': int(underwater_trades),
        'total_trades': total_trades,
        'underwater_pct': (underwater_trades / total_trades * 100) if total_trades > 0 else 0.0
    }

