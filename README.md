# TradeLog

`TradeLog` is a validation and preprocessing utility for algorithmic trading analysis. It ensures that trade logs follow a strict and reliable schema before being used for metrics, backtesting, or performance reporting. The module handles input loading, type enforcement, data cleaning, and construction of an equity curve.

---

## Features

- Load trade logs from a CSV file or a pandas `DataFrame`
- Enforce required columns and validate their types
- Automatically parse timestamps and numeric fields
- Validate trade direction, PnL values, and position sizes
- Detect missing or invalid data early through clear error messages
- Generate a chronological equity curve suitable for strategy evaluation

---

## Installation

No external installation is required beyond pandas and numpy:

```bash
pip install pandas numpy
```
## Usage
### Basic example
```python
from tradelog import TradeLog

log = TradeLog("my_trades.csv")
equity_curve = log.to_equity_curve(starting_balance=10000)

print(log)               # Summary information
print(equity_curve.head())
```
### Initializing from a DataFrame
```python
import pandas as pd
from tradelog import TradeLog

df = pd.DataFrame({
    "timestamp_entry": [...],
    "timestamp_exit": [...],
    "symbol": [...],
    "direction": [...],   # "long" or "short"
    "size": [...],
    "pnl": [...]
})

log = TradeLog(df)
```
### Required Columns
Every trade log must contain the following fields:

`timestamp_entry` — entry time (parsed to datetime)

`timestamp_exit` — exit time (parsed to datetime)

`symbol` — asset identifier

`direction` — "long" or "short" (case-insensitive)

`size` — positive numeric value

`pnl` — profit or loss for the trade

Optional columns may be included and are coerced to numeric if present:

`return_pct`

`risk_amount`

### Validation Rules
The `TradeLog` class enforces several rules:

All required columns must be present

Timestamps must be valid datetime objects

No missing values in required fields

`timestamp_exit` must be greater than or equal to timestamp_entry

`direction` must be "long" or "short"

`size` and `pnl` must be numeric

`size` must be strictly positive

Trade log must contain at least one row

Validation failures raise `TradeLogValidationError` with a descriptive message.

### Generating an Equity Curve
The method `to_equity_curve()` computes:

cumulative account balance

per-trade PnL

per-trade percentage returns

sorted chronological timestamps

Example:

```python
equity = log.to_equity_curve(starting_balance=10000)
```
Output DataFrame columns:

`timestamp` — exit time of each trade

`balance` — cumulative balance after each trade

`pnl` — PnL of the trade

`returns` — percent return based on prior balance

### Exceptions
All validation failures raise:
'''
python
TradeLogValidationError
'''
This allows clean, predictable error handling in trading pipelines.

### Summary
TradeLog provides a robust foundation for validating, cleaning, and preparing trade data for quantitative analysis. It reduces downstream errors, enforces consistent structure, and offers a reliable method for generating equity curves used by risk and performance metrics.
