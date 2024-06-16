import streamlit as st




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

@st.cache_data
def process_stock(df):

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
            .reset_index(drop=True) 
            )
    
    return df

