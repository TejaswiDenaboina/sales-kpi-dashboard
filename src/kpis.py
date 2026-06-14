import pandas as pd
import numpy as np

def revenue_by_month(df):
    monthly = df.groupby('yearmonth').agg(
        revenue=('sales','sum'),
        profit=('profit','sum'),
        orders=('order_id','nunique')
    ).reset_index()
    monthly['margin_pct'] = (monthly['profit'] / monthly['revenue'] * 100).round(2)
    monthly['mom_growth'] = monthly['revenue'].pct_change() * 100
    monthly['mom_growth'] = monthly['mom_growth'].round(2)
    return monthly

def revenue_by_region(df):
    return df.groupby('region').agg(
        revenue=('sales','sum'),
        profit=('profit','sum'),
        orders=('order_id','nunique'),
        customers=('customer_id','nunique')
    ).assign(
        margin_pct=lambda x: (x['profit']/x['revenue']*100).round(2),
        avg_order=lambda x: (x['revenue']/x['orders']).round(2)
    ).reset_index().sort_values('revenue', ascending=False)

def revenue_by_category(df):
    return df.groupby(['category','sub_category']).agg(
        revenue=('sales','sum'),
        profit=('profit','sum'),
        quantity=('quantity','sum')
    ).assign(
        margin_pct=lambda x: (x['profit']/x['revenue']*100).round(2)
    ).reset_index().sort_values('revenue', ascending=False)

def cohort_analysis(df):
    # First purchase month per customer
    df = df.copy()
    first_purchase = df.groupby('customer_id')['order_date'].min().reset_index()
    first_purchase.columns = ['customer_id','cohort_date']
    first_purchase['cohort'] = first_purchase['cohort_date'].dt.to_period('M').astype(str)

    df = df.merge(first_purchase, on='customer_id')
    df['months_since_first'] = (
        df['order_date'].dt.to_period('M').astype(int) -
        first_purchase.set_index('customer_id')['cohort_date']
        .dt.to_period('M').astype(int)
        .reindex(df['customer_id'].values).values
    )
    cohort = df.groupby(['cohort','months_since_first'])['customer_id'].nunique().reset_index()
    cohort.columns = ['cohort','months_since_first','customers']

    # Retention rate vs month 0
    cohort_size = cohort[cohort['months_since_first']==0][['cohort','customers']].rename(
        columns={'customers':'cohort_size'})
    cohort = cohort.merge(cohort_size, on='cohort')
    cohort['retention_rate'] = (cohort['customers']/cohort['cohort_size']*100).round(1)
    return cohort

def top_customers(df, n=10):
    return df.groupby(['customer_id','customer_name']).agg(
        total_revenue=('sales','sum'),
        total_profit=('profit','sum'),
        orders=('order_id','nunique')
    ).reset_index().sort_values('total_revenue', ascending=False).head(n)

def loss_analysis(df):
    losses = df[df['profit'] < 0].groupby('sub_category').agg(
        loss_amount=('profit','sum'),
        loss_orders=('order_id','count'),
        avg_discount=('discount','mean')
    ).reset_index().sort_values('loss_amount')
    losses['avg_discount'] = (losses['avg_discount']*100).round(1)
    losses['loss_amount'] = losses['loss_amount'].round(2)
    return losses

if __name__ == "__main__":
    import sys
    sys.path.append('.')
    from src.etl import load_and_clean
    df = load_and_clean()

    print("\nKPI 1 — Monthly revenue (last 6 months):")
    print(revenue_by_month(df).tail(6).to_string(index=False))

    print("\nKPI 2 — Revenue by region:")
    print(revenue_by_region(df).to_string(index=False))

    print("\nKPI 3 — Top 5 categories by revenue:")
    print(revenue_by_category(df).head(5).to_string(index=False))

    print("\nKPI 4 — Top 10 customers:")
    print(top_customers(df).to_string(index=False))

    print("\nKPI 5 — Loss-making sub-categories:")
    print(loss_analysis(df).to_string(index=False))