import dash
from dash import html, Input, Output, ctx
import os, requests
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Button('Click to Update', id='button1', n_clicks=0),
    html.Table([
        html.Tr([html.Td(['Column Name on the NFM4 Allocation Letter DB']),
                html.Td(['Filling Percentage (%)'])]),
        html.Tr([html.Td(['CoFinancing Minimum Marginal Commitment - HIV']),
                 html.Td(id='hiv')]),
        html.Tr([html.Td(['CoFinancing Minimum Marginal Commitment - TB']),
                 html.Td(id='tb')]),
        html.Tr([html.Td(['CoFinancing Minimum Marginal Commitment - Malaria']),
                 html.Td(id='malaria')]),
        html.Tr([html.Td(['CoFinancing Minimum Marginal Commitment - RSSH']),
                 html.Td(id='rssh')]),
        html.Tr([html.Td(['Suggested Text']), html.Td(id='text')]),
    ]),
])


# app.layout = html.Div([
#     html.Button('Click to Update', id='button1', n_clicks=0),
#     dash_table.DataTable(
#         data=output.to_dict('records'),
#         columns=[{'id': c, 'name': c} for c in df.columns],
#         style_cell={'textAlign': 'left'},
#         style_cell_conditional=[
#             {
#                 'if': {'column_id': 'Region'},
#                 'textAlign': 'left'
#             }
# ])


def update_table():
    API_KEY = os.environ.get("AIRTABLE_KEY")
    ROOT = "https://api.airtable.com/v0/"
    DATABASE_id = "appRJdyaNf9o4l0rT"
    TABLE1_ID = "tbltjA4y12LbREnit"
    TABLE_NAME = "/Table 1"
    URL = ROOT + DATABASE_id + TABLE_NAME
    headers = {"Authorization": "Bearer " + API_KEY}
    params = ()
    airtable_records = []
    # this block reads the data from AirTable
    run = True
    while run is True:
        response = requests.get(URL, params=params, headers=headers)
        airtable_response = response.json()
        airtable_records += (airtable_response["records"])
        if "offset" in airtable_response:
            run = True
            params = (("offset", airtable_response["offset"]),)
        else:
            run = False
    # This block creates the dataframe from the Airtable table
    airtable_rows = []
    airtable_index = []
    for record in airtable_records:
        airtable_rows.append(record["fields"])
        airtable_index.append(record["id"])
    airtable_df = pd.DataFrame(airtable_rows, index=airtable_index)
    airtable_df = airtable_df[
        airtable_df['ISO3'].notna()]  # removes NaN in ISO3
                                      # column
    # sorts the dataframe by Country name
    extract_df = airtable_df.sort_values(by=['Country'])
    num_rows = extract_df.shape[0]
    HIV_na = extract_df["CoFinancing Minimum Marginal Commitment - HIV"].isna() \
             .sum()
    TB_na = extract_df["CoFinancing Minimum Marginal Commitment - TB"].isna() \
            .sum()
    Malaria_na = extract_df["CoFinancing Minimum Marginal Commitment - Malaria"] \
                 .isna().sum()
    RSSH_na = extract_df["CoFinancing Minimum Marginal Commitment - RSSH"] \
              .isna().sum()
    Test_na = extract_df["Suggested Text"].isna().sum()
    Test_newline = extract_df.loc[extract_df["Suggested Text"] == "\n",
                                  "Suggested Text"].count()
    HIV_filled_perc = (num_rows - HIV_na) / num_rows * 100
    TB_filled_perc = (num_rows - TB_na) / num_rows * 100
    Malaria_filled_perc = (num_rows - Malaria_na) / num_rows * 100
    RSSH_filled_perc = (num_rows - RSSH_na) / num_rows * 100
    Test_filled_perc = (num_rows - Test_na - Test_newline) / num_rows * 100
    out1 = f"{HIV_filled_perc:.1f}%"
    out2 = f"{TB_filled_perc:.1f}%"
    out3 = f"{Malaria_filled_perc:.1f}%"
    out4 = f"{RSSH_filled_perc:.1f}%"
    out5 = f"{Test_filled_perc:.1f}%"
    return out1, out2, out3, out4, out5

@app.callback(
    Output('hiv', 'children'),
    Output('tb', 'children'),
    Output('malaria', 'children'),
    Output('rssh', 'children'),
    Output('text', 'children'),
    Input('button1', 'n_clicks'))
def callback_a(btn1):
    if "btn" == None:
        raise PreventUpdate
    else:#== ctx.triggered_id:
        out1, out2, out3, out4, out5 = update_table()
        return out1, out2, out3, out4, out5


if __name__ == '__main__':
    app.run_server(debug=True)