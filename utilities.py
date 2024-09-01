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
from streamlit_option_menu import option_menu
from wordcloud import WordCloud
from datetime import datetime, timedelta