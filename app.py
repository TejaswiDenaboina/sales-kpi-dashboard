import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import sys
sys.path.append('.')
from src.etl  import load_and_clean, get_summary
from src.kpis import (revenue_by_month, revenue_by_region,
                      revenue_by_category, top_customers, loss_analysis)

df      = load_and_clean()
summary = get_summary(df)
monthly = revenue_by_month(df)
region  = revenue_by_region(df)
categ   = revenue_by_category(df)
top_c   = top_customers(df)
losses  = loss_analysis(df)

def _metric(label, value):
    return html.Div([
        html.P(label, style={'fontSize':'12px','color':'#6B7280','margin':'0'}),
        html.P(value, style={'fontSize':'20px','fontWeight':'500','margin':'0'}),
    ], style={'background':'#F3F4F6','borderRadius':'8px','padding':'12px'})


app = Dash(__name__)
server = app.server   
YEARS = ['All'] + sorted(df['order_year'].unique().tolist(), reverse=True)

app.layout = html.Div([
    html.H1("Superstore Sales KPI Dashboard",
            style={'fontFamily':'Arial','fontSize':'22px','marginBottom':'4px'}),
    html.P("Real sales data — 9,994 orders | 2014–2017 | 4 US regions",
           style={'color':'#6B7280','fontSize':'13px','marginBottom':'20px'}),

    html.Div([
        _metric("Total Revenue",  f"${summary['total_revenue']:,.0f}"),
        _metric("Total Profit",   f"${summary['total_profit']:,.0f}"),
        _metric("Profit Margin",  f"{summary['overall_margin']}%"),
        _metric("Unique Customers", f"{summary['total_customers']:,}"),
        _metric("Avg Order Value",  f"${summary['avg_order_value']:,.0f}"),
        _metric("Loss Orders",    f"{summary['loss_pct']}%"),
    ], style={'display':'grid','gridTemplateColumns':'repeat(3,1fr)','gap':'12px','marginBottom':'20px'}),

    html.Div([
        html.Label("Filter by Year:", style={'fontSize':'13px','fontWeight':'500'}),
        dcc.Dropdown(id='year-filter',
                     options=[{'label':y,'value':y} for y in YEARS],
                     value='All', clearable=False,
                     style={'width':'200px','marginTop':'4px'}),
    ], style={'marginBottom':'20px'}),

    html.Div([
        dcc.Graph(id='monthly-revenue'),
        dcc.Graph(id='region-bar'),
    ], style={'display':'grid','gridTemplateColumns':'2fr 1fr','gap':'16px'}),

    html.Div([
        dcc.Graph(id='category-treemap'),
        dcc.Graph(id='loss-bar'),
    ], style={'display':'grid','gridTemplateColumns':'1fr 1fr','gap':'16px','marginTop':'16px'}),

    dcc.Graph(id='top-customers', style={'marginTop':'16px'}),

], style={'fontFamily':'Arial','padding':'24px','maxWidth':'1200px','margin':'0 auto'})



@app.callback(
    [Output('monthly-revenue','figure'),
     Output('region-bar','figure'),
     Output('category-treemap','figure'),
     Output('loss-bar','figure'),
     Output('top-customers','figure')],
    Input('year-filter','value')
)
def update(year):
    dff = df if year=='All' else df[df['order_year']==int(year)]
    mon = revenue_by_month(dff)
    reg = revenue_by_region(dff)
    cat = revenue_by_category(dff)
    tc  = top_customers(dff)
    ls  = loss_analysis(dff)

    fig1 = px.bar(mon, x='yearmonth', y='revenue',
                  title='Monthly revenue with profit overlay',
                  color='margin_pct', color_continuous_scale='RdYlGn',
                  labels={'revenue':'Revenue ($)','yearmonth':'Month','margin_pct':'Margin %'})
    fig1.add_scatter(x=mon['yearmonth'], y=mon['profit'],
                     mode='lines+markers', name='Profit',
                     line=dict(color='#378ADD', width=2))
    fig1.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    fig1.update_xaxes(tickangle=45, nticks=12)

    fig2 = px.bar(reg, x='revenue', y='region', orientation='h',
                  title='Revenue by region',
                  color='margin_pct', color_continuous_scale='RdYlGn',
                  labels={'revenue':'Revenue ($)','margin_pct':'Margin %'})
    fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white')

    fig3 = px.treemap(cat, path=['category','sub_category'],
                      values='revenue', color='margin_pct',
                      color_continuous_scale='RdYlGn',
                      title='Revenue treemap by category and sub-category')
    fig3.update_layout(paper_bgcolor='white')

    fig4 = px.bar(ls, x='loss_amount', y='sub_category', orientation='h',
                  title='Loss-making sub-categories (avg discount %)',
                  color='avg_discount', color_continuous_scale='Reds',
                  labels={'loss_amount':'Total Loss ($)','avg_discount':'Avg Discount %'})
    fig4.update_layout(plot_bgcolor='white', paper_bgcolor='white')

    fig5 = px.bar(tc, x='customer_name', y='total_revenue',
                  title='Top 10 customers by revenue',
                  color='total_profit', color_continuous_scale='RdYlGn',
                  labels={'total_revenue':'Revenue ($)','total_profit':'Profit ($)'})
    fig5.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    fig5.update_xaxes(tickangle=30)

    return fig1, fig2, fig3, fig4, fig5

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8050)