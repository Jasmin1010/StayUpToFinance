import streamlit as st
from streamlit_option_menu import option_menu
import pages.market_overview as mo
import pages.financial_news as fn
import pages.company_analysis as ca
import pages.market_guide as mg

# Initialize dark mode state
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# Toggle function for dark mode
def switch_dark_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode

# Custom CSS for aligning the checkbox to the right
st.markdown(
    """
    <style>
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 20px;
    }
    .dark-mode-toggle {
        text-align: right;
    }
    .info-button-container {
        margin-top: 10px;
        text-align: left;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header container with dark mode toggle and navigation menu
st.markdown('<div class="header-container">', unsafe_allow_html=True)

# Dark/White mode toggle checkbox aligned to the right
st.markdown('<div class="dark-mode-toggle">', unsafe_allow_html=True)

# Adjust the text color of the "Dark Mode" checkbox based on the mode
dark_mode_text_color = "white" if st.session_state.dark_mode else "black"
st.markdown(
    f"""
    <style>
    .st-checkbox .st-bk {{
        color: {dark_mode_text_color};
    }}
    </style>
    """,
    unsafe_allow_html=True
)
st.checkbox("Dark Mode", value=st.session_state.dark_mode, on_change=switch_dark_mode)

# Information button for app details
st.markdown('<div class="info-button-container">', unsafe_allow_html=True)

# Adjust the text color of the "Information" button based on the mode
info_button_text_color = "white" if st.session_state.dark_mode else "black"
if st.button("ℹ️ Information about the app", help="Click for more details"):
    st.session_state.show_help = not st.session_state.get("show_help", False)
    st.markdown(
        f"""
        <style>
        .stButton button {{
            color: {info_button_text_color};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Display help content in an expandable section as requested in assigment description: "All parts of the assignment should contain short and precise explanations of individual components of the pages".
if st.session_state.get("show_help", False):
    with st.expander("App Information"):
        st.write("""
        **Stay Up to Finance** is an app designed to keep you informed about the latest financial trends and market data. Here’s what each section offers:

        - **Market Overview**: When you enter the page, you'll first encounter options to select the type of financial market you're interested in, such as stocks, bonds, cryptocurrencies, commodities, forex, or real estate. Depending on your choice, the page adjusts to present relevant data.
            If you choose to view stock market information, you can select a specific company or stock from a pre-defined list, such as Apple or Microsoft, or enter a custom ticker symbol. For stocks, the page allows you to compare the performance of the selected stock against a major benchmark index, like the S&P 500 or NASDAQ Composite. You can also pick the time period for this comparison, ranging from the past month to a year.
            Once you've made your selections, the page downloads the relevant stock and benchmark data. The visualizations then display the normalized price data for both the stock and the benchmark index. Normalization adjusts the prices so that they start at the same level, making it easier to compare their relative movements over time. For other markets, such as bonds, cryptocurrencies, commodities, forex, or real estate, the page adapts to show data specific to those categories. You'll select a relevant ticker symbol from a list or enter your own. For these markets, the page provides visualizations of price data, moving averages, and trading volume.
            In the case of bonds, cryptocurrencies, commodities, forex, or real estate, you'll see a line plot showing the price data over time. For a more in-depth analysis, you can view moving averages, which smooth out price fluctuations to show longer-term trends. The page also includes a volume analysis, which displays the trading volume as a bar chart to give insight into the trading activity.
            Finally, the page concludes with descriptive statistics for the selected data. This summary provides key metrics such as the mean, median, and standard deviation, offering a snapshot of the data's performance.
        - **Financial News**: In the sidebar, you have several controls that let you customize your news feed to suit your interests. You can begin by entering a keyword, such as "stock market," to search for news related to that topic. You also have the option to select from a variety of news sources.The timeframe selection allows you to choose between seeing news from today, the last 7 days, or the last 30 days, helping you focus on recent or slightly older news.
            For further customization, you can filter the news based on sentiment. This means you can choose to see only positive, negative, or neutral news, or view all sentiment types. Additionally, there's an option to pick a color for the sentiment graph, allowing you to personalize how the sentiment distribution appears visually.If you decide to click the button to display the sentiment graph, you'll be presented with a bar chart that shows the distribution of sentiments across the news articles. This graph helps you quickly understand how many articles fall into each sentiment category, with the color of the bars reflecting your chosen color.
            Another feature you can access by clicking the button for the word cloud is a visual representation of common words used in the news descriptions. This word cloud helps you easily spot frequently mentioned topics or trends in the financial news.
        - **Company Analysis**: This page offers a comprehensive analysis of selected companies with several interactive features. Users can choose from a list of popular stock tickers or enter a custom ticker to fetch detailed historical data for the selected period, including up to five years. The page presents essential company information such as sector, industry, market cap, and P/E ratio. It then visualizes price changes and average daily volume through customizable line charts.
            Additionally, the page provides insights into absolute and relative changes in stock prices and performs a regression analysis against the S&P 500 to calculate and explain the company’s beta value and its market sensitivity.
        - **Market Guide**: This page provides a comprehensive overview of investment strategies and market sentiment indicators. It features the Fear and Greed Index, which helps gauge investor sentiment by measuring levels of fear and greed in the market. You can select a company to view its financial metrics and historical performance, and compare them against industry averages to evaluate different investment strategies, such as Dividend Growth, Dividend Yield, and Profit Growth. The page also calculates and displays scores for these strategies based on company data and reference values, helping you decide which investment approach aligns best with your goals. Finally, it presents historical performance data and offers guidance on selecting the most suitable investment strategy.

        Use the dark mode box to switch between light and dark themes for a more comfortable viewing experience.
        """)

# Navigation menu 
selected = option_menu(
    None,
    ["Market Overview", "Financial News", "Company Analysis", "Market Guide"],
    icons=["activity", "newspaper", "building", "arrow-90deg-up"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "nav-link": {"flex-direction": "column"},
    }
)

# Apply dark mode styles if active
if st.session_state.dark_mode:
    st.markdown(
        """
        <style>
        .main {
            background-color: #1c1c1c;
            color: white;
        }
        .css-1d391kg {
            background-color: #1c1c1c;
        }
        h1, h2, h3, h4, h5, h6 {
            color: white;
        }
        .st-expander-content {
            background-color: #2c2c2c;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <style>
        .main {
            background-color: white;
            color: black;
        }
        .css-1d391kg {
            background-color: white;
        }
        h1, h2, h3, h4, h5, h6 {
            color: black;
        }
        .st-expander-content {
            background-color: white;
            color: black;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Function to display app name at the top
def app_name(dark_mode=False):
    text_color = "white" if dark_mode else "black"
    st.markdown(
        f"""
        <h1 style='text-align: center; color: {text_color}; font-family: Arial, sans-serif;'>
        Stay Up to Finance
        </h1>
        <hr style="border: 1px solid #ccc;">
        """, 
        unsafe_allow_html=True
    )

# Call the header function with the dark_mode parameter
app_name(dark_mode=st.session_state.dark_mode)

# Page routing
if selected == "Market Overview":
    import pages.market_overview as mo
    mo.display()
elif selected == "Financial News":
    import pages.financial_news as fn
    fn.display()
elif selected == "Company Analysis":
    import pages.company_analysis as ca
    ca.display()
elif selected == "Market Guide":
    import pages.market_guide as mg
    mg.display()