import streamlit as st

@st.cache_data(show_spinner=False)
def add_rows_stores(df):
        # List of unique stores required for each combination
    import pandas as pd
    required_stores = ['AM.VINTAGE', 'ATTICA', 'GOLDEN', 'ΓΛΥΦΑΔΑΣ', 'ΨΥΧΙΚΟΥ']

    # Identifying all unique combinations of partnumber, color, size
    unique_combos = df[['partnumber', 'color', 'size']].drop_duplicates()

    # Placeholder DataFrame to collect results
    new_rows = []

    # Iterate over each unique combination
    for _, combo in unique_combos.iterrows():
        # Filter df for rows matching the current combination
        subset = df[(df['partnumber'] == combo['partnumber']) & (df['color'] == combo['color']) & (df['size'] == combo['size'])]
        # Check if all required stores are present
        present_stores = subset['store'].unique()
        missing_stores = set(required_stores) - set(present_stores)
        # If missing, use values from the existing rows of the same combo
        if missing_stores:
            template_row = subset.iloc[0]
        # Append missing rows
        for store in missing_stores:
            new_row = template_row.copy()
            new_row.update({
                'store': store,
                'returns': 0,
                'store_sales': 0,
                'store_stock': 0,
            })
            new_rows.append(new_row)

    # Convert list of dicts to DataFrame and append to original df
    missing_df = pd.DataFrame(new_rows)
    df = pd.concat([df, missing_df], ignore_index=True).sort_values(by=['partnumber', 'color', 'size', 'store']).reset_index(drop=True).fillna(0)


    return df