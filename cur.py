from datetime import datetime
import pandas as pd
from prophet import Prophet
import requests
import io
import matplotlib.pyplot as plt
import matplotlib
from prophet.plot import add_changepoints_to_plot
import streamlit as st
import plotly.tools


df = pd.read_csv('data.csv')
m = Prophet()
m.fit(df)
future = m.make_future_dataframe(periods=3, freq="B")
forecast = m.predict(future)
fig_ = m.plot(forecast)
a = add_changepoints_to_plot(fig_.gca(), m, forecast)
fig, x = plt.subplots()
x = a

# @st.cache(hash_funcs={matplotlib.figure.Figure: hash})
# def plot():
#     #time.sleep(2)
#     a = add_changepoints_to_plot(fig_.gca(), m, forecast)
#     fig, ax = plt.subplots(11)
#     ax.imshow(a)
    
#     return fig

#horizontal_size = st.slider("horizontal size", 50,150,step=50)
st.pyplot(fig)
