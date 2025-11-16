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

        REQUIRED_COLUMNS = [
            "timestamp_entry",
            "timestamp_exit",
            "symbol",
            "direction",
            "size",
            "pnl"
        ]


