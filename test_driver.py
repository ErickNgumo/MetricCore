"""
Test script for the algo trading metrics library.
Tests: TradeLog validation, win/loss metrics, and equity curve generation.
"""
import pandas as pd
import sys


try:
    from metrics import( 
        #from tradelog.tradelog.py
        TradeLog,
        #from winloss.winloss.py
        win_rate, loss_rate, average_win, average_loss, 
        expectancy, profit_factor, win_loss_ratio,
        longest_win_streak, longest_loss_streak, summary as winloss_summary,
        
        #form equitycurve.equitycurve.py
        to_equity_curve,resample_equity_curve
    )

except ImportError as e:
    print(f"Import error:{e}")
    print("Folder Structure")
    print(" metrics/")
    print("     __init__.py")
    print("     tradelog/" \
    "               tradelog.py")
    print("     winloss/" \
    "               winloss.py")
    print("     equitycurve/" \
    "               equitycurve.py")
    sys.exit(1)


def create_sample_trades():
    """Create a sample trade log for testing."""
    trades = pd.DataFrame({
        "timestamp_entry": [
            "2025-01-01 09:00",
            "2025-01-01 14:00",
            "2025-01-02 09:30",
            "2025-01-02 15:00",
            "2025-01-03 10:00",
            "2025-01-04 09:00",
            "2025-01-04 13:00",
            "2025-01-05 11:00",
        ],
        "timestamp_exit": [
            "2025-01-01 10:30",
            "2025-01-01 15:00",
            "2025-01-02 11:00",
            "2025-01-02 16:30",
            "2025-01-03 12:00",
            "2025-01-04 10:30",
            "2025-01-04 14:00",
            "2025-01-05 12:30",
        ],
        "symbol": [
            "NAS100", "EURUSD", "XAUUSD", "NAS100",
            "EURUSD", "NAS100", "XAUUSD", "EURUSD"
        ],
        "direction": [
            "long", "short", "long", "long",
            "short", "long", "long", "short"
        ],
        "size": [1.0, 0.5, 0.2, 1.0, 0.5, 1.0, 0.2, 0.5],
        "pnl": [150.0, -75.0, 300.0, 200.0, -100.0, 50.0, -50.0, 125.0]
    })
    return trades
   
def test_tradelog_validation():
    """Test 1: TradeLog validation"""
    print("TEST 1: TradeLog Validation")
    print("=" * 70)

    trades = create_sample_trades()

    try:
        log = TradeLog(trades)
        print("Trade log validated successfully!")
        print(f"Loaded {len(log.df)} trades")
        print(f"Date range: {log.df['timestamp_entry'].min()} to {log.df['timestamp_exit'].max()}")
        print(f"Symbols: {', '.join(log.df['symbol'].unique())}")
        return log
    except Exception as e:
        print(f"Validation failed: {e}")
        return None

def test_winloss_metrics(log):
    """Test 2: Win/Loss metrics"""
    print("TEST 2: Win/Loss Metrics")
    print("=" * 70)
    
    df = log.df
    print(f"   Total trades: {len(df)}")
    print(f"   Win rate: {win_rate(df):.1%}")
    print(f"   Loss rate: {loss_rate(df):.1%}")
    
    print(f"   Average win: ${average_win(df):.2f}")
    print(f"   Average loss: ${average_loss(df):.2f}")
    print(f"   Win/Loss ratio: {win_loss_ratio(df):.2f}")
    print(f"   Expectancy: ${expectancy(df):.2f} per trade")
    print(f"   Profit factor: {profit_factor(df):.2f}")
    
    print(f"   Longest win streak: {longest_win_streak(df)} trades")
    print(f"   Longest loss streak: {longest_loss_streak(df)} trades")

    print(f"Complete Summary:")
    summary = winloss_summary(df)
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")

def test_equity_curve(log):
    """Test 3: Equity curve generation"""
    print("TEST 3: Equity Curve Generation")
    print("=" * 70)

    starting_balance = 10000.0
    equity = to_equity_curve(log.df, starting_balance=starting_balance)

    print(f"Equity Curve (first 5 rows):")
    print(equity.head().to_string(index=False))
    
    print(f"Equity Curve (last 3 rows):")
    print(equity.tail(3).to_string(index=False))

    print(f"Balance progression:")
    print(f"   Starting: ${starting_balance:,.2f}")
    print(f"   Ending: ${equity['balance'].iloc[-1]:,.2f}")
    print(f"   Total P&L: ${equity['pnl'].sum():,.2f}")

    return equity
        

def test_equity_resampling(equity):
    """Test 4: Equity curve resampling"""

    print("TEST 4: Equity Curve Resampling")
    print("=" * 70)
    
    daily = resample_equity_curve(equity, freq="D")

    print(f"Daily Resampled Equity:")
    print(daily.to_string(index=False))

    print(f"   Trading days: {len(daily)}")
    print(f"   Days with trades: {(daily['pnl'] != 0).sum()}")
    print(f"   Days without trades: {(daily['pnl'] == 0).sum()}")
    print(f"   Average daily return: {daily['period_returns'].mean():.2f}%")
    print(f"   Daily volatility: {daily['period_returns'].std():.2f}%")

    return daily


def test_validation_errors():
    """Test 5: Validation error handling"""
    print("TEST 6: Validation Error Handling")
    print("=" * 70)

    print("Test case: Missing required column")
    bad_trades = pd.DataFrame({
        "timestamp_entry": ["2025-01-01 09:00"],
        "timestamp_exit": ["2025-01-01 10:00"],
        "symbol": ["NAS100"],
        # Missing 'direction', 'size', 'pnl'
    })

    try:
        log = TradeLog(bad_trades)
        print("Should have failed validation!")
    except Exception as e:
        print(f"Correctly caught error: {str(e)[:80]}...")

    # Test 2: Invalid direction
    print("\nTest case: Invalid direction value")
    bad_trades = create_sample_trades()
    bad_trades.loc[0, 'direction'] = 'buy'  # Should be 'long' or 'short'
    
    try:
        log = TradeLog(bad_trades)
        print("Should have failed validation!")
    except Exception as e:
        print(f"Correctly caught error: {str(e)[:80]}...")
    
    # Test 3: Exit before entry
    print("\nTest case: Exit time before entry time")
    bad_trades = create_sample_trades()
    bad_trades.loc[0, 'timestamp_exit'] = "2024-12-31 10:00"  # Before entry
    
    try:
        log = TradeLog(bad_trades)
        print("Should have failed validation!")
    except Exception as e:
        print(f"Correctly caught error: {str(e)[:80]}...")



def run_all_tests():
    """Run all tests"""
    print("ALGO TRADING METRICS LIBRARY - TEST SUITE")
    
    # Test 1: Validation
    log = test_tradelog_validation()
    if log is None:
        print("Failed at validation stage. Stopping tests.")
        return
    
    # Test 2: Win/Loss metrics
    test_winloss_metrics(log)
    
    # Test 3: Equity curve
    equity = test_equity_curve(log)
    
    # Test 4: Resampling
    daily = test_equity_resampling(equity)      
    
    # Test 5: Error handling
    test_validation_errors()

if __name__ == "__main__":
    run_all_tests()
    


    
    




    



    












