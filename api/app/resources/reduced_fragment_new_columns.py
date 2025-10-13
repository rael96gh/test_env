import yfinance as yf
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import time

# ------------------ Configuration ------------------
TICKERS = [
    "PG", "KO", "WMT", "COST", "JNJ", "PFE", "UNH",
    "NEE", "DUK", "DG", "MSFT", "CRWD", "MET", "ALL"
]
REFRESH_INTERVAL = 60 * 60 * 24  # 24 hours

# ------------------ Data Fetching ------------------
@st.cache_data(ttl=REFRESH_INTERVAL)
def get_stock_data(tickers):
    data = []

    for ticker in tickers:
        stock = yf.Ticker(ticker)
        info = stock.info

        try:
            row = {
                "Ticker": ticker,
                "Company": info.get("shortName", "N/A"),
                "Sector": info.get("sector", "N/A"),
                "Market Cap": info.get("marketCap", 0),
                "PE Ratio": info.get("trailingPE", None),
                "Debt/Equity": info.get("debtToEquity", None),
                "Current Ratio": info.get("currentRatio", None),
                "ROE": info.get("returnOnEquity", None),
                "Dividend Yield (%)": round(info.get("dividendYield", 0) * 100, 2) if info.get("dividendYield") else 0,
                "Beta": info.get("beta", None),
                "5Y EPS Growth (%)": info.get("earningsQuarterlyGrowth", None)
            }
            data.append(row)
        except Exception as e:
            st.warning(f"Error retrieving {ticker}: {e}")

    df = pd.DataFrame(data)
    return df

# ------------------ Filtering Logic ------------------
def apply_filters(df):
    filtered = df[
        (df["PE Ratio"] < 25) &
        (df["Debt/Equity"] < 0.8) &
        (df["Current Ratio"] > 1.2) &
        (df["ROE"] > 0.1) &
        (df["Dividend Yield (%)"] > 2) &
        (df["Beta"] < 1)
    ]
    return filtered

# ------------------ Streamlit Dashboard ------------------
st.set_page_config(page_title="Recession-Resilient Stock Screener", layout="wide")
st.title("🛡️ Recession-Resilient Stock Screener")
st.caption("Updated daily | Filters: PE<25, D/E<0.8, Current Ratio>1.2, ROE>10%, Dividend>2%, Beta<1")

with st.spinner("Fetching stock data..."):
    df = get_stock_data(TICKERS)
    filtered_df = apply_filters(df)

st.subheader("📈 Filtered Stocks")
st.dataframe(filtered_df, use_container_width=True)

# ------------------ Visualizations ------------------
st.subheader("📊 Visualizations")

col1, col2 = st.columns(2)

with col1:
    sector_counts = filtered_df['Sector'].value_counts()
    fig1, ax1 = plt.subplots()
    ax1.pie(sector_counts, labels=sector_counts.index, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    st.pyplot(fig1)
    st.caption("Sector Distribution")

with col2:
    fig2, ax2 = plt.subplots()
    filtered_df.set_index("Ticker")["Dividend Yield (%)"].plot(kind='bar', ax=ax2, color='skyblue')
    ax2.set_ylabel("Dividend Yield (%)")
    ax2.set_title("Dividend Yields of Filtered Stocks")
    st.pyplot(fig2)

# ------------------ CSV Export ------------------
st.download_button(
    label="💾 Download Filtered Stocks as CSV",
    data=filtered_df.to_csv(index=False),
    file_name="recession_resilient_filtered_stocks.csv",
    mime="text/csv"
)

st.success("Dashboard updated successfully!")
