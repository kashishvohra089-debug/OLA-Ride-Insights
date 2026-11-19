import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="OLA Ride Insights",
    page_icon="🚕",
    layout="wide"
)

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("../Python/ola_cleaned.csv")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df

df = load_data()

# Application title
st.title("🚕 OLA Ride Insights")
st.markdown("### Ride-Sharing & Mobility Analytics Dashboard")
st.markdown(
    "Explore OLA booking trends, revenue, vehicle performance, "
    "cancellations and customer experience."
)

# Sidebar filters
st.sidebar.header("Dashboard Filters")

vehicle_options = sorted(df["Vehicle_Type"].dropna().unique())
selected_vehicles = st.sidebar.multiselect(
    "Select Vehicle Type",
    vehicle_options,
    default=vehicle_options
)

status_options = sorted(df["Booking_Status"].dropna().unique())
selected_status = st.sidebar.multiselect(
    "Select Booking Status",
    status_options,
    default=status_options
)

filtered_df = df[
    df["Vehicle_Type"].isin(selected_vehicles)
    & df["Booking_Status"].isin(selected_status)
].copy()

# Overview KPIs
st.subheader("Overall Performance")

total_bookings = len(filtered_df)
successful_rides = (
    filtered_df["Booking_Status"] == "Success"
).sum()

cancelled_rides = filtered_df["Booking_Status"].isin(
    ["Canceled by Customer", "Canceled by Driver"]
).sum()

total_revenue = filtered_df.loc[
    filtered_df["Booking_Status"] == "Success",
    "Booking_Value"
].sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Bookings", f"{total_bookings:,}")
col2.metric("Successful Rides", f"{successful_rides:,}")
col3.metric("Cancelled Rides", f"{cancelled_rides:,}")
col4.metric("Revenue", f"₹{total_revenue:,.0f}")

st.divider()

# Booking status
st.subheader("Booking Status Breakdown")

status_data = filtered_df["Booking_Status"].value_counts().reset_index()
status_data.columns = ["Booking Status", "Bookings"]

fig_status = px.pie(
    status_data,
    names="Booking Status",
    values="Bookings",
    hole=0.45,
    title="Distribution of Booking Status"
)
st.plotly_chart(fig_status, use_container_width=True)

# Ride volume over time
st.subheader("Ride Volume Over Time")

daily_data = (
    filtered_df.groupby("Date")["Booking_ID"]
    .count()
    .reset_index(name="Bookings")
    .sort_values("Date")
)

fig_trend = px.line(
    daily_data,
    x="Date",
    y="Bookings",
    markers=True,
    title="Daily Booking Trend"
)
st.plotly_chart(fig_trend, use_container_width=True)

# Vehicle analysis
st.divider()
st.subheader("Vehicle Analysis")

vehicle_data = (
    filtered_df.groupby("Vehicle_Type")
    .agg(
        Total_Bookings=("Booking_ID", "count"),
        Total_Distance=("Ride_Distance", "sum")
    )
    .reset_index()
)

fig_vehicle = px.bar(
    vehicle_data,
    x="Vehicle_Type",
    y="Total_Bookings",
    title="Bookings by Vehicle Type",
    text_auto=True
)
st.plotly_chart(fig_vehicle, use_container_width=True)

# Revenue analysis
st.divider()
st.subheader("Revenue Analysis")

successful_data = filtered_df[
    filtered_df["Booking_Status"] == "Success"
]

payment_data = (
    successful_data.groupby("Payment_Method")["Booking_Value"]
    .sum()
    .reset_index()
)

fig_payment = px.pie(
    payment_data,
    names="Payment_Method",
    values="Booking_Value",
    hole=0.4,
    title="Revenue by Payment Method"
)
st.plotly_chart(fig_payment, use_container_width=True)

# Cancellation analysis
st.divider()
st.subheader("Cancellation Analysis")

cancelled_data = filtered_df[
    filtered_df["Booking_Status"].isin(
        ["Canceled by Customer", "Canceled by Driver"]
    )
]

cancel_col1, cancel_col2 = st.columns(2)

with cancel_col1:
    customer_reasons = (
        cancelled_data["Canceled_Rides_by_Customer"]
        .dropna()
        .value_counts()
        .reset_index()
    )
    customer_reasons.columns = ["Reason", "Count"]
    st.plotly_chart(
        px.bar(
            customer_reasons,
            x="Count",
            y="Reason",
            orientation="h",
            title="Customer Cancellation Reasons"
        ),
        use_container_width=True
    )

with cancel_col2:
    driver_reasons = (
        cancelled_data["Canceled_Rides_by_Driver"]
        .dropna()
        .value_counts()
        .reset_index()
    )
    driver_reasons.columns = ["Reason", "Count"]
    st.plotly_chart(
        px.bar(
            driver_reasons,
            x="Count",
            y="Reason",
            orientation="h",
            title="Driver Cancellation Reasons"
        ),
        use_container_width=True
    )

# Ratings analysis
st.divider()
st.subheader("Customer & Driver Ratings")

rating_col1, rating_col2 = st.columns(2)

with rating_col1:
    st.metric(
        "Average Customer Rating",
        f"{filtered_df['Customer_Rating'].mean():.2f}"
    )

with rating_col2:
    st.metric(
        "Average Driver Rating",
        f"{filtered_df['Driver_Ratings'].mean():.2f}"
    )

# Data explorer
st.divider()
st.subheader("Explore Ride Records")

search_id = st.text_input("Search by Booking ID")

if search_id:
    search_results = filtered_df[
        filtered_df["Booking_ID"].astype(str).str.contains(
            search_id, case=False, na=False
        )
    ]
    st.dataframe(search_results, use_container_width=True)
else:
    st.dataframe(filtered_df.head(100), use_container_width=True)

st.caption("OLA Ride Insights | Academic Data Analytics Project")

