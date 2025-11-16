import pandas as pd
import numpy as np
from pathlib import Path
from typing import Union

class TradeLogValidationError(Exception):
    """Custom exception for trade log validation failures"""
    pass

class TradeLog:
    """
    Trade log validator and processor for algorithmic trading metrics.
    
    Enforces strict schema requirements on trade data to ensure
    reliable metric calculations downstream.
    """

    REQUIRED_COLUMNS = [
        "timestamp_entry",
        "timestamp_exit",
        "symbol",
        "direction",
        "size",
        "pnl"
    ]

    OPTIONAL_COLUMNS = [
        "return_pct",
        "risk_amount",
        "comment"
    ]

    VALID_DIRECTIONS = ["LONG", "SHORT"]

    def __init__(self, data: Union[str, Path, pd.DataFrame]):
        """
        Initialize and validate trade log data.
        
        Args:
            data: Either a path to CSV file or a pandas DataFrame
            
        Raises:
            TradeLogValidationError: If data fails validation
        """
        self.raw_data = data
        self.df = None
        self._load_data()
        self._validate()

    def _load_data(self):
        """
        Load CSV or DataFrame into self.df.
        Performs initial type conversions.
        """
        #Load from CSV or use DataFrame directly
        if isinstance(self.raw_data, (str, Path)):
            try:
                self.df = pd.read_csv(self.raw_data)
            except FileNotFoundError:
                raise TradeLogValidationError(f"CSV file not found: {self.raw_data}")
            except Exception as e:
                raise TradeLogValidationError(f"Failed to read CSV: {str(e)}")
        
        elif isinstance(self.raw_data, pd.DataFrame):
            self.df = self.raw_data.copy()
        else:
            raise TradeLogValidationError(
                f"Invalid data type. Expected str, Path, or DataFrame, got {type(self.raw_data)}"
            )
        # Strip whitespace from column names
        self.df.columns = self.df.columns.str.strip()

         # Convert timestamps to datetime
        for ts_col in ["timestamp_entry", "timestamp_exit"]:
            if ts_col in self.df.columns:
                try:
                    self.df[ts_col] = pd.to_datetime(self.df[ts_col])
                except Exception as e:
                    raise TradeLogValidationError(
                        f"Failed to parse {ts_col} as datetime: {str(e)}"
                    )
                
        # Convert numeric columns
        numeric_cols = ["size", "pnl"]
        for col in numeric_cols:
            if col in self.df.columns:
                try:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                except Exception as e:
                    raise TradeLogValidationError(
                        f"Failed to convert {col} to numeric: {str(e)}"
                    )
                
        # Convert optional numeric columns if present
        for col in ["return_pct", "risk_amount"]:
            if col in self.df.columns:
                try:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                except Exception:
                    pass  # Optional columns can fail gracefully
        
        # Normalize direction to lowercase
        if "direction" in self.df.columns:
            self.df["direction"] = self.df["direction"].astype(str).str.strip().str.lower()
        
        # Strip whitespace from symbol
        if "symbol" in self.df.columns:
            self.df["symbol"] = self.df["symbol"].astype(str).str.strip()
    
        
    
    def _validate(self):
        """
        Run comprehensive validation checks on the trade log.
        
        Raises:
            TradeLogValidationError: If any validation rule fails
        """
        # Rule 7: DataFrame must not be empty
        if self.df.empty:
            raise TradeLogValidationError("Trade log is empty. At least one trade is required.")
        
        # Rule 1: All required columns must exist
        missing_cols = set(self.REQUIRED_COLUMNS) - set(self.df.columns)
        if missing_cols:
            raise TradeLogValidationError(
                f"Missing required columns: {sorted(missing_cols)}"
            )
        
        # Rule 3: No NaNs in required columns
        for col in self.REQUIRED_COLUMNS:
            nan_count = self.df[col].isna().sum()
            if nan_count > 0:
                raise TradeLogValidationError(
                    f"Column '{col}' contains {nan_count} NaN value(s). "
                    f"All required fields must have valid data."
                )


         # Rule 2: Timestamps must be valid datetime objects
        for ts_col in ["timestamp_entry", "timestamp_exit"]:
            if not pd.api.types.is_datetime64_any_dtype(self.df[ts_col]):
                raise TradeLogValidationError(
                    f"Column '{ts_col}' must be datetime type, got {self.df[ts_col].dtype}"
                )
        
        # Rule 4: timestamp_exit must be >= timestamp_entry
        invalid_timestamps = self.df["timestamp_exit"] < self.df["timestamp_entry"]
        if invalid_timestamps.any():
            invalid_indices = self.df[invalid_timestamps].index.tolist()
            raise TradeLogValidationError(
                f"timestamp_exit must be >= timestamp_entry. "
                f"Invalid rows: {invalid_indices[:5]}" + 
                (f" ... and {len(invalid_indices) - 5} more" if len(invalid_indices) > 5 else "")
            )
        
        # Rule 5: direction must be exactly "long" or "short"
        invalid_directions = ~self.df["direction"].isin(self.VALID_DIRECTIONS)
        if invalid_directions.any():
            unique_invalid = self.df.loc[invalid_directions, "direction"].unique().tolist()
            raise TradeLogValidationError(
                f"Invalid direction values: {unique_invalid}. "
                f"Must be exactly 'long' or 'short' (case-insensitive)."
            )
        
        # Rule 6: pnl and size must be numeric
        if not pd.api.types.is_numeric_dtype(self.df["pnl"]):
            raise TradeLogValidationError(
                f"Column 'pnl' must be numeric, got {self.df['pnl'].dtype}"
            )
        
        if not pd.api.types.is_numeric_dtype(self.df["size"]):
            raise TradeLogValidationError(
                f"Column 'size' must be numeric, got {self.df['size'].dtype}"
            )
        
        #Additional sanity check: size should be positive
        non_positive_size = self.df["size"] <= 0
        if non_positive_size.any():
            invalid_indices = self.df[non_positive_size].index.tolist()
            raise TradeLogValidationError(
                f"Position size must be positive. "
                f"Invalid rows: {invalid_indices[:5]}" + 
                (f" ... and {len(invalid_indices) - 5} more" if len(invalid_indices) > 5 else "")
            )
        


              
        

        
        


