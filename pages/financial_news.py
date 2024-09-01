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