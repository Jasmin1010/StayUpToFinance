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
from wordcloud import WordCloud
from datetime import datetime, timedelta


# def display():
#     st.title("Financial News")

# # Add the fear and greed index to show investor sentiment
# def fetch_fear_and_greed_index():
#     """Fetch the current Fear and Greed Index."""
#     url = "https://api.alternative.me/fng/?limit=1"  # API for Fear and Greed Index
#     response = requests.get(url)
#     data = response.json()
#     if data and data.get("data"):
#         return data["data"][0]
#     return None

# st.write("""
#     ### Information on fear and greed index
#     The Fear and Greed Index aims to capture two fundamental emotions that drive market behavior: fear and greed. 
#     Fear Indicators might include metrics such as market volatility, put/call ratios (which measure investor sentiment about market declines), and other signs that suggest caution or concern among investors.
#     Greed Indicators might encompass metrics such as stock market momentum, market breadth (the number of stocks advancing vs. declining), and other signs of optimistic or bullish behavior.         
# """)
# st.write("""
#     ###  Interpreting the Index
#     - 0-25 (Extreme Fear): This range indicates that investors are highly fearful, which might suggest that the market is experiencing significant stress or uncertainty. Extreme fear often accompanies market downturns and can signal potential buying opportunities if the fear is overblown.
#     - 26 to 49 (Fear): This range shows that there is a general atmosphere of fear in the market, but it is less intense than extreme fear. Investors might be cautious, and the market could be experiencing volatility or downward pressure.
#     - 50 to 74 (Greed): This range suggests that investors are generally feeling optimistic and are more inclined towards risk-taking. Greed can drive market rallies, but it may also indicate that the market is overheated and due for a correction.
#     75 to 100 (Extreme Greed): This range represents a high level of investor enthusiasm and risk-taking. Extreme greed can be a warning sign that the market is overheated and could be due for a pullback or correction.                           
# """)


def display():
    st.title("Financial News")

    # Initialize sentiment analysis model
    sentiment_model = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone")

    # News API Key
    NEWS_API_KEY = "354b352e66194c7b9495d90ed009c509"

    # Function to fetch news articles based on filters
    def fetch_news(keyword, sources, from_date, to_date):
        url = f"https://newsapi.org/v2/everything?q={keyword}&from={from_date}&to={to_date}&apiKey={NEWS_API_KEY}"
        if sources:  # Check if specific sources are selected
            sources_str = ",".join(sources)
            url += f"&sources={sources_str}"
        return requests.get(url).json()

   

    # Sidebar for News Settings
    st.sidebar.subheader("News Settings")
    keyword = st.sidebar.text_input("Enter keyword for news search", "stock market")

    # Multi-select for news sources
    news_sources = st.sidebar.multiselect(
        "Select news sources (you can select multiple)",
        ["bbc-news", "bloomberg", "reuters", "the-wall-street-journal", "business-insider"],
        default=[]
    )

    # Timeframe selection with "Last 7 Days" as default
    timeframe = st.sidebar.selectbox("Select timeframe", ["Today", "Last 7 Days", "Last 30 Days"], index=1)

    # Date filtering based on user selection
    today = datetime.today().strftime('%Y-%m-%d')
    if timeframe == "Today":
        from_date = today
    elif timeframe == "Last 7 Days":
        from_date = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')
    elif timeframe == "Last 30 Days":
        from_date = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')

    # Sentiment filter (Positive/Negative/Neutral)
    sentiment_filter = st.sidebar.selectbox("Filter by Sentiment", ["All", "Positive", "Negative", "Neutral"])

    # Color picker for the graph
    graph_color = st.sidebar.color_picker("Pick a color for the sentiment graph", "#FF5733")

    # Buttons for showing sentiment graph and word cloud
    show_sentiment_graph = st.sidebar.button("Show Sentiment Graph")
    show_wordcloud = st.sidebar.button("Show Word Cloud")

    # Style for the buttons
    st.markdown(
        """
        <style>
        .stButton > button {
            padding: 5px 10px;
            background-color: grey;
            color: white;
            font-size: 14px;
            border-radius: 5px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Fetch the news data
    news_data = fetch_news(keyword, news_sources, from_date, today)

    # # Fetch the Fear and Greed Index
    # fng_data = fetch_fear_and_greed_index()

    # if fng_data:
    #     st.subheader("Current Fear and Greed Index")
    #     st.write(f"**Index Value**: {fng_data['value']} ({fng_data['value_classification']})")
    #     st.write(f"**Last Updated**: {fng_data['timestamp']}")

    #     # Visual representation of Fear and Greed
    #     fig, ax = plt.subplots()
    #     ax.barh(["Fear and Greed Index"], [int(fng_data['value'])], color="orange")
    #     ax.set_xlim([0, 100])
    #     ax.set_title("Fear and Greed Index")
    #     st.pyplot(fig)

    if news_data["status"] != "ok":
        st.error(f"Failed to fetch news articles: {news_data.get('message', 'Unknown error')}")
    else:
        # Count sentiment labels for graph
        sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
        articles = news_data["articles"]
        filtered_articles = []
        wordcloud_text = ""

        for article in articles:
            title = article.get('title')
            description = article.get('description')
            url = article.get('url')

            if description:
                # Perform sentiment analysis on description
                sentiment_desc = sentiment_model(description)[0]
                sentiment_label_desc = sentiment_desc['label']
                sentiment_score_desc = sentiment_desc['score']

                if sentiment_label_desc in sentiment_counts:
                    sentiment_counts[sentiment_label_desc] += 1

                # Filter articles based on sentiment
                if sentiment_filter == "All" or sentiment_filter == sentiment_label_desc:
                    filtered_articles.append((title, description, url, sentiment_label_desc, sentiment_score_desc))

                # Accumulate text for word cloud
                wordcloud_text += f"{description} "

        # Display sentiment graph at the top if the button is clicked
        if show_sentiment_graph:
            st.subheader("Sentiment Overview of the Last Week")

            # Plotting the sentiment distribution graph
            labels = list(sentiment_counts.keys())
            sizes = list(sentiment_counts.values())
            plt.figure(figsize=(8, 5))
            sns.barplot(x=labels, y=sizes, color=graph_color)
            plt.title("Sentiment Distribution")
            plt.xlabel("Sentiment")
            plt.ylabel("Number of Articles")
            st.pyplot(plt)

        # Display word cloud if the button is clicked
        if show_wordcloud:
            st.subheader("Word Cloud of News Descriptions")
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(wordcloud_text)
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            st.pyplot(plt)

        # Display news articles after the graph and word cloud
        st.subheader("Latest Financial News and Sentiment")
        for title, description, url, sentiment_label, sentiment_score in filtered_articles:
            st.write(f"**Title**: [{title}]({url})")
            st.write(f"**Description**: {description}")
            st.write(f"**Sentiment**: {sentiment_label}, **Confidence**: {sentiment_score:.2f}")
            st.write("---")