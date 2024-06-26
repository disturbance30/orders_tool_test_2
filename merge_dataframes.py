import streamlit as st


@st.cache_data
def merge_sales_stock(df_sales, df_stock):

    import pandas as pd
    df =  pd.merge(df_sales, df_stock, on=['partnumber', 'color', 'size', 'Υποκατάστημα'], how='outer')
    
    df = df.fillna(0)

    return df

