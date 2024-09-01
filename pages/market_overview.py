import streamlit as st
import yfinance as yf 
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import seaborn as sns
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go
from statsmodels.api import OLS
import requests
from transformers import pipeline

def display():
    st.title("Market Overview")

    # Market selection at the top of the sidebar
    st.sidebar.subheader("Market Selection")
    market = st.sidebar.selectbox("Select a market", ["Equity", "Bond", "Cryptocurrency", "Commodities", "Forex", "Real Estate"])

    ticker = None
    benchmark_ticker = None
    data = None
    benchmark_data = None

    # Handling each market selection
    if market == "Equity":
        ticker = st.sidebar.selectbox("Select a company", [
            "Apple (AAPL)", "Microsoft (MSFT)", "Google (GOOGL)", 
            "Amazon (AMZN)", "Tesla (TSLA)", "Netflix (NFLX)", 
            "Meta (FB)", "NVIDIA (NVDA)", "JPMorgan Chase (JPM)", 
            "Visa (V)"
        ])
        custom_ticker = st.sidebar.text_input("Or enter another ticker", "")
        if custom_ticker:
            ticker = custom_ticker.upper()

        company_to_ticker = {
            "Apple (AAPL)": "AAPL",
            "Microsoft (MSFT)": "MSFT",
            "Google (GOOGL)": "GOOGL",
            "Amazon (AMZN)": "AMZN",
            "Tesla (TSLA)": "TSLA",
            "Netflix (NFLX)": "NFLX",
            "NVIDIA (NVDA)": "NVDA",
            "JPMorgan Chase (JPM)": "JPM",
            "Visa (V)": "V"
        }
        ticker = company_to_ticker.get(ticker, ticker)

        benchmark = st.sidebar.selectbox("Select a benchmark index", ["S&P 500", "NASDAQ Composite", "Dow Jones Industrial Average"])
        benchmark_to_ticker = {
            "S&P 500": "^GSPC",
            "NASDAQ Composite": "^IXIC",
            "Dow Jones Industrial Average": "^DJI"
        }
        benchmark_ticker = benchmark_to_ticker[benchmark]

    elif market == "Bond":
        ticker = st.sidebar.selectbox("Select a bond ETF", ["TLT", "BND", "IEF", "AGG", "HYG"])
        custom_ticker = st.sidebar.text_input("Or enter another bond ETF", "")
        if custom_ticker:
            ticker = custom_ticker.upper()
        benchmark_ticker = "^TNX"  # US 10-Year Treasury Yield Index

    elif market == "Cryptocurrency":
        ticker = st.sidebar.selectbox("Select a cryptocurrency", ["BTC-USD", "ETH-USD", "XRP-USD", "LTC-USD", "ADA-USD"])
        custom_ticker = st.sidebar.text_input("Or enter another cryptocurrency ticker", "")
        if custom_ticker:
            ticker = custom_ticker.upper()

    elif market == "Commodities":
        ticker = st.sidebar.selectbox("Select a commodity ETF", ["GLD", "SLV", "USO", "DBA", "PALL"])
        custom_ticker = st.sidebar.text_input("Or enter another commodity ticker", "")
        if custom_ticker:
            ticker = custom_ticker.upper()
        benchmark_ticker = "^SPGSCI"  # S&P GSCI Index

    elif market == "Forex":
        ticker = st.sidebar.selectbox("Select a forex pair", ["EURUSD=X", "GBPUSD=X", "JPYUSD=X", "AUDUSD=X", "USDCAD=X"])
        custom_ticker = st.sidebar.text_input("Or enter another forex pair", "")
        if custom_ticker:
            ticker = custom_ticker.upper()

    elif market == "Real Estate":
        ticker = st.sidebar.selectbox("Select a real estate ETF", ["VNQ", "SCHH", "IYR", "XLRE", "REZ"])
        custom_ticker = st.sidebar.text_input("Or enter another real estate ETF", "")
        if custom_ticker:
            ticker = custom_ticker.upper()

    # Fetch the data
    period = st.sidebar.selectbox("Select time period", ["1mo", "3mo", "6mo", "1y", "5y"])
    data = yf.download(ticker, period=period)
    if benchmark_ticker:
        benchmark_data = yf.download(benchmark_ticker, period=period)

    # Add color picker for line plot color
    line_color = st.sidebar.color_picker("Pick a color for the graph", "#FF5733")

    # 1. Closing Price Graph
    st.subheader(f"{ticker} Closing Price Data")
    closing_fig = px.line(data, x=data.index, y='Close', title=f'{ticker} Closing Price')
    closing_fig.update_traces(line=dict(color=line_color))
    st.plotly_chart(closing_fig)

    if benchmark_ticker and market in ["Equity", "Bond", "Commodities"]:
        if not benchmark_data.empty and 'Close' in benchmark_data:
            # Normalize Data
            data['Normalized'] = data['Close'] / data['Close'].iloc[0]
            benchmark_data['Normalized'] = benchmark_data['Close'] / benchmark_data['Close'].iloc[0]

            benchmark_color = st.sidebar.color_picker("Pick a color for the benchmark graph", "#33FF57")

            # 2. Benchmark Comparison Graph (for Equity, Bond, Commodities)
            st.subheader(f"{ticker} vs {benchmark_ticker} Benchmark (Normalized)")
            comparison_fig = go.Figure()
            comparison_fig.add_trace(go.Scatter(x=data.index, y=data['Normalized'], mode='lines', name=f'{ticker} (Normalized)', line=dict(color=line_color)))
            comparison_fig.add_trace(go.Scatter(x=benchmark_data.index, y=benchmark_data['Normalized'], mode='lines', name=f'{benchmark_ticker} (Normalized)', line=dict(color=benchmark_color)))
            comparison_fig.update_layout(title=f'{ticker} vs {benchmark_ticker} (Normalized)', xaxis_title='Date', yaxis_title='Normalized Price')
            st.plotly_chart(comparison_fig)

    # Descriptive Statistics and Insights
    st.subheader("Statistical Performance Insights")
    highest_price = data['Close'].max()
    highest_price_date = data['Close'].idxmax()
    lowest_price = data['Close'].min()
    lowest_price_date = data['Close'].idxmin()
    opening_price = data['Open'][0]
    closing_price = data['Close'][-1]
    high_12m = data['Close'].rolling(window=252, min_periods=1).max().iloc[-1]
    low_12m = data['Close'].rolling(window=252, min_periods=1).min().iloc[-1]
    one_year_return = (data['Close'][-1] / data['Close'].iloc[0] - 1) * 100

    st.table(pd.DataFrame({
        "Metric": ["Highest Price", "Lowest Price", "Opening Price", "Closing Price", "12M High", "12M Low", "52-Week Change"],
        "Value": [
            f"{highest_price:.2f} (on {highest_price_date.date()})",
            f"{lowest_price:.2f} (on {lowest_price_date.date()})",
            f"{opening_price:.2f}",
            f"{closing_price:.2f}",
            f"{high_12m:.2f}",
            f"{low_12m:.2f}",
            f"{one_year_return:.2f}%"
        ]
    }))

    # Display descriptive statistics
    st.write(data.describe())