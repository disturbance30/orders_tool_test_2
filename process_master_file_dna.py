import pandas as pd
import numpy as np

def process_master_df(df: pd.DataFrame) -> pd.DataFrame:
    cols = ['PARTNUMBER', 'BASIC / FASHION', 'ΠΕΡΙΓΡΑΦΗ', 'ΚΑΤΗΓΟΡΙΑ', 'ΣΥΝΘΕΣΗ',  'ΧΡΩΜΑΤΑ', 'BRAND', 'ΣΕΖΟΝ','SEX', 'ΜΕΓΕΘΗ']
    return df[cols]


def left_join_dna(df: pd.DataFrame, dna: pd.DataFrame) -> pd.DataFrame:
    return df.merge(dna, 
                    left_on=['partnumber', 'color', 'size'], 
                    right_on=['PARTNUMBER', 'ΧΡΩΜΑΤΑ', 'ΜΕΓΕΘΗ'], 
                    how='left')


def replace_null_with_other_string(df: pd.DataFrame) -> pd.DataFrame:
    cols = ['PARTNUMBER', 'BASIC / FASHION', 'ΠΕΡΙΓΡΑΦΗ', 'ΚΑΤΗΓΟΡΙΑ', 'ΣΥΝΘΕΣΗ',  'ΧΡΩΜΑΤΑ', 'BRAND', 'ΣΕΖΟΝ','SEX', 'ΜΕΓΕΘΗ']
    df[cols] = df[cols].fillna('Άλλο')
    return df
