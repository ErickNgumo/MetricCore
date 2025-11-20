# Win/Loss Metrics Module
This module provides common win/loss statistics used in evaluating trading strategy performance.
It is designed to operate on the validated trade log produced by TradeLog and assumes the presence of a `pnl` column.

The functions are pure, vectorized, and return numerical or dictionary outputs suitable for reports and dashboards.

## Features

The module includes:

- Win rate

- Loss rate

- Breakeven rate

- Average win / average loss

- Expectancy (expected value per trade)

- Profit factor

- Win/Loss ratio (payoff ratio)

- Win streaks & loss streaks

- Streak distribution

- Summary aggregator

All metrics assume that:

- Positive `pnl` = win

- Negative `pnl` = loss

- Zero `pnl` = breakeven (excluded from streaks)

## Requirements

This module expects a DataFrame with at least:
```cpp
pnl
timestamp_exit (optional, but recommended for chronological streak analysis)
```
It is recommended to pass data that has already been validated using:
```python
from metrics import TradeLog
log = TradeLog("trades.csv")
df = log.df
```
## Example Usage
```python
from metrics import (
    win_rate, loss_rate, expectancy,
    longest_win_streak, longest_loss_streak,
    streak_distribution, summary
)

metrics = summary(df)

print("Win rate:", metrics["win_rate"])
print("Longest win streak:", metrics["longest_win_streak"])
print("Profit factor:", metrics["profit_factor"])
```
## Output Example

Calling summary(df) returns:
```python
{
    'total_trades': 120,
    'win_rate': 0.58,
    'loss_rate': 0.37,
    'breakeven_rate': 0.05,
    'average_win': 230.50,
    'average_loss': -120.30,
    'expectancy': 74.82,
    'profit_factor': 1.91,
    'win_loss_ratio': 1.91,
    'longest_win_streak': 6,
    'longest_loss_streak': 4
}
```
## Notes

- Breakeven trades do not interrupt win/loss streaks.

- Expectancy handles edge cases (all wins, all losses) cleanly.

- All operations are fully vectorized for speed on large trade logs.