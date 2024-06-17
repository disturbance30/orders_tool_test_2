import streamlit as st
import pandas as pd



def set_header(df):
    for i in range(5):
        if df.iloc[i, 0] == 'Είδος/PartNumber':
            df.columns = df.iloc[i]
            df = df.iloc[i+1:]
            break
    return df


def remove_rows_with_totals(df):
    df = df[~df.applymap(lambda x: 'totals' in str(x).strip().lower()).any(axis=1)]
    return df

def fill_na_categorical(df):
    df.iloc[:,:3] = df.iloc[:,:3].ffill()
    return df


def add_stores_missing_stock(df, df_sales):
    
    # List of unique stores required for each combination
    required_stores = df_sales['Υποκατάστημα'].dropna().unique()
    required_stores_df = pd.DataFrame(required_stores, columns=['Υποκατάστημα'])

    # Identifying all unique combinations of partnumber, color, size
    unique_combos = df[['partnumber', 'color', 'size']].drop_duplicates()

    # Creating a Cartesian product of unique combinations and required stores
    combo_stores_df_sales = unique_combos.assign(key=1).merge(required_stores_df.assign(key=1), on='key').drop('key', axis=1)

    df = pd.merge(combo_stores_df_sales, df, how='inner', on=['partnumber', 'color', 'size'])

    return df



@st.cache_data
def process_stock(df, df_sales):

    rename_dict = {
        'Είδος/PartNumber': 'partnumber',
        'ΧΡΩΜΑ': 'color',
        'ΜΕΓΕΘΟΣ': 'size',
        'Αποθ/Εισαγωγές': 'wh_imports',
        'Αποθ/Εξαγωγές': 'wh_exports',
        'Αποθ/Υπόλοιπο': 'wh_stock',
        'ΕκκρΠαραγγ/Προμ.Ανεκτ.': 'outstanding_orders_supliers',
        'ΕκκρΠαραγγ/Πελ.Ανεκτ.': 'outstanding_orders_customers',
        'Προβλ.Υπολ.': 'projected_balance'
    }

    columns_to_keep = list(rename_dict.values())

    df = (df 
            .pipe(set_header)
            .pipe(remove_rows_with_totals)
            .pipe(fill_na_categorical)       
            .rename(columns = rename_dict)
            .loc[:, columns_to_keep]
            .fillna(0)
            .pipe(add_stores_missing_stock, df_sales)
            .reset_index(drop=True) 
            )
    
    return df

