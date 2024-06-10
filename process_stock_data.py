import streamlit as st

def skip_rows(df):
    df = df.iloc[1:]
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
def process_stock(df):

    df = (df 
            .pipe(remove_rows_with_totals)
            .pipe(replace_nan_with_partnumber)       
            .rename(columns = {'Είδος/PartNumber': 'partnumber',  # create dictionary to rename columns
                            'ΧΡΩΜΑ': 'color',
                                'ΜΕΓΕΘΟΣ': 'size', 
                            'Αποθ/Εισαγωγές': 'wh_imports', 
                            'Αποθ/Εξαγωγές': 'wh_exports', 
                            'Αποθ/Υπόλοιπο': 'wh_stock',
                            'ΕκκρΠαραγγ/Προμ.Ανεκτ.': 'outstanding_orders_supliers',
                            'ΕκκρΠαραγγ/Πελ.Ανεκτ.': 'outstanding_orders_customers',
                            'Προβλ.Υπολ.': 'projected_balance'})
            .fillna(0)
            .reset_index(drop=True) 
            )
    
    return df

