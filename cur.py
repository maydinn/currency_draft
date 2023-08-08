from datetime import datetime
import datetime
import pandas as pd
from prophet import Prophet
import requests
import io
import matplotlib.pyplot as plt
import matplotlib
from prophet.plot import add_changepoints_to_plot
import streamlit as st
import plotly.tools

st.set_page_config(layout='wide', initial_sidebar_state='expanded',page_title="currency",
    )
st.write(
    """
    <style>
    [data-testid="stMetricDelta"] svg {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    

df = pd.read_csv('data.csv')
ny = pd.read_csv('ny.csv')

ny['time'] = pd.to_datetime(ny['time'])
df['ds'] = pd.to_datetime(df['ds'])
col1, col2, col3, col4 = st.columns(4)
key = 'Turkisch Lira'
now = df.y.values[-1]

val = round(df.y.values[0] - now,2)
delta_current ='The current {} is {} comparing the same day before'.format(key,val, "more" if val >= 0 else "less")
col1.metric("Current",  f'{round(now,2)}', df[df.ds == df.ds.max()]['ds'].dt.strftime("%d %b, %Y").values[0], "inverse" if val >= 0 else "normal", delta_current)

val = round(df.y.max() - now,2)
delta_current ='The maximum value for {} in this year was {}, and comparing today {} {}'.format(key,df[df.y == df.y.max()]['ds'].dt.strftime('%m-%d'),val, "more" if val >= 0 else "less")
col2.metric("Max", f'{round(df.y.max(),2)}', df[df.y == df.y.max()]['ds'].dt.strftime("%d %b, %Y").values[0], 'inverse', delta_current)

val = round(df.y.min() - now,2)
delta_current ='The minimum value for {} in this year was {}, and comparing today {} {}'.format(key,df[df.y == df.y.min()]['ds'].dt.strftime('%m-%d'),val, "more" if val >= 0 else "less")
col3.metric("Min", f'{round(df.y.min(), 2)}', df[df.y == df.y.min()]['ds'].dt.strftime("%d %b, %Y").values[0], 'normal', delta_current)


val = round(df.y.rolling(7).mean().values[-1],2)
delta_current ='The mean for the last 7 days for {} is {}'.format(key,val )
col4.metric("Mean in last 7 days",  val, '' ,"inverse" if val >= 0 else "normal", delta_current )

m = Prophet(n_changepoints = 10)
m.fit(df)
future = m.make_future_dataframe(periods=3, freq="B")
forecast = m.predict(future)
fig_ = m.plot(forecast)
a = add_changepoints_to_plot(fig_.gca(), m, forecast)
c1, c2 = st.columns([3, 1])
df['str_time'] = df.apply(lambda x: x.ds.strftime("%d %b, %Y"), 1)
with c1:
    st.pyplot(fig_)
    
with c2:
    
    st.write(df.rename(columns = {'str_time':'date', 'y':'values'}).tail(7).sort_values('ds',ascending=False)[['date', 'values']].reset_index(drop = True))
    

    
col1, col2 = st.columns((4, 8))
col1_x = col1.expander('Changes Points')

with col1_x:
    st.write(df.loc[df["ds"].isin(m.changepoints)].rename(columns = {'str_time':'date', 'y':'values'})[['date', 'values']].reset_index(drop = True))
    

col2_x = col2.expander('News in Changes Points')
points = df.loc[df["ds"].isin(m.changepoints)].reset_index(drop = True)

d = datetime.timedelta(days = 7)
df0 =ny[(ny.time <(points['ds'][0] + d)) & (ny.time > (points['ds'][0] - d))]
st.write(df0)
eco = df0[df0.keywords.apply(lambda x: True if 'econom' in " ".join([i['value'].lower()  for i in x if len(x) > 0]) else False)]
eco = eco[['abstract', 'web_url']].rename(columns = {'abstract':'Info','web_url':'Url'} )
with col2_x:
    st.write(eco)       
    
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

