from datetime import datetime
import pandas as pd
from prophet import Prophet
import requests
import io
import matplotlib.pyplot as plt
from prophet.plot import add_changepoints_to_plot
import streamlit as st

df = pd.read_csv('data.csv')
m = Prophet()
m.fit(df)
future = m.make_future_dataframe(periods=3, freq="B")
forecast = m.predict(future)
fig = m.plot(forecast)
a = add_changepoints_to_plot(fig.gca(), m, forecast)

st.plotly_chart(a, 
         use_container_width=True )