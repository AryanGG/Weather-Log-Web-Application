from flask import Flask, render_template, request, redirect
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import os

app = Flask(__name__)
df = pd.read_csv('weather_log.csv')
# Load or create weather dataset
CSV_FILE = 'weather_log.csv'

def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        # Create empty DataFrame if CSV does not exist
        df = pd.DataFrame(columns=["Date", "Temperature", "Humidity", "WindSpeed", "WeatherCondition"])
        df.to_csv(CSV_FILE, index=False)
        return df

@app.route('/')
def index():
    data = load_data()
    table_html = data.to_html(classes='table table-striped', index=False, escape=False)
    return render_template('index.html', table=table_html)

@app.route('/add', methods=['POST'])
def add():
    # Get user inputs from form
    date = request.form['date']
    temperature = request.form['temperature']
    humidity = request.form['humidity']
    windspeed = request.form['windspeed']
    condition = request.form['condition']
    
    # Append new data to CSV
    df = load_data()
    new_data = pd.DataFrame([[date, temperature, humidity, windspeed, condition]], columns=df.columns)
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)
    
    return redirect('/')

@app.route('/plot')
def plot():
    # Load data
    df = load_data()

    # Calculate moving averages
    df['Temperature_MA'] = df['Temperature'].rolling(window=7).mean()
    df['Humidity_MA'] = df['Humidity'].rolling(window=7).mean()
    df['WindSpeed_MA'] = df['WindSpeed'].rolling(window=7).mean()

    # Create individual plots with moving averages and specified colors
    fig_temp = px.line(df, x='Date', y='Temperature_MA', title='Temperature Over Time (°C)', 
                       line_shape='linear', template="plotly_dark", color_discrete_sequence=["#FF5733"])
    fig_temp.add_scatter(x=df['Date'], y=df['Temperature'], mode='lines', name='Daily Temperature', line=dict(width=0.5, color='lightgray'))
    fig_temp.update_layout(
        title_font=dict(size=24, family='Arial', color='white'),
        paper_bgcolor="#1f1f1f",
        plot_bgcolor="#1f1f1f",
        font_color="white",
    )

    fig_hum = px.line(df, x='Date', y='Humidity_MA', title='Humidity Over Time (%)', 
                      line_shape='linear', template="plotly_dark", color_discrete_sequence=["#33C1FF"])
    fig_hum.add_scatter(x=df['Date'], y=df['Humidity'], mode='lines', name='Daily Humidity', line=dict(width=0.5, color='lightgray'))
    fig_hum.update_layout(
        title_font=dict(size=24, family='Arial', color='white'),
        paper_bgcolor="#1f1f1f",
        plot_bgcolor="#1f1f1f",
        font_color="white",
    )

    fig_wind = px.line(df, x='Date', y='WindSpeed_MA', title='Wind Speed Over Time (km/h)', 
                       line_shape='linear', template="plotly_dark", color_discrete_sequence=["#75FF33"])
    fig_wind.add_scatter(x=df['Date'], y=df['WindSpeed'], mode='lines', name='Daily Wind Speed', line=dict(width=0.5, color='lightgray'))
    fig_wind.update_layout(
        title_font=dict(size=24, family='Arial', color='white'),
        paper_bgcolor="#1f1f1f",
        plot_bgcolor="#1f1f1f",
        font_color="white",
    )

    # Convert figures to HTML
    temp_html = fig_temp.to_html(full_html=False)
    hum_html = fig_hum.to_html(full_html=False)
    wind_html = fig_wind.to_html(full_html=False)

    return render_template('plot.html', temp_plot=temp_html, hum_plot=hum_html, wind_plot=wind_html)

@app.route('/data', methods=['GET'])
def data():
    search_term = request.args.get('search', '')
    if search_term:
        filtered_data = df[df['Date'].astype(str).str.contains(search_term, na=False)]
    else:
        filtered_data = df
    
    data_html = filtered_data.to_html(index=False, classes='data', border=0)
    return render_template('data.html', data=data_html, search_term=search_term)

if __name__ == '__main__':
    app.run(debug=True)
