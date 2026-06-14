import pandas as pd
import numpy as np
from pathlib import Path

def load_and_clean(filepath: str = 'data/superstore.csv') -> pd.DataFrame:
    df = pd.read_csv(filepath, encoding='latin-1')

    # Parse dates
    df['Order Date'] = pd.to_datetime(df['Order Date'], format='%m/%d/%Y')
    df['Ship Date']  = pd.to_datetime(df['Ship Date'], format='%m/%d/%Y')

    # Add derived date columns
    df['Order Year']    = df['Order Date'].dt.year
    df['Order Month']   = df['Order Date'].dt.month
    df['Order Quarter'] = df['Order Date'].dt.quarter
    df['YearMonth']     = df['Order Date'].dt.to_period('M').astype(str)
    df['Ship Days']     = (df['Ship Date'] - df['Order Date']).dt.days

    # Clean column names
    df.columns = (
    df.columns
      .str.strip()
      .str.replace(' ', '_')
      .str.replace('-', '_')
      .str.lower()
)

    # Add profit margin column
    df['profit_margin'] = np.where(
        df['sales'] != 0,
        (df['profit'] / df['sales'] * 100).round(2),
        0
    )

    # Flag negative profit orders
    df['is_loss'] = df['profit'] < 0

    print(f"Loaded: {df.shape[0]:,} rows, {df.shape[1]} columns")
    print(f"Date range: {df['order_date'].min().date()} → {df['order_date'].max().date()}")
    print(f"Regions: {df['region'].unique().tolist()}")
    print(f"Categories: {df['category'].unique().tolist()}")
    return df

def get_summary(df: pd.DataFrame) -> dict:
    return {
        'total_revenue'   : round(df['sales'].sum(), 2),
        'total_profit'    : round(df['profit'].sum(), 2),
        'overall_margin'  : round(df['profit'].sum() / df['sales'].sum() * 100, 2),
        'total_orders'    : df['order_id'].nunique(),
        'total_customers' : df['customer_id'].nunique(),
        'avg_order_value' : round(df.groupby('order_id')['sales'].sum().mean(), 2),
        'loss_orders'     : int(df['is_loss'].sum()),
        'loss_pct'        : round(df['is_loss'].mean() * 100, 2),
    }

if __name__ == "__main__":
    df = load_and_clean()
    summary = get_summary(df)
    print("\nBUSINESS SUMMARY:")
    for k, v in summary.items():
        print(f"  {k}: {v}")