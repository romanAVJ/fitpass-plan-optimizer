import dash
from dash import dcc, html

app = dash.Dash(__name__)

# Your Dash app layout and callbacks go here

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)