import streamlit as st
import pandas as pd
import yfinance as yf 
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
import seaborn as sns
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go
from statsmodels.api import OLS
import requests
from transformers import pipeline

def display():
    # Predefined list of popular US stock tickers and their corresponding company names
    company_dict = {
        "Apple Inc.": "AAPL",
        "Microsoft Corporation": "MSFT",
        "Alphabet Inc.": "GOOGL",
        "Amazon.com, Inc.": "AMZN",
        "Tesla, Inc.": "TSLA",
        "NVIDIA Corporation": "NVDA",
        "JPMorgan Chase & Co.": "JPM",
        "Visa Inc.": "V",
        "Netflix, Inc.": "NFLX"
    }

    # Sidebar inputs
    company_name = st.sidebar.selectbox("Select a company", list(company_dict.keys()))
    custom_ticker = st.sidebar.text_input("Or enter another ticker", "")

    # Determine the ticker based on the selection or custom input
    ticker = custom_ticker.upper() if custom_ticker else company_dict[company_name]

    # Include "5 years" in the time period selection
    period = st.sidebar.selectbox("Select time period", ["1mo", "3mo", "6mo", "1y", "5y"])

    # Download data for the selected company
    company_data = yf.Ticker(ticker)
    hist_data = company_data.history(period=period)

    # Convert datetime indices to naive
    hist_data.index = hist_data.index.tz_localize(None)

    # Provide some company information
    st.subheader(f"Company Information: {company_name}")
    st.write(f"**Ticker:** {ticker}")
    st.write(f"**Sector:** {company_data.info.get('sector', 'N/A')}")
    st.write(f"**Industry:** {company_data.info.get('industry', 'N/A')}")
    st.write(f"**Market Cap:** ${company_data.info.get('marketCap', 'N/A'):,}")
    st.write(f"**P/E Ratio:** {company_data.info.get('trailingPE', 'N/A')}")

    # Color picker for the line chart
    line_color = st.sidebar.color_picker("Pick a color for the line", "#FF5733")

    # Performance Metrics
    st.subheader(f"Performance Metrics for {company_name} over the selected period")
    price_change = (hist_data['Close'][-1] - hist_data['Close'][0]) / hist_data['Close'][0] * 100
    st.write(f"**Price Change:** {price_change:.2f}%")
    st.write(f"**Average Daily Volume:** {hist_data['Volume'].mean():,.0f}")

    # Plotting the close price line chart with the selected color
    plt.figure(figsize=(10, 6))
    sns.lineplot(x=hist_data.index, y=hist_data['Close'], color=line_color)
    plt.title(f"{company_name} Price Data")
    plt.xlabel("Date")
    plt.ylabel("Close Price")
    st.pyplot(plt)

    # Show summary statistics
    st.write(hist_data.describe())

    # Calculate relative and absolute changes
    hist_data['Absolute Change'] = hist_data['Close'].diff()
    hist_data['Relative Change (%)'] = hist_data['Close'].pct_change() * 100

    # Plotting Absolute and Relative changes side by side
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # Plot Absolute Change
    sns.lineplot(ax=axes[0], x=hist_data.index, y=hist_data['Absolute Change'], color="blue")
    axes[0].set_title(f"{company_name} Absolute Change")
    axes[0].set_xlabel("Date")
    axes[0].set_ylabel("Absolute Change")

    # Plot Relative Change
    sns.lineplot(ax=axes[1], x=hist_data.index, y=hist_data['Relative Change (%)'], color="green")
    axes[1].set_title(f"{company_name} Relative Change (%)")
    axes[1].set_xlabel("Date")
    axes[1].set_ylabel("Relative Change (%)")

    # Display the plot
    st.pyplot(fig)

    #### Regression Analysis #####
    st.subheader("Regression Analysis")

    # Download S&P 500 data (for regression)
    sp500 = yf.download("^GSPC", period=period)
    sp500.index = sp500.index.tz_localize(None)

    # Calculate daily returns
    hist_data['Return'] = hist_data['Close'].pct_change().dropna()
    sp500['Return'] = sp500['Close'].pct_change().dropna()

    # Align the data on dates
    aligned_data = pd.concat([hist_data['Return'], sp500['Return']], axis=1).dropna()
    aligned_data.columns = ['Company Return', 'Market Return']

    # Add a constant to the independent variable which is required for statsmodels regression
    X = sm.add_constant(aligned_data['Market Return'])
    y = aligned_data['Company Return']

    # Perform the regression
    model = sm.OLS(y, X).fit()

    # Explanation of Beta (β) values
    st.write("""
    ### Understanding Beta (β) Values
    - **Beta (β):** This value represents the sensitivity of the company's stock returns relative to the market returns.
    - **β > 1** indicates that the company's stock is more volatile than the market. For example, if β = 1.5, the stock tends to move 1.5 times the market return.
    - **β < 1** indicates that the company's stock is less volatile than the market. For example, if β = 0.5, the stock tends to move only 50% of the market return.
    - **β = 1** suggests the company's stock moves in line with the market.
    - **Adjusted R-squared:** This value measures the proportion of the stock's movement explained by the market's movement. A higher R-squared indicates a better fit.
    """)

    # Display regression results
    st.write(f"**Beta (Exposure to Market):** {model.params['Market Return']:.2f}")
    st.write(f"**Adjusted R-squared:** {model.rsquared_adj:.2f}")

    # Regression line Plot
    st.subheader(f"{company_name} vs Market Return")
    plt.figure(figsize=(10, 6))
    plt.scatter(aligned_data['Market Return'], aligned_data['Company Return'], alpha=0.5)
    plt.plot(aligned_data['Market Return'], model.predict(X), color=line_color, linewidth=2)
    plt.xlabel("Market Return (S&P 500)")
    plt.ylabel(f"{company_name} Return")
    plt.title(f"{company_name} Return vs Market Return")
    st.pyplot(plt)
