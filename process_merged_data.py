import pandas as pd
from process_master_file_dna import left_join_dna, replace_null_with_other_string
from add_rows_for_stores_missing import add_rows_stores


def generate_full_df(df, df_master):
    
    # Define the list of columns to be converted to int
    columns_numeric = [
    'Επιστοφές', 'Πωλήσεις', 'Απόθεμα', 'wh_imports', 'wh_exports', 
    'wh_stock', 'outstanding_orders_supliers', 'outstanding_orders_customers', 
    'projected_balance']
    
    
    # Create a dictionary for astype conversion
    astype_dict = {col: int for col in columns_numeric}
    astype_dict['Υποκατάστημα'] = str

    df = (df
                .pipe(left_join_dna, df_master)
                .pipe(replace_null_with_other_string)
                .drop(columns=['PARTNUMBER', 'ΧΡΩΜΑΤΑ', 'ΜΕΓΕΘΗ'])
                .fillna(0)
                .astype(astype_dict)
                .query('Υποκατάστημα != "0"')
                )
    return df