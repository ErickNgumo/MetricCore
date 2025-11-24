# equity_curve

Utilities for converting raw trade logs into equity curves and resampling them for higher-level return analysis.
This module is part of the metric engine designed to work with validated trade logs (such as those produced by `TradeLog`).

## Overview

The equity curve represents the progression of account balance after each trade, based on cumulative PnL.
This module provides two core functions:

1. `to_equity_curve(df, starting_balance=10000.0)`

Converts a validated trade log DataFrame into a chronological equity curve.

2. `resample_equity_curve(equity_curve, freq="D")`

Resamples the equity curve to daily, weekly, or monthly periods, allowing higher-level return calculations.

## Requirements

The input DataFrame must contain:

- `timestamp_exit` — trade exit timestamp (datetime)

- `pnl` — profit or loss for each trade (numeric)

These are automatically provided by the TradeLog validator.

## Function Details
`to_equity_curve(df, starting_balance=10000.0)`

### Purpose:
Generate a trade-by-trade equity curve with cumulative balance and percentage returns.

### Returns:
A DataFrame with:

| Column      | Description                           |
|-------------|----------------------------------------|
| `timestamp` | Exit timestamp of each trade           |
| `balance`   | Account balance after each trade       |
| `pnl`       | PnL of each trade                      |
| `returns`   | Return % relative to previous balance  |


### Example:
```python
from metrics import to_equity_curve

equity = to_equity_curve(trades_df, starting_balance=5000)
print(equity.head())
```

`resample_equity_curve(equity_curve, freq="D")`

### Purpose:
Resample the equity curve into time-based periods (daily/weekly/monthly).
Useful for computing portfolio-style metrics such as monthly returns, drawdown series, etc.

### Arguments:

equity_curve: DataFrame produced by to_equity_curve

`freq`: `"D"`, `"W"`, or `"M"` for daily, weekly, or monthly

### Returns:
A DataFrame containing:

- last balance per period

- total PnL per period

- compounded returns

- period-over-period returns

- cumulative returns

### Example:
```python
from metrics import (
    to_equity_curve, resample_equity_curve
)

equity = to_equity_curve(trades_df)
monthly = resample_equity_curve(equity, freq="M")

print(monthly.tail())
```
## Notes

Periods with no trades are forward-filled to keep the balance series continuous.

Returns inside `resample_equity_curve` use compounded returns, not arithmetic.

`starting_balance` is inferred during resampling to ensure consistent cumulative return calculations.