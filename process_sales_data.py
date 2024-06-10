import streamlit as st


def skip_rows(df):
    df = df.iloc[3:]
    return df

def remove_rows_with_totals(df):
    df = df[~df.applymap(lambda x: 'totals' in str(x).strip().lower()).any(axis=1)]
    return df

def replace_nan_with_partnumber(df):
    df.iloc[:, 0] = df.iloc[:, 0].fillna(method='ffill')
    df.iloc[:, 1] = df.iloc[:, 1].fillna(method='ffill')
    df.iloc[:, 2] = df.iloc[:, 2].fillna(method='ffill')
    return df

@st.cache_data
def process_sales(df):
        
        df = (df           
        .pipe(remove_rows_with_totals)
        .pipe(replace_nan_with_partnumber)
        .rename(columns = {'PartNumber': 'partnumber', 
                           'ΧΡΩΜΑ': 'color', 
                           'ΜΕΓΕΘΟΣ': 'size', 
                           'Υποκ/μα': 'store', 
                           'Ποσ': 'returns',
                           'Ποσ.1': 'store_sales',
                           'Ποσ.2': 'store_stock'})
        .fillna(0)
        .reset_index(drop=True) 
        )

        return df

