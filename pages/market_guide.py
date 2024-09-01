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
from datetime import datetime


def fetch_fear_and_greed_index():
    """Fetch the current Fear and Greed Index."""
    url = "https://api.alternative.me/fng/?limit=1"  # API for Fear and Greed Index
    response = requests.get(url)
    data = response.json()
    if data and data.get("data"):
        return data["data"][0]
    return None

def display():
    st.title("Market Guide")

    # Initialize reference_values with default values or fetch them from a data source
    reference_values = {
        'dividend_yield': 0.02,  # Example default value (2%)
        'dividend_growth': 0.05,  # Example default value (5%)
        'profit_growth': 0.03  # Example default value (3%)
    }

    # Fetch the Fear and Greed Index
    fng_data = fetch_fear_and_greed_index()

    if fng_data:
        st.subheader("Fear and Greed Index")
        st.write("""
        #### Information on fear and greed index
        The Fear and Greed Index aims to capture two fundamental emotions that drive market behavior: fear and greed.
        Fear Indicators might include metrics such as market volatility, put/call ratios (which measure investor sentiment about market declines), and other signs that suggest caution or concern among investors.
        Greed Indicators might encompass metrics such as stock market momentum, market breadth (the number of stocks advancing vs. declining), and other signs of optimistic or bullish behavior.
        """)
    st.write("""
        #### Interpreting the Index
        - 0-25 (Extreme Fear): This range indicates that investors are highly fearful, which might suggest that the market is experiencing significant stress or uncertainty. Extreme fear often accompanies market downturns and can signal potential buying opportunities if the fear is overblown.
        - 26 to 49 (Fear): This range shows that there is a general atmosphere of fear in the market, but it is less intense than extreme fear. Investors might be cautious, and the market could be experiencing volatility or downward pressure.
        - 50 to 74 (Greed): This range suggests that investors are generally feeling optimistic and are more inclined towards risk-taking. Greed can drive market rallies, but it may also indicate that the market is overheated and due for a correction.
        - 75 to 100 (Extreme Greed): This range represents a high level of investor enthusiasm and risk-taking. Extreme greed can be a warning sign that the market is overheated and could be due for a pullback or correction.
        """)
    st.write(f"***Current Index Value***: {fng_data['value']} ({fng_data['value_classification']})")

    # Visual representation of Fear and Greed
    fig, ax = plt.subplots()
    ax.barh(["Fear and Greed Index"], [int(fng_data['value'])], color="orange")
    ax.set_xlim([0, 100])
    ax.set_title("Fear and Greed Index")
    st.pyplot(fig)

    # Function to fetch stock information and metrics
    def get_stock_info(ticker):
        stock = yf.Ticker(ticker)
        info = stock.info

        metrics = {
            "dividend_yield": info.get("dividendYield", None),
            "payout_ratio": info.get("payoutRatio", None),
            "revenue_growth": info.get("revenueGrowth", None),
            "earnings_growth": info.get("earningsGrowth", None),
            "trailing_pe": info.get("trailingPE", None),
            "dividend_growth_5y": info.get("dividendGrowthRate5Y", None),
            "industry": info.get("industry", None),
            "sector": info.get("sector", None),
        }
        return metrics

    # Function to safely calculate returns for a given period
    def safe_return(hist, periods):
        try:
            return (hist["Close"][-1] / hist["Close"].iloc[-periods] - 1) * 100
        except IndexError:
            return "N/A"

    # Function to fetch historical stock prices and calculate returns
    def get_historical_returns(ticker):
        stock = yf.Ticker(ticker)
        hist = stock.history(period="max")

        # Calculate returns for each time period
        returns = {
            "20_years": safe_return(hist, 20 * 252),  # 252 trading days in a year
            "15_years": safe_return(hist, 15 * 252),
            "10_years": safe_return(hist, 10 * 252),
            "5_years": safe_return(hist, 5 * 252),
            "1_year": safe_return(hist, 252),
            "current_year": safe_return(hist, len(hist[hist.index >= f'{datetime.now().year}-01-01'])),  # From start of current year
        }
        return returns

    # Function to evaluate metrics for each strategy
    def evaluate_dividend_growth(metrics, reference_values):
        if metrics['dividend_growth_5y'] is not None and metrics['payout_ratio'] is not None:
            score = min(10, (metrics['dividend_growth_5y'] * 4) + (1 - metrics['payout_ratio']) * 6)
        else:
            score = 5  # Default score if data is missing
        return round(score), reference_values['dividend_growth']

    def evaluate_dividend_yield(metrics, reference_values):
        if metrics['dividend_yield'] is not None:
            score = min(10, metrics['dividend_yield'] * 15)
        else:
            score = 5  # Default score if data is missing
        return round(score), reference_values['dividend_yield']

    def evaluate_profit_growth(metrics, reference_values):
        if metrics['revenue_growth'] is not None and metrics['earnings_growth'] is not None:
            score = min(10, ((metrics['revenue_growth'] + metrics['earnings_growth']) / 2) * 20)
        else:
            score = 5  # Default score if data is missing
        return round(score), reference_values['profit_growth']

    # Reference values for the industry (example values)
    reference_values = {
        "dividend_yield": 0.015,  # 1.5% average for tech/consumer electronics
        "dividend_growth": 0.08,  # 8% average 5-year dividend growth
        "profit_growth": 0.10,    # 10% average revenue and earnings growth
    }

    # Sidebar with company and ticker selection
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
    company_name = custom_ticker.upper() if custom_ticker else company_dict[company_name]

    # Get stock metrics and historical returns
    metrics = get_stock_info(company_name)
    returns = get_historical_returns(company_name)


    # Calculate scores with industry references
    dividend_growth_score, div_growth_ref = evaluate_dividend_growth(metrics, reference_values)
    dividend_yield_score, div_yield_ref = evaluate_dividend_yield(metrics, reference_values)
    profit_growth_score, profit_growth_ref = evaluate_profit_growth(metrics, reference_values)

    # Prepare formatted values for the table
    dividend_yield = f"{metrics['dividend_yield']:.2%}" if metrics['dividend_yield'] is not None else "N/A"
    payout_ratio = f"{metrics['payout_ratio']:.2%}" if metrics['payout_ratio'] is not None else "N/A"
    pe_ratio = f"{metrics['trailing_pe']:.2f}" if metrics['trailing_pe'] is not None else "N/A"
    revenue_growth = f"{metrics['revenue_growth']:.2%}" if metrics['revenue_growth'] is not None else "N/A"
    earnings_growth = f"{metrics['earnings_growth']:.2%}" if metrics['earnings_growth'] is not None else "N/A"
    dividend_growth_5y = f"{metrics['dividend_growth_5y']:.2%}" if metrics['dividend_growth_5y'] is not None else "N/A"

    # Dividend Growth Strategy Section
    with st.container():
        st.subheader(f"View different Investment Strategies for company {company_name}")
        st.markdown("### Dividend Growth Strategy")
        st.write("The Dividend Growth Strategy focuses on investing in stocks that consistently increase their dividend payouts over time. The primary goal of this strategy is to achieve a steady and growing income stream through dividends, alongside potential capital appreciation. Investors who adopt this strategy look for companies with a history of regularly increasing their dividends, indicating financial health and stability. This strategy is particularly appealing to those seeking reliable income and lower volatility in their investment portfolio.")

        st.markdown(f"**Dividend Growth Score: {dividend_growth_score}/10**")

        if dividend_growth_score >= 7:
            st.success("This stock is well-suited for a Dividend Growth Strategy.")
        else:
            st.warning("This stock may not be ideal for a Dividend Growth Strategy.")

        st.markdown(f"""
        | Metric                 | Value   | Reference |
        |------------------------|---------|-----------|
        | Dividend Yield         | {dividend_yield}    |  Higher is better |
        | Payout Ratio           | {payout_ratio}      | Lower is better |
        | 5Y Dividend Growth     | {dividend_growth_5y} | Higher is better |
        """)

    # Dividend Yield Strategy Section
    with st.container():
        st.markdown("### Dividend Yield Strategy")
        st.write("The Dividend Yield Strategy is an investment approach focused on selecting stocks or other securities that offer high dividend yields. The dividend yield is calculated as the annual dividend payment divided by the stock's current price, expressed as a percentage. Investors using this strategy prioritize companies with high yields because they provide a substantial income relative to the investment cost. This strategy is often employed by income investors and retirees who prioritize current income over capital appreciation.")

        st.markdown(f"**Dividend Yield Score: {dividend_yield_score}/10**")

        if dividend_yield_score >= 7:
            st.success("This stock is well-suited for a Dividend Yield Strategy.")
        else:
            st.warning("This stock may not be ideal for a Dividend Yield Strategy.")

        st.markdown(f"""
        | Metric                 | Value   |  Reference |
        |------------------------|---------|  -----------|
        | Dividend Yield         | {dividend_yield}    |  Higher is better |
        """)

    # Profit Growth Strategy Section
    with st.container():
        st.markdown("### Profit Growth Strategy")
        st.write("The Profit Growth Strategy is an investment approach focused on selecting stocks or companies that demonstrate strong and consistent growth in profits. This strategy aims to identify businesses with rising earnings and revenue, indicating robust financial health and potential for long-term capital appreciation. Investors using this strategy look for companies that not only have a track record of increasing profits but also show the potential for future profit growth based on their business model, industry trends, and competitive position.")

        st.markdown(f"**Profit Growth Score: {profit_growth_score}/10**")

        if profit_growth_score >= 7:
            st.success("This stock is well-suited for a Profit Growth Strategy.")
        else:
            st.warning("This stock may not be ideal for a Profit Growth Strategy.")

        st.markdown(f"""
        | Metric                 | Value   |  Reference |
        |------------------------|---------|  ----------|
        | Revenue Growth         | {revenue_growth}    |  Higher is better |
        | Earnings Growth        | {earnings_growth}   |  Higher is better |
        | P/E Ratio              | {pe_ratio}          | Lower is better |
        """)

    # Historical Performance Table
    st.markdown("### Historical Performance")
    st.write(f"The following table shows the historical price performance of {company_name} over different time periods.")

    st.markdown(f"""
    | Time Period    | Price Change (%) |
    |----------------|------------------|
    | 20 Years       | {returns['20_years'] if returns['20_years'] != "N/A" else "N/A"}       |
    | 15 Years       | {returns['15_years'] if returns['15_years'] != "N/A" else "N/A"}       |
    | 10 Years       | {returns['10_years'] if returns['10_years'] != "N/A" else "N/A"}       |
    | 5 Years        | {returns['5_years'] if returns['5_years'] != "N/A" else "N/A"}        |
    | 1 Year         | {returns['1_year'] if returns['1_year'] != "N/A" else "N/A"}         |
    | Current Year   | {returns['current_year'] if returns['current_year'] != "N/A" else "N/A"}      |
    """)

    st.markdown("### What's next ?")
    st.write("Based on the provided information and analysis, select the investment strategy that best aligns with your financial goals and objectives. Whether you’re drawn to dividend growth, yield, or profit growth, each approach offers distinct advantages tailored to different investment preferences. Stay informed and engaged with your investments.*Stay up to Finance* wishes you a successful and enjoyable investment journey.")
