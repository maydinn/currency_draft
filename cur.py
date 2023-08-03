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

key = 'Turkisch Lira'
now = df.y.values[-1]
val = round(df.y.values[0] - now,2)
delta_current ='The current {} is {} comparing the same day before'.format(key,val, "more" if val >= 0 else "less")
col1.metric("Current",  f'{now}', df.ds.max(), "inverse" if val >= 0 else "normal", delta_current)

val = round(df.y.max - now],2)
delta_current ='The maximum value for {} in this year was {}, and comparing today {} °C {}'.format(key,df[df.y == df.y.max()]['ds'].dt.strftime('%m-%d'),val, "more" if val >= 0 else "less")
col2.metric("Max", f'{df.y.max()}', str(df[df.y == data.y.max()]['time'].dt.strftime('%m-%d')), 'inverse', delta_current)

val = round(df.y.min - now],2)
delta_current ='The minimum value for {} in this year was {}, and comparing today {} °C {}'.format(key,df[df.y == df.y.min()]['ds'].dt.strftime('%m-%d'),val, "more" if val >= 0 else "less")
col2.metric("Max", f'{df.y.min()}', str(df[df.y == data.y.min()]['time'].dt.strftime('%m-%d')), 'inverse', delta_current)


data_me = data.iloc[-20:,:]
val = round(df_new.trend.values[-1] - df_new.trend.values[-2],2)
val_all = round(df_new.trend.values[-1] - df_new.trend.values[0],2)

delta_current ='The mean for the last 7 days for {} is {}'.format(key,sum(df.y.values[-1:-7])/7 )
col4.metric("Mean in last 7 days",  f'{val_all} °C',sum(df.y.values[-1:-7])/7 ,"inverse" if val >= 0 else "normal", delta_current )

m = Prophet()
m.fit(df)
future = m.make_future_dataframe(periods=3, freq="B")
forecast = m.predict(future)
fig_ = m.plot(forecast)
a = add_changepoints_to_plot(fig_.gca(), m, forecast)
st.pyplot(fig_)
#fig, x = plt.subplots()
#x = a

# @st.cache(hash_funcs={matplotlib.figure.Figure: hash})
# def plot():
#     #time.sleep(2)
#     a = add_changepoints_to_plot(fig_.gca(), m, forecast)
#     fig, ax = plt.subplots(11)
#     ax.imshow(a)
    
#     return fig

#horizontal_size = st.slider("horizontal size", 50,150,step=50)

