import streamlit as st

@st.cache_data(show_spinner=False)
def add_rows_stores(df):
    import pandas as pd

    # List of unique stores required for each combination
    required_stores = df['Υποκατάστημα'].dropna().unique()
    required_stores_df = pd.DataFrame(required_stores, columns=['Υποκατάστημα'])

    # Identifying all unique combinations of partnumber, color, size
    unique_combos = df[['partnumber', 'color', 'size']].drop_duplicates()

    # Creating a Cartesian product of unique combinations and required stores
    combo_stores_df = unique_combos.assign(key=1).merge(required_stores_df.assign(key=1), on='key').drop('key', axis=1)

    # Merging this with the original dataframe to find the missing rows
    merged_df = combo_stores_df.merge(df, on=['partnumber', 'color', 'size', 'Υποκατάστημα'], how='left')

    # Filling missing values in 'Επιστοφές', 'Πωλήσεις', and 'Απόθεμα' columns
    merged_df['Επιστοφές'].fillna(0, inplace=True)
    merged_df['Πωλήσεις'].fillna(0, inplace=True)
    merged_df['Απόθεμα'].fillna(0, inplace=True)

    # Sorting and resetting index
    df = merged_df.sort_values(by=['partnumber', 'color', 'size', 'Υποκατάστημα']).reset_index(drop=True)

    return df
