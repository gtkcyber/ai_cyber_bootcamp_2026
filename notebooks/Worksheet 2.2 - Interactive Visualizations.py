import streamlit as st
import pandas as pd

DATA_PATH = '../data'


# In this lab you will be asked to create a small interactive dashboard using the dailybots CSV file.
# You will incorporate layout and dynamic elements into your dashboard.
# The two elements we are going to include are a bar chart which shows a breakdown of bot attacks and the raw data.
# You will be able to filter the bar chart by industry with a drop down.

# First read the data into a pandas dataframe
raw_data = pd.read_csv(f'{DATA_PATH}/dailybots.csv')

# Create a title and some description of what we are viewing:
st.markdown("Your text here...")

# We first have to create a drop down with a list of the industries.  You can read the docs for the
# selectbox here: https://docs.streamlit.io/develop/api-reference/widgets/st.selectbox
# Don't forget to assign the value from the select box to a variable.
industry_list =
selected_industry =

# Now create two tabs, one for the data table, and other for a chart.  You may create more if you wish.

# Next create a dataframe with a filter by industry that breaks down the infected host total by botfam.
with chart_tab:
    # Your code here ...

# Now in the table tab, create a data frame of the raw data.  If you want you can apply the filter from the selectbox
# to the data table as well.  You can format the columns of the data frame as well using the column configuration parameters
with table_tab:
    # Your code here...
