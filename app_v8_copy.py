# Standard library imports
from io import BytesIO  
import os

# Third-party imports
import gspread  # Google Sheets API
from oauth2client.service_account import ServiceAccountCredentials  # Authentication for Google API
import pandas as pd 
import numpy as np  
import streamlit as st 

# Local imports
from process_sales_data import process_sales 
from process_stock_data import process_stock  
from process_master_file_dna import process_master_df, left_join_dna, replace_null_with_other_string
from merge_dataframes import merge_sales_stock  
from add_rows_for_stores_missing import add_rows_stores 

# Streamlit extras for enhanced UI components
from streamlit_extras.add_vertical_space import add_vertical_space  
from streamlit_extras.metric_cards import style_metric_cards 
from streamlit_extras.stylable_container import stylable_container

# streamlit dynamic filters (custom class)
from dynamic_filters_copy import DynamicFilters_custom




# configure streamlit page
st.set_page_config(layout="wide", page_title="Orders Tool", page_icon="🛒")



if 'row_index' not in st.session_state:
    st.session_state.row_index = 0

if 'login_auth' not in st.session_state:
    st.session_state.login_auth = False

@st.cache_data(show_spinner=False)
def get_render_pw():
    render_pw = os.getenv('form_pw')
    return render_pw

def logged_in_success():
    if username == 'American' and kodikos == pw:
        st.session_state.login_auth = True
    else:
        st.session_state.login_auth = False



if not st.session_state.login_auth:

    pw = get_render_pw()


    col1, col2, col3 = st.columns([1, 1, 1])


    with col2:
        st.image("logo.png")
        add_vertical_space(2)
        loggin_container =  stylable_container(
                            key="container_with_border",
                            css_styles="""{background-color: #FFFFFF;; border: 1px solid rgba(49, 51, 63, 0.2);border-radius: 0.5rem; padding: calc(1em - 1px)}""",
                            )
        with loggin_container:
            


            with st.form(key='my_form', border=False):
                username = st.text_input('Username')
                kodikos = st.text_input('Password', type='password')
                add_vertical_space(1)
                submit_button_1 = st.form_submit_button('Log in')
                if submit_button_1:
                    logged_in_success()
                    if st.session_state.login_auth:
                        st.experimental_rerun()

if st.session_state.login_auth:


    ###########
    # Google Sheets connection
    ###########
    ###########
    ###########
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]


    # Function to get the path to the JSON 
    st.cache_data(show_spinner=False)
    def get_render_fle():
        render_file = "/etc/secrets/service_access" 
        return render_file


    render_file = get_render_fle() 
    creds = ServiceAccountCredentials.from_json_keyfile_name(render_file, scope)

    # Function to authorize and get the client, cached to avoid re-authorizing unnecessarily
    @st.cache_resource(show_spinner=False)
    def authorize_gsheets():
        return gspread.authorize(creds)

    client = authorize_gsheets()

    # Access the spreadsheet
    @st.cache_resource(show_spinner=False)
    def get_access_to_spreadsheet():
        return client.open("streamlit")

    spreadsheet = get_access_to_spreadsheet()

    # Function to fetch data from a Google sheet, given the sheet name
    @st.cache_resource(show_spinner=False)
    def get_data_from_google_sheets(sheet_name: str):
        return spreadsheet.worksheet(sheet_name).get_all_records()
    ###########
    ###########
    ###########
    ###########





    # initialize session state variables
    if 'get_data_clicked' not in st.session_state:
        st.session_state['get_data_clicked'] = False
    if 'data_uploaded' not in st.session_state:
        st.session_state['data_uploaded'] = False

    def get_data():
        st.session_state.get_data_clicked = True






    ###########
    #UPLOAD FILES OR FETCH DATA USING GET DATA BUTTON
    ###########
    ###########
    # UI for uploading files and fetching data
    if not st.session_state.get_data_clicked and not st.session_state.data_uploaded:
        sales = st.file_uploader("Upload Sales", type=['xlsx', 'xls'])
        stock = st.file_uploader("Upload Stock", type=['xlsx', 'xls'])
        master = st.file_uploader("Upload Master", type=['xlsx', 'xls'])
        # master file
        get_data_button = st.button("Get Data", on_click=get_data)

        if sales and stock and master:
                
                df_sales = pd.read_excel(sales, skiprows=3)
                df_stock = pd.read_excel(stock, skiprows=1)
                df_master = pd.read_excel(master)

                df_salesp = process_sales(df_sales)
                df_stock_pr = process_stock(df_stock)
                df_master = process_master_df(df_master)



                df_merged = merge_sales_stock(df_salesp, df_stock_pr)

                df_merged = (df_merged
                            .pipe(add_rows_stores)
                            .replace([np.inf, -np.inf], np.nan)
                            .pipe(left_join_dna, df_master)
                            .pipe(replace_null_with_other_string)
                            .drop(columns=['PARTNUMBER', 'ΧΡΩΜΑΤΑ', 'ΜΕΓΕΘΗ'])
                            .fillna(0)
                            .astype({'store': str})
                            .query('store != "0"')
                            )

                
                # Prepare data for upload
                data_to_upload = [df_merged.columns.values.tolist()] + df_merged.values.tolist()
                # Upload data
                worksheet = spreadsheet.worksheet("Sheet1")
                worksheet.update('A1', data_to_upload)
                spreadsheet.worksheet("Sheet2").clear()
                headers_for_sheet2 = ['partnumber', 'color', 'size', 'AM.VINTAGE', 'ATTICA', 'GOLDEN', 'ΓΛΥΦΑΔΑΣ', 'ΨΥΧΙΚΟΥ', 'ΑΠΟΘΗΚΗ', 'ΣΥΝΟΛΟ']
                values_for_sheet2 = [['Test, not for use', 'Red', 'L', 10, 20, 30, 40, 50, 60, 70]]
                data_to_upload_in_sheet2 = [headers_for_sheet2] + values_for_sheet2
                worksheet_decisions = spreadsheet.worksheet("Sheet2")
                worksheet_decisions.update('A1' ,data_to_upload_in_sheet2)


                st.session_state.data_uploaded = True

    ###########
    ###########
    ###########









    ###########
    #MAIN APP
    ###########
    ###########

    if st.session_state.get_data_clicked or st.session_state.data_uploaded:
        sheet1_data = get_data_from_google_sheets('Sheet1')
        sheet2_data = get_data_from_google_sheets('Sheet2')
        fetched_data = pd.DataFrame(sheet1_data)
        decisions_data = pd.DataFrame(sheet2_data)
        fetched_data = pd.merge(fetched_data, decisions_data[['partnumber', 'color', 'size', 'ΣΥΝΟΛΟ']], on=['partnumber', 'color', 'size'], how='left')
        fetched_data.fillna(50000, inplace=True)


        # Get unique combinations of partnumber, color, and size

        # @st.cache_data(show_spinner=False)
        # def get_unique_combos(df: pd.DataFrame) -> pd.DataFrame:
        #     df = (df[['partnumber', 'color', 'size']]
        #                 .drop_duplicates()
        #                 .reset_index(drop=True))
        #     return df

        @st.cache_data(show_spinner=False)
        def get_unique_combos(df):

            cols_to_covert_str = ['partnumber', 'color', 'size', 'BASIC / FASHION', 'ΠΕΡΙΓΡΑΦΗ', 'ΣΥΝΘΕΣΗ', 'BRAND', 'SEX', 'SKU']
            
            df = (
                df
                .groupby(['partnumber', 'color', 'size'])
                .agg({'BASIC / FASHION': 'first', 
                    'ΠΕΡΙΓΡΑΦΗ': 'first', 
                    'ΣΥΝΘΕΣΗ': 'first', 
                    'BRAND': 'first', 
                    'SEX': 'first',
                    'store_sales': 'sum'})
                .reset_index()  
                .assign(SKU=lambda x: x['partnumber'].astype(str) + ' | ' +
                                    x['color'].astype(str) + ' | ' +
                                    x['size'].astype(str))
                .reindex(columns=['partnumber', 'color', 'size', 'BASIC / FASHION', 'ΠΕΡΙΓΡΑΦΗ', 
                                'ΣΥΝΘΕΣΗ', 'BRAND', 'SEX', 'SKU', 'store_sales'])
                .astype({col: str for col in cols_to_covert_str})
                .astype({'store_sales': int})
            )

            return df

        




        
        
        unique_combos = get_unique_combos(fetched_data)


    # FILTERS
    #######
    ########


        if 'prev_df_len' not in st.session_state:  # this will be used to check if a new filter has made any difference in our df
            st.session_state.prev_df_len = len(unique_combos)


        st.sidebar.subheader('⚙️ ΦΙΛΤΡΑ')

        dynamic_filters = DynamicFilters_custom(unique_combos, filters=unique_combos.columns.tolist())

        with st.sidebar:
            add_vertical_space(1)

        dynamic_filters.display_filters()

        unique_combos = dynamic_filters.get_filtered_df() #update  df based on the filters



        if len(unique_combos) != st.session_state.prev_df_len:
            st.session_state.prev_df_len = len(unique_combos)
            st.session_state.row_index = 0

    #######
    ########

        











    # Title of sku, and previous and next buttons to navigate SKU combinations
    ###########
    ###########
        
        col1, col2 = st.columns([1, 1])

        # col2a, col2b, col2c, col2d = col2.columns([1, 1, 1, 2])

        cols = col2.columns(6)

        #previous button    
        with cols[3]:
            add_vertical_space(1)
            if st.button(':arrow_backward:'):
                st.session_state.row_index -= 1
                if st.session_state.row_index < 0:
                    st.session_state.row_index = len(unique_combos) - 1

        #pagination
        with cols[5]:
            add_vertical_space(1)
            if st.button(':arrow_forward:'):
                st.session_state.row_index += 1
                if st.session_state.row_index == len(unique_combos):
                    st.session_state.row_index = 0


        #next button
        with cols[4]:
            add_vertical_space(2)
            st.write(f"{st.session_state.row_index + 1} από {len(unique_combos)}")



        #set dynamic SKU title to display the current SKU combination
        with col1:
            current_combo = unique_combos.iloc[st.session_state.row_index]

            filtered_df = fetched_data[(fetched_data['partnumber'] == current_combo['partnumber']) &
                (fetched_data['color'] == current_combo['color']) &
                (fetched_data['size'] == current_combo['size'])]
            
            
            st.title(f'{current_combo["partnumber"]} :grey[|] {current_combo["color"]} :grey[|] {current_combo["size"]}')

            decision_info = ':red[Εκρεμμεί απόφαση για παραγγελία]' if filtered_df.iloc[0]['ΣΥΝΟΛΟ'] == 50000 else f':green[Έχετε πάρει απόφαση για παραγγελία:  ]   {int(filtered_df.iloc[0]["ΣΥΝΟΛΟ"])} '
            st.write(decision_info)


    ###########
    ###########
        











    # ΑΠΟΘΗΚΗ ΣΤΑΤΙΣΤΙΚΑ
    ###########
    ###########     

        #CUSTOMIZE THE APPEARANCE OF THE METRIC CARDS
        style_metric_cards(border_left_color ='lightgrey', border_size_px=0.2, box_shadow=False)
        add_vertical_space(2)

        col_wh1, col_wh2, col_wh3 = st.columns([0.6, 0.03, 0.8])

        with col_wh1:

            # create custom conainer box UI
            container_apothiki =  stylable_container(
                                        key="container_with_border",
                                        css_styles="""{background-color: #FFFFFF;; border: 1px solid rgba(49, 51, 63, 0.2);border-radius: 0.5rem; padding: calc(1em - 1px)}""",
                                        )


            #PRESENT WAREHOUSE METRICS WITHIN THE CONTAINER BOX
            with container_apothiki:

                st.subheader(" 📦 Αποθήκη ")
                add_vertical_space(1)
                colm1, colm2, colm3, colm4, colm5, colm6 = st.columns(6)
                colm1.metric(label=":grey[Εισαγωγές]", value=filtered_df.iloc[:, 7].mean().astype(int))
                colm2.metric(label=":grey[Εξαγωγές]", value=filtered_df.iloc[:, 8].mean().astype(int))
                colm3.metric(label=":grey[Π. Προμηθευτές]", value=filtered_df.iloc[:, 10].mean().astype(int))
                colm4.metric(label=":grey[Π. Πελάτες]", value=filtered_df.iloc[:, 11].mean().astype(int))
                colm5.metric(label=":grey[Υπόλοιπο]", value=filtered_df.iloc[:, 9].mean().astype(int))
                colm6.metric(label=":grey[Πρ. Υπόλοιπο]", value=filtered_df.iloc[:, 12].mean().astype(int))

                add_vertical_space(2)
    ###########
    ########### 





    # ΠΩΛΗΣΕΙΣ 
    ###########
    ########### 
            container_poliseis =  stylable_container(
                                        key="container_with_border",
                                        css_styles="""{background-color: #FFFFFF;; border: 1px solid rgba(49, 51, 63, 0.2);border-radius: 0.5rem; padding: calc(1em - 1px)}""",
                                        )

            with container_poliseis:

            
                filtered_df_html = filtered_df.iloc[:, 3:7]
                # filtered_df_html = filtered_df_html.style.set_properties(**{'font-size': '14pt', 'font-family': 'Calibri'})

                filtered_df_html_2 = filtered_df_html.to_html(index=False )  #CREATE html TABLE FOR SALES DATA

                

                st.subheader(" 📊 Πωλήσεις")
                # AgGrid(filtered_df_html, height=150, width=50)
                st.markdown(filtered_df_html_2, unsafe_allow_html=True)
                add_vertical_space(2)
    ###########
    ########### 
                            




    # ΠΡΟΤΑΣΕΙΣ ΠΑΡΑΓΓΕΛΙΑΣ 
    ###########
    ###########

        with col_wh3:

            container_protaseis =  stylable_container(key="container_with_border",
                                                    css_styles="""{background-color: #FFFFFF;; border: 1px solid rgba(49, 51, 63, 0.2);border-radius: 0.5rem; padding: calc(1em - 1px)}""",)

            with container_protaseis:

                st.subheader(' ⭐ Προτάσεις για παραγγελία')

                add_vertical_space(1)
                cols3a, cols3b, cols3c = st.columns(3)

                #funtion for replacement suggestion
                def calculate_replacement(df: pd.DataFrame) -> float:
                    replace = df['store_sales'].apply(lambda x: 0 if x < 0 else x)
                    antikatastasi_value = replace.sum() - df['projected_balance'].mean()
                    antikatastasi_value = 0 if antikatastasi_value < 0 else antikatastasi_value

                    return antikatastasi_value

                antikatastasi = calculate_replacement(filtered_df)

                #function for rounding the replacement value (>= 0.5 then round up)
                def custom_round(value: float) -> int:
                    integer_part = int(value)
                    fractional_part = round(value, 2) - integer_part
                    if fractional_part >= 0.5:
                        return integer_part + 1
                    else:
                        return integer_part
                    
                # create variables for epithetikes protaseis
                epithetiki_1 = custom_round(antikatastasi * 1.30)
                epithetiki_2 = custom_round(antikatastasi * 1.50)

                cols3a.metric(label="Αντικατάσταση", value=int(antikatastasi), delta='0%')
                cols3b.metric(label="Επιθετική 1", value=epithetiki_1, delta = '30%')
                cols3c.metric(label="Επιθετική 2", value=epithetiki_2, delta = '50%')


                #function to create the form for the user to input the quantity
                def create_form():
                        magazi1 = st.number_input('AM.VINTAGE', min_value=0, max_value=1000, value=replace.iloc[0])
                        magazi2 = st.number_input('ATTICA', min_value=0, max_value=1000, value=replace.iloc[1])
                        magazi3 = st.number_input('GOLDEN', min_value=0, max_value=1000, value=replace.iloc[2])
                        magazi4 = st.number_input('ΓΛΥΦΑΔΑΣ', min_value=0, max_value=1000, value=replace.iloc[3])
                        magazi5 = st.number_input('ΨΥΧΙΚΟΥ', min_value=0, max_value=1000, value=replace.iloc[4])

                        return magazi1, magazi2, magazi3, magazi4, magazi5
                
                #function to send form data to google sheets
                def send_data_to_google_sheets_decisions(magazi1, magazi2, magazi3, magazi4, magazi5, apothiki):
                        
                        final_value_for_sinolo = (sum([magazi1, magazi2, magazi3, magazi4, magazi5, apothiki]) - filtered_df.iloc[:, 12].mean().astype(int))
                        final_value_for_sinolo = 0 if final_value_for_sinolo < 0 else final_value_for_sinolo
                        final_value_for_sinolo = int(final_value_for_sinolo)
                        data_to_upload_decisions =  [current_combo["partnumber"], current_combo["color"], current_combo["size"], magazi1, magazi2, magazi3, magazi4, magazi5, apothiki, final_value_for_sinolo]
                        body=data_to_upload_decisions #the values should be a list
                        worksheet_decisions = spreadsheet.worksheet("Sheet2")
                        worksheet_decisions.append_row(body) 

                with st.expander("Ανα κατάστημα"):
                    tab1, tab2, tab3= st.tabs(["Αντικατάσταση", "Επιθετική 30%", 'Επιθετική 50%'])
                    replace = filtered_df['store_sales'].apply(lambda x: 0 if x < 0 else x)

                    with tab1:
                        with st.form(key='my_form', border=False):
                            magazi_values = create_form()
                            apothiki = st.number_input('ΑΠΟΘΗΚΗ', min_value=0, max_value=1000, value= 0) 
                            submit_button_1 = st.form_submit_button(label='Αποδοχή')

                            if submit_button_1:
                                send_data_to_google_sheets_decisions(*magazi_values, apothiki)


                    with tab2:
                        with st.form(key='my_form1', border=False):
                            magazi_values = create_form()
                            apothiki = st.number_input('ΑΠΟΘΗΚΗ', min_value=0, max_value=1000, value= (int(epithetiki_1) - int(antikatastasi)))
                            submit_button_2 = st.form_submit_button(label='Αποδοχή')

                            if submit_button_2:
                                send_data_to_google_sheets_decisions(*magazi_values, apothiki)

                    with tab3:
                        with st.form(key='my_form2', border=False):
                            magazi_values= create_form()
                            apothiki = st.number_input('ΑΠΟΘΗΚΗ', min_value=0, max_value=1000, value= (int(epithetiki_2) - int(antikatastasi)))
                            submit_button_3 = st.form_submit_button(label='Αποδοχή')
                            
                            if submit_button_3:
                                send_data_to_google_sheets_decisions(*magazi_values, apothiki)



                with st.expander("Συνολική Παραγγελία"):
                    with st.form(key='custom_order', border=False):
                        custom_order = st.number_input('Ποσότητα', min_value=0, max_value=10000, value=0)
                        submit_button_custom_total_order = st.form_submit_button(label='Αποδοχή')
                        if submit_button_custom_total_order:
                            data_to_upload_decisions =  [current_combo["partnumber"], current_combo["color"], current_combo["size"], 'ελειπές', 'ελειπές', 'ελειπές', 'ελειπές', 'ελειπές', 'ελειπές', custom_order]
                            body_for_custom_order=data_to_upload_decisions
                            worksheet_decisions = spreadsheet.worksheet("Sheet2")
                            worksheet_decisions.append_row(body_for_custom_order)

            col1, col2, col3, col4 = col_wh3.columns([1, 1, 1, 1])
            with col4:
                add_vertical_space(2)
                download_button = st.button('Excel αποφάσεις')

                if download_button:
                    worksheet_decisions_to_download = spreadsheet.worksheet("Sheet2").get_all_records()
                    df_decisions = pd.DataFrame(worksheet_decisions_to_download).iloc[1:]

                    # Convert DataFrame to Excel in memory
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df_decisions.to_excel(writer, sheet_name='Sheet1', index=False)
                        writer.save()
                        excel_data = output.getvalue()

                    # Create a download button for the Excel file
                    st.download_button(
                        label="🔽 Λήψη αρχείου",
                        data=excel_data,
                        file_name="decisions.xlsx",
                        mime="application/vnd.ms-excel"
                    )

                
                add_vertical_space(1)
                episkopisi = st.button('Επικόπηση')
                
                if episkopisi:
                    col1, col2, col3 = col_wh3.columns([1, 1, 3])
                    with col3:

                        worksheet_decisions_to_download = spreadsheet.worksheet("Sheet2").get_all_records()
                        df_decisions = pd.DataFrame(worksheet_decisions_to_download).iloc[1:, [0, 1, 2, -1]]
                        st.markdown(f' 🔎 {len(df_decisions)} αποφάσεις')
                        st.dataframe(df_decisions)


