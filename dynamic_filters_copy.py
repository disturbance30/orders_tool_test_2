import streamlit as st
import pandas as pd

class DynamicFilters_custom:
    def __init__(self, df, filters):
        self.df = df
        self.filters = {filter_name: [] if not pd.api.types.is_numeric_dtype(df[filter_name]) else (df[filter_name].min(), df[filter_name].max()) for filter_name in filters}
        self.check_state()

    def check_state(self):
        if 'filters' not in st.session_state:
            st.session_state.filters = self.filters

    def filter_except(self, except_filter=None):
        filtered_df = self.df.copy()
        for key, values in st.session_state.filters.items():
            if key != except_filter and values:
                if pd.api.types.is_numeric_dtype(self.df[key]):
                    filtered_df = filtered_df[(filtered_df[key] >= values[0]) & (filtered_df[key] <= values[1])]
                else:
                    filtered_df = filtered_df[filtered_df[key].isin(values)]
        return filtered_df

    def display_filters(self):
        filters_changed = False
        for filter_name in st.session_state.filters.keys():
            filtered_df = self.filter_except(filter_name)
            options = filtered_df[filter_name].unique().tolist()

            if pd.api.types.is_numeric_dtype(self.df[filter_name]):
                min_val = int(filtered_df[filter_name].min())
                max_val = int(filtered_df[filter_name].max())
                selected_range = st.sidebar.slider(f"{filter_name}", min_val, max_val, st.session_state.filters[filter_name])
                selected = (selected_range[0], selected_range[1])
            else:
                selected = st.sidebar.multiselect(f"{filter_name}", options, default=st.session_state.filters[filter_name])

            if selected != st.session_state.filters[filter_name]:
                st.session_state.filters[filter_name] = selected
                filters_changed = True

        if filters_changed:
            st.experimental_rerun()

    def display_df(self):
        st.dataframe(self.filter_except())

    def get_filtered_df(self):
        return self.filter_except()

