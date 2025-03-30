import streamlit as st
import pandas as pd
import plotly.express as px

# Data Loading and Preprocessing
@st.cache_data
def load_data():
    df = pd.read_csv(r"D:\Data since\Epsilon AI\DSP\mid_project\food_order.csv")
    
    # Data cleaning
    df['Discounts and Offers'].fillna(0, inplace=True)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '')
    df.drop('order_id', axis=1, inplace=True)
    
    # Datetime conversion
    df[['order_date_and_time', 'delivery_date_and_time']] = df[['order_date_and_time', 'delivery_date_and_time']].apply(pd.to_datetime)
    
    # Date features
    df['order_year'] = df['order_date_and_time'].dt.year
    df['order_month'] = df['order_date_and_time'].dt.month_name()
    df['order_day'] = df['order_date_and_time'].dt.day_name()
    df['order_week'] = df['order_date_and_time'].dt.weekday
    df['order_day_of_month'] = df['order_date_and_time'].dt.day
    df['order_hour'] = df['order_date_and_time'].dt.hour
    
    # Numeric conversions
    numeric_cols = ['order_value', 'delivery_fee', 'commission_fee', 
                   'payment_processing_fee', 'refunds/chargebacks']
    df[numeric_cols] = df[numeric_cols].astype('float')
    
    # Discount processing
    df['discount_value'] = df['discounts_and_offers'].str.extract(r'(\d+)').astype('float')
    df['discount_source'] = df['discounts_and_offers'].str.replace(r'(\d+%)', '', regex=True).str.strip()
    df.drop(['discounts_and_offers'], axis=1, inplace=True)
    
    return df

df = load_data()

# Streamlit App
st.title('Food Delivery Service Data Analysis')
st.write('Interactive dashboard for analyzing food delivery service metrics')

# Sidebar filters
st.sidebar.header('Filters')
selected_year = st.sidebar.selectbox('Select Year', options=sorted(df['order_year'].unique()))
selected_month = st.sidebar.multiselect('Select Month', options=sorted(df['order_month'].unique()))

# Apply filters
filtered_df = df.copy()
if selected_year:
    filtered_df = filtered_df[filtered_df['order_year'] == selected_year]
if selected_month:
    filtered_df = filtered_df[filtered_df['order_month'].isin(selected_month)]

# Main dashboard
tab1, tab2, tab3 = st.tabs(["Sales Analysis", "Customer Behavior", "Financial Metrics"])

with tab1:
    st.header("Sales Performance")
    
    col1, col2 = st.columns(2)
    with col1:
        # Monthly Order Value
        monthly_sales = filtered_df.groupby('order_month')['order_value'].sum().reset_index()
        fig = px.bar(monthly_sales, x='order_month', y='order_value', 
                     title='Total Order Value by Month', color='order_value')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Orders by Day of Week
        daily_orders = filtered_df['order_day'].value_counts().reset_index()
        fig = px.bar(daily_orders, x='order_day', y='count', 
                     title='Orders by Day of Week', color='count')
        st.plotly_chart(fig, use_container_width=True)
    
    # Hourly Order Pattern
    hourly_orders = filtered_df['order_hour'].value_counts().sort_index().reset_index()
    fig = px.line(hourly_orders, x='order_hour', y='count', 
                 title='Orders by Hour of Day', markers=True)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Customer Behavior")
    
    col1, col2 = st.columns(2)
    with col1:
        # Payment Methods
        payment_data = filtered_df['payment_method'].value_counts().reset_index()
        fig = px.pie(payment_data, values='count', names='payment_method', 
                    title='Payment Method Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Discount Sources
        discount_data = filtered_df['discount_source'].value_counts().reset_index()
        fig = px.pie(discount_data, values='count', names='discount_source', 
                    title='Discount Source Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    # Discount Impact
    fig = px.scatter(filtered_df, x='discount_value', y='order_value',
                    title='Impact of Discounts on Order Value',
                    trendline='ols')
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Financial Metrics")
    
    col1, col2 = st.columns(2)
    with col1:
        # Delivery Fees
        st.metric("Total Delivery Fees", f"${filtered_df['delivery_fee'].sum():,.2f}")
    
    with col2:
        # Commission Fees
        st.metric("Total Commission Fees", f"${filtered_df['commission_fee'].sum():,.2f}")
    
    # Commission Distribution
    filtered_df['commission_percentage'] = (filtered_df['commission_fee'] / filtered_df['order_value']) * 100
    fig = px.box(filtered_df, y='commission_percentage', 
                title='Commission Percentage Distribution')
    st.plotly_chart(fig, use_container_width=True)

# Data Explorer
st.header("Data Explorer")
if st.checkbox('Show raw data'):
    st.dataframe(filtered_df)
    
if st.checkbox('Show summary statistics'):
    st.write(filtered_df.describe())
