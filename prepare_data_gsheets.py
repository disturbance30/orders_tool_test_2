def upload_data_gsheets(df, spreadsheet_name):

    # Prepare data for upload
    data_to_upload = [df.columns.values.tolist()] + df.values.tolist()
    # Upload data
    worksheet = spreadsheet_name.worksheet("Sheet1")
    worksheet.update('A1', data_to_upload)
    spreadsheet_name.worksheet("Sheet2").clear()
    unique_stores = df['Υποκατάστημα'].dropna().unique().tolist()
    headers_for_sheet2 = ['partnumber', 'color', 'size']
    headers_for_sheet2.extend(unique_stores)
    headers_for_sheet2.append('ΑΠΟΘΗΚΗ')
    headers_for_sheet2.append('ΣΥΝΟΛΟ')
    str_lst = ['test', 'test', 'test']
    lst_template = [i for i in range(len(unique_stores) + 2)]
    str_lst.extend(lst_template)
    values_for_sheet2 = [str_lst]
    data_to_upload_in_sheet2 = [headers_for_sheet2] + values_for_sheet2
    worksheet_decisions = spreadsheet_name.worksheet("Sheet2")
    worksheet_decisions.update('A1' ,data_to_upload_in_sheet2)