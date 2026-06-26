import streamlit as st
import pandas as pd

DATA_PATH = '../data'

# Display some intro text
st.markdown("""
# Basic Application 
This basic application will demonstrate how to display data, both as a table and as a chart.
""")

raw_data = pd.read_csv(f'{DATA_PATH}/dailybots.csv')

# Prepare the data for a line chart.
line_chart_data = raw_data[['date', 'hosts']].groupby('date').sum('hosts')

# Display the line chart
st.area_chart(line_chart_data)

# Display the table
st.dataframe(raw_data, hide_index=True)


