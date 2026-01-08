# app.py - revised (SQL WORKING + 4 IMPORTANT VISUALS)

import streamlit as st
import pandas as pd
import pyodbc
import os
import re
import pymysql
from config import DB_CONFIG

st.set_page_config(page_title="Ola Ride Insights", layout="wide")
st.title("Ola Ride Insights | SQL & Power BI Analytics")

# -----------------------------
# DB connection helpers
# -----------------------------
def get_conn():
    return pymysql.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        port=DB_CONFIG["port"],
        ssl={"ssl": {}},   # required for TiDB Cloud
        cursorclass=pymysql.cursors.DictCursor
    )

def test_connection():
    try:
        conn = get_conn()
        conn.close()
        return True, "Connected to database successfully"
    except Exception as e:
        return False, str(e)

ok, msg = test_connection()
if ok:
    st.success(msg)
else:
    st.error("Database connection failed: " + msg)

# -----------------------------
# Load base table
# -----------------------------
@st.cache_data(ttl=600)
def load_base_table():
    conn = get_conn()
    query = """
    SELECT
        Date,
        Booking_ID,
        Booking_Status,
        Vehicle_Type,
        Booking_Value,
        Payment_Method,
        Ride_Distance,
        Driver_Ratings,
        Customer_Rating
    FROM dbo.ola_rides_july_clean
    """
    df = pd.read_sql(query, conn)
    conn.close()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df

df = load_base_table()

# -----------------------------
# Sidebar filters
# -----------------------------
st.sidebar.header("Filters")
vehicle = st.sidebar.multiselect(
    "Vehicle Type",
    sorted(df["Vehicle_Type"].dropna().unique()),
    default=sorted(df["Vehicle_Type"].dropna().unique())
)
status = st.sidebar.multiselect(
    "Booking Status",
    sorted(df["Booking_Status"].dropna().unique()),
    default=sorted(df["Booking_Status"].dropna().unique())
)

filtered_df = df[
    (df["Vehicle_Type"].isin(vehicle)) &
    (df["Booking_Status"].isin(status))
]

# -----------------------------
# KPI Section
# -----------------------------
st.subheader("Key Metrics")
c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Rides", len(filtered_df))
c2.metric("Completed Rides", filtered_df[filtered_df["Booking_Status"] == "Success"].shape[0])
c3.metric(
    "Total Revenue",
    f"₹ {filtered_df.loc[filtered_df['Booking_Status'] == 'Success', 'Booking_Value'].sum():,.0f}"
)
c4.metric(
    "Avg Ride Distance (km)",
    round(filtered_df["Ride_Distance"].mean(), 2)
)

st.divider()

# -----------------------------
# VISUAL 1: Ride Volume Over Time
# -----------------------------
st.subheader("Ride Volume Over Time")

ride_trend = (
    filtered_df
    .dropna(subset=["Date"])
    .groupby(filtered_df["Date"].dt.date)
    .size()
)

st.line_chart(ride_trend)

# -----------------------------
# VISUAL 2: Booking Status Breakdown
# -----------------------------
st.subheader("Booking Status Breakdown")
status_counts = filtered_df["Booking_Status"].value_counts()
st.bar_chart(status_counts)

# -----------------------------
# VISUAL 3: Revenue by Payment Method
# -----------------------------
st.subheader("Revenue by Payment Method")

revenue_payment = (
    filtered_df[filtered_df["Booking_Status"] == "Success"]
    .groupby("Payment_Method")["Booking_Value"]
    .sum()
)

st.bar_chart(revenue_payment)

# -----------------------------
# VISUAL 4: Average Ratings Comparison
# -----------------------------
st.subheader("Average Ratings Comparison")

ratings_df = pd.DataFrame({
    "Rating Type": ["Customer Rating", "Driver Rating"],
    "Average Rating": [
        filtered_df["Customer_Rating"].mean(),
        filtered_df["Driver_Ratings"].mean()
    ]
})

st.bar_chart(ratings_df.set_index("Rating Type"))

st.divider()

# -----------------------------
# SQL QUERY EXECUTOR (UNCHANGED & WORKING)
# -----------------------------
st.subheader("Run SQL Queries")

def load_sql_file(path="SQLQuery1.sql"):
    if not os.path.exists(path):
        return {}

    text = open(path, "r", encoding="utf-8").read()
    parts = re.split(r'--\s*name\s*:\s*(.+)', text, flags=re.IGNORECASE)

    queries = {}
    for i in range(1, len(parts), 2):
        queries[parts[i].strip()] = parts[i + 1].strip()

    return queries

sql_queries = load_sql_file()

query_name = st.selectbox(
    "Select Predefined SQL Query",
    ["-- Select --"] + list(sql_queries.keys())
)

sql_text = st.text_area(
    "SQL Query",
    value=sql_queries.get(query_name, ""),
    height=180
)

if st.button("Run Query"):
    if sql_text.strip() == "":
        st.warning("Please enter a SQL query")
    else:
        try:
            conn = get_conn()
            result_df = pd.read_sql(sql_text, conn)
            conn.close()

            st.success(f"Returned {len(result_df)} rows")
            st.dataframe(result_df)

            csv = result_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download CSV",
                csv,
                "query_result.csv",
                "text/csv"
            )
        except Exception as e:
            st.error(str(e))

st.divider()

# -----------------------------
# Power BI Dashboard
# -----------------------------
st.subheader("Power BI Dashboard")

st.components.v1.iframe(
    "https://app.powerbi.com/reportEmbed?"
    "reportId=8dfeb7fc-42e5-453b-ac57-06eaf7511330"
    "&autoAuth=true"
    "&ctid=136fe6a7-243d-45b5-93a1-0ab9c53fb298",
    height=720,
    width=1200
)