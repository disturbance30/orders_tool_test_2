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

def process_sales(df):
        
        
        columns_to_keep = ['partnumber', 'color', 'size', 'Υποκατάστημα', 'Επιστοφές', 'Πωλήσεις', 'Απόθεμα']


        df = (df    
        .pipe(set_header)       
        .pipe(remove_rows_with_totals)
        .pipe(replace_nan_with_partnumber)
        .pipe(rename_columns)
        .loc[:, columns_to_keep]
        .fillna(0)
        .reset_index(drop=True) 
        )

        return df

