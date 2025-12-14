# Drawdown Analysis Module

This module provides a comprehensive set of tools for **drawdown analysis** based on an equity curve generated from a trading strategy. Drawdown analysis focuses on *risk*, *capital decline*, and *recovery behavior*, answering questions such as:

* How bad did losses get at their worst?
* How long did the strategy stay underwater?
* How often do drawdowns occur, and how severe are they typically?

The functions in this file are designed to work directly with the output of `to_equity_curve()`.

---

## Prerequisites

The equity curve passed into these functions **must**:

* Be a `pandas.DataFrame`
* Contain at least the following columns:

  * `timestamp`
  * `balance`

Typically, this comes from:

```python
from metrics import to_equity_curve

equity = to_equity_curve(trades_df)
```

---

## Core Concepts

**Drawdown** measures how far the equity curve has fallen from its most recent peak.

* Drawdowns are always zero or negative
* A strategy can be profitable overall and still experience severe drawdowns
* Duration matters as much as magnitude

This module separates drawdown analysis into:

* Drawdown *series* (point‑by‑point)
* Individual *drawdown periods*
* Aggregate statistics (max, average, duration, time underwater)

---

## API Reference

### `calculate_drawdown_series(equity_curve)`

Computes the full drawdown time series.

Adds the following columns:

| Column         | Description                        |
| -------------- | ---------------------------------- |
| `peak`         | Running maximum of account balance |
| `drawdown`     | Absolute drawdown from peak        |
| `drawdown_pct` | Percentage drawdown from peak      |
| `underwater`   | Boolean flag indicating drawdown   |

Example:

```python
from metrics import calculate_drawdown_series

dd = calculate_drawdown_series(equity)
print(dd[['balance', 'drawdown_pct']].tail())
```

---

### `identify_drawdown_periods(equity_curve)`

Identifies **individual drawdown events**, from peak → trough → recovery.

Each period includes:

* Start and end indices
* Peak and trough balances
* Maximum drawdown (absolute and percentage)
* Duration in trades
* Recovery status

Returns a list of dictionaries.

Example:

```python
periods = identify_drawdown_periods(equity)
worst = max(periods, key=lambda x: abs(x['max_drawdown_pct']))
print(worst)
```

---

### `maximum_drawdown(equity_curve)`

Extracts detailed statistics for the **worst drawdown** in the equity curve.

Returned metrics include:

* Maximum drawdown (percentage and amount)
* Peak and trough dates
* Time to trough
* Time to recovery (if recovered)
* Whether the strategy is currently in this drawdown

Example:

```python
max_dd = maximum_drawdown(equity)
print(f"Max DD: {max_dd['max_drawdown_pct']:.2f}%")
```

---

### `average_drawdown(equity_curve)`

Computes the **average drawdown magnitude** across all drawdown periods.

This provides a sense of *typical* drawdown severity rather than the worst case.

Example:

```python
avg_dd = average_drawdown(equity)
print(f"Typical drawdown: {avg_dd:.2f}%")
```

---

### `drawdown_duration_stats(equity_curve)`

Analyzes how long drawdowns last.

Returned metrics:

* Average duration
* Maximum duration
* Median duration
* Total number of drawdown periods
* Whether the strategy is currently underwater

Example:

```python
stats = drawdown_duration_stats(equity)
print(stats)
```

---

### `underwater_time(equity_curve)`

Calculates the percentage of trades spent in drawdown.

This answers the psychological question:

> *How often am I underwater?*

Example:

```python
uw = underwater_time(equity)
print(f"Underwater {uw['underwater_pct']:.1f}% of the time")
```

---

### `summary(equity_curve)`

Generates a **comprehensive drawdown report**, combining all key metrics:

* Maximum drawdown
* Average drawdown
* Drawdown durations
* Time underwater
* Current drawdown status

Example:

```python
from metrics import drawdown_summary

dd_summary = summary(equity)
for k, v in dd_summary.items():
    print(f"{k}: {v}")
```

---

## Design Notes

* Drawdown calculations are trade‑based, not time‑based
