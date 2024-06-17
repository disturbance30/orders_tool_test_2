import streamlit as st
import pandas as pd


def remove_rows_with_totals(df):
    df = df[~df.applymap(lambda x: 'totals' in str(x).strip().lower()).any(axis=1)]
    return df

def fill_na_categorical(df):
    df.iloc[:,:3] = df.iloc[:,:3].ffill()
    return df

def set_header(df):
    for i in range(5):
        if df.iloc[i, 0] == 'PartNumber':
            df.columns = df.iloc[i]
            df = df.iloc[i+1:]
            break
    return df





def rename_columns(df):
    df.columns = ['partnumber', 'color', 'size', 'Υποκατάστημα', 'Επιστοφές', 'Πωλήσεις', 'Απόθεμα']
    return df

def add_stores_missing(df):
    
    # List of unique stores required for each combination
    required_stores = df['Υποκατάστημα'].dropna().unique()
    required_stores_df = pd.DataFrame(required_stores, columns=['Υποκατάστημα'])

    # Identifying all unique combinations of partnumber, color, size
    unique_combos = df[['partnumber', 'color', 'size']].drop_duplicates()

    # Creating a Cartesian product of unique combinations and required stores
    combo_stores_df_sales = unique_combos.assign(key=1).merge(required_stores_df.assign(key=1), on='key').drop('key', axis=1)

    df = pd.merge(df, combo_stores_df_sales, how='right', on=['partnumber', 'color', 'size', 'Υποκατάστημα'])

    return df



def process_sales(df):
        
        
        columns_to_keep = ['partnumber', 'color', 'size', 'Υποκατάστημα', 'Επιστοφές', 'Πωλήσεις', 'Απόθεμα']


        df = (df    
        .pipe(set_header)       
        .pipe(remove_rows_with_totals)
        .pipe(fill_na_categorical)
        .pipe(rename_columns)
        .loc[:, columns_to_keep]
        .fillna(0)
        .query('Υποκατάστημα != 0')
        .reset_index(drop=True)
        .pipe(add_stores_missing) 
        )

        return df

