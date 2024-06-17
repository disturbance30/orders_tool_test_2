 # Standard library imports 
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
from process_merged_data import generate_full_df
from prepare_data_gsheets import upload_data_gsheets

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
        st.write(':red[Λάθος στοιχεία σύνδεσης]')



if not st.session_state.login_auth:

    pw = get_render_pw()


    col1, col2, col3 = st.columns([1, 1, 1])


    with col2:
        st.image("logo_lora.png")
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
                        st.rerun()

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

            st.subheader("📂 Ανέβασε τα αρχεία σου")
            add_vertical_space(3)
            sales = st.file_uploader("Upload Sales", type=['xlsx', 'xls'])
            stock = st.file_uploader("Upload Stock", type=['xlsx', 'xls'])
            master = st.file_uploader("Upload Master", type=['xlsx', 'xls'])
            # master file
            add_vertical_space(5)
            get_data_button = st.button("Συνέχεια προηγούμενης δουλειάς 🔄", on_click=get_data, help="Κάντε κλικ για να πάρετε τα δεδομένα σας")

            if sales and stock and master:
                    
                with st.spinner('Φόρτωση και επεξεργασία δεδομένων...'):
                        
                    try:
                        # Read the uploaded files
                        df_sales = pd.read_excel(sales)
                        df_stock = pd.read_excel(stock)
                        df_master = pd.read_excel(master)

                        # Process the data
                        df_sales_processed = process_sales(df_sales)
                        df_stock_processed = process_stock(df_stock, df_sales_processed)
                        df_master = process_master_df(df_master)


                        # Merge sales and stock data
                        df_merged = merge_sales_stock(df_sales_processed, df_stock_processed)
                        
                        # Generate the full dataframe by merging with the master file, handling null values, converting to appropriate types
                        df_merged = generate_full_df(df_merged, df_master)
                    


                    
                        # prepare and upload data to Google Sheets
                        upload_data_gsheets(df_merged, spreadsheet)
                        



                        st.session_state.data_uploaded = True
                        
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
                        st.session_state.data_uploaded = False
                    


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
        fetched_data['ΣΥΝΟΛΟ'].fillna(50000, inplace=True)


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
                    'Πωλήσεις': 'sum',
                    'ΣΥΝΟΛΟ': 'first'})
                .reset_index()  
                .assign(SKU=lambda x: x['partnumber'].astype(str) + ' | ' +
                                    x['color'].astype(str) + ' | ' +
                                    x['size'].astype(str),
                        ΑΠΟΦΑΣΗ=lambda x: np.where(x['ΣΥΝΟΛΟ'] == 50000, 'Εκρεμμεί', 'Ολοκληρώθηκε'))
                .reindex(columns=['partnumber', 'color', 'size', 'BASIC / FASHION', 'ΠΕΡΙΓΡΑΦΗ', 
                                'ΣΥΝΘΕΣΗ', 'BRAND', 'SEX', 'SKU', 'Πωλήσεις', 'ΑΠΟΦΑΣΗ'])
                .astype({col: str for col in cols_to_covert_str})
                .astype({'Πωλήσεις': int})
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
                colm1.metric(label=":grey[Εισαγωγές]", value=filtered_df.iloc[0].loc['wh_imports'].astype(int))
                colm2.metric(label=":grey[Εξαγωγές]", value=filtered_df.iloc[0].loc['wh_exports'].astype(int))
                colm3.metric(label=":grey[Π. Προμηθευτές]", value=filtered_df.iloc[0].loc['outstanding_orders_supliers'].astype(int))
                colm4.metric(label=":grey[Π. Πελάτες]", value=filtered_df.iloc[0].loc['outstanding_orders_customers'].astype(int))
                colm5.metric(label=":grey[Υπόλοιπο]", value=filtered_df.iloc[0].loc['wh_stock'].astype(int))
                colm6.metric(label=":grey[Πρ. Υπόλοιπο]", value=filtered_df.iloc[0].loc['projected_balance'].astype(int))

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

            
                filtered_df_html = filtered_df.iloc[:, 3:7].drop_duplicates()
                # filtered_df_html = filtered_df_html.style.set_properties(**{'font-size': '14pt', 'font-family': 'Calibri'})

                filtered_df_html_2 = filtered_df_html.to_html(index=False )  #CREATE html TABLE FOR SALES DATA

                

                st.subheader(" 📊 Πωλήσεις")
                add_vertical_space(1)
                # AgGrid(filtered_df_html, height=150, width=50)
                st.markdown(filtered_df_html_2, unsafe_allow_html=True)
                add_vertical_space(1)
                st.write('Συνολικές πωλήσεις: ', filtered_df.iloc[:, 5].sum())
                sell_through = filtered_df.iloc[:, 5].sum() / (filtered_df.iloc[:, 5].sum() + filtered_df.iloc[:, 6].sum())
                sell_through = 0 if np.isnan(sell_through) else sell_through
                st.write(f'Sell through: :green[{sell_through * 100:.0f}%]')

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
                    replace = df['Πωλήσεις'].apply(lambda x: 0 if x < 0 else x)
                    antikatastasi_value = replace.sum() - df.iloc[0].loc['projected_balance']
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

                
            def create_form():
                inputs = {}
                for magazi in filtered_df['Υποκατάστημα'].unique():
                    magazi_sales = filtered_df.query(f'Υποκατάστημα == "{magazi}"').Πωλήσεις.sum()
                    magazi_sales = 0 if magazi_sales < 0 else magazi_sales
                    inputs[magazi] = st.number_input(f'{magazi}', min_value=0, max_value=1000, value=magazi_sales)
                return inputs
            


            def send_data_to_google_sheets_decisions():
                    
                    final_value_for_sinolo = (sum(list(magazi_values.values())) + apothiki) - filtered_df.iloc[0, 12].astype(int)
                    final_value_for_sinolo = 0 if final_value_for_sinolo < 0 else final_value_for_sinolo
                    final_value_for_sinolo = int(final_value_for_sinolo)
                    data_to_upload_decisions =  [current_combo["partnumber"], current_combo["color"], current_combo["size"]]
                    data_to_upload_decisions.extend(list(magazi_values.values()))
                    data_to_upload_decisions.append(apothiki)
                    data_to_upload_decisions.append(final_value_for_sinolo)
                    body=data_to_upload_decisions 
                    worksheet_decisions = spreadsheet.worksheet("Sheet2")
                    worksheet_decisions.append_row(body) 
            
            cols = st.columns(2)

            with cols[0]:
                with st.popover("Ανα κατάστημα", use_container_width=True, help = ' 🏬 Εισάγετε παραγγελίες ανά κατάστημα'):
                    tab1, tab2, tab3= st.tabs(["Αντικατάσταση", "Επιθετική 30%", 'Επιθετική 50%'])
                    replace = filtered_df['Πωλήσεις'].apply(lambda x: 0 if x < 0 else x)

                    with tab1:
                        with st.form(key='my_form', border=False):
                            magazi_values = create_form()
                            apothiki = st.number_input('ΑΠΟΘΗΚΗ', min_value=0, max_value=1000, value= 0) 
                            add_vertical_space(1)
                            submit_button_1 = st.form_submit_button(label='✅ Αποδοχή')

                            if submit_button_1:
                                with st.spinner('Αποθήκευση...'):
                                    try:
                                        # Call the function to send data to Google Sheets
                                        send_data_to_google_sheets_decisions()
                                        # Once the function completes, show the success message
                                        st.success("Η επιλογή σας αποθηκεύτηκε επιτυχώς!")
                                    except Exception as e:
                                        st.error(f"An error occurred: {e}")


                    with tab2:
                        with st.form(key='my_form1', border=False):
                            magazi_values = create_form()
                            apothiki = st.number_input('ΑΠΟΘΗΚΗ', min_value=0, max_value=1000, value= (int(epithetiki_1) - int(antikatastasi)))
                            add_vertical_space(1)
                            submit_button_2 = st.form_submit_button(label='✅ Αποδοχή')

                            if submit_button_2:
                                with st.spinner('Αποθήκευση...'):
                                    try:
                                        # Call the function to send data to Google Sheets
                                        send_data_to_google_sheets_decisions()
                                        # Once the function completes, show the success message
                                        st.success("Η επιλογή σας αποθηκεύτηκε επιτυχώς!")
                                    except Exception as e:
                                        st.error(f"An error occurred: {e}")

                    with tab3:
                        with st.form(key='my_form2', border=False):
                            magazi_values= create_form()
                            apothiki = st.number_input('ΑΠΟΘΗΚΗ', min_value=0, max_value=1000, value= (int(epithetiki_2) - int(antikatastasi)))
                            add_vertical_space(1)
                            submit_button_3 = st.form_submit_button(label='✅ Αποδοχή')
                            
                            if submit_button_3:
                                with st.spinner('Αποθήκευση...'):
                                    try:
                                        # Call the function to send data to Google Sheets
                                        send_data_to_google_sheets_decisions()
                                        # Once the function completes, show the success message
                                        st.success("Η επιλογή σας αποθηκεύτηκε επιτυχώς!")
                                    except Exception as e:
                                        st.error(f"An error occurred: {e}")


            with cols[1]:
                with st.popover("Συνολική Παραγγελία", use_container_width=True, help = ' 🛒 Εισάγετε την συνολική παραγγελία'):
                    with st.form(key='custom_order', border=False):
                        custom_order = st.number_input('Ποσότητα', min_value=0, max_value=10000, value=0)
                        add_vertical_space(1)
                        submit_button_custom_total_order = st.form_submit_button(label='✅ Αποδοχή')

                        if submit_button_custom_total_order:
                            with st.spinner('Αποθήκευση...'):
                                try:
                                    data_to_upload_decisions =  [current_combo["partnumber"], current_combo["color"], current_combo["size"], 'ελειπές', 'ελειπές', 'ελειπές', 'ελειπές', 'ελειπές', 'ελειπές', custom_order]
                                    body_for_custom_order=data_to_upload_decisions
                                    worksheet_decisions = spreadsheet.worksheet("Sheet2")
                                    worksheet_decisions.append_row(body_for_custom_order)
                                    st.success("Η επιλογή σας αποθηκεύτηκε επιτυχώς!")
                                except Exception as e:
                                    st.error(f"An error occurred: {e}")


                col1, col2, col3, col4 = col_wh3.columns([1, 1, 8, 1])
                with col4:
                    button_episkopisi = st.button('🔎', help = ' :green[Επισκόπηση αποφάσεων]')
                    # refresh_button = st.button('🔄')
                    # if refresh_button:
                    #     sheet2_data = spreadsheet.worksheet("Sheet2").get_all_records()
                    #     decisions_data = pd.DataFrame(sheet2_data)
                    #     fetched_data = pd.merge(fetched_data, decisions_data[['partnumber', 'color', 'size', 'ΣΥΝΟΛΟ']], on=['partnumber', 'color', 'size'], how='left')
                    #     fetched_data['ΣΥΝΟΛΟ'].fillna(50000, inplace=True)

            if button_episkopisi:
                worksheet_decisions_to_download = spreadsheet.worksheet("Sheet2").get_all_records()
                df_decisions = pd.DataFrame(worksheet_decisions_to_download).iloc[1:]
                st.subheader(f'{len(df_decisions)} αποφάσεις')
                st.dataframe(df_decisions, hide_index=True)







 