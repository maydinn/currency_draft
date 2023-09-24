from datetime import datetime as ddt
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
    

#df = pd.read_csv('data.csv')


API_CUR = st.secrets["API_CUR"]
API_NEWS = st.secrets["API_NEWS"]
payload = {}
headers= {
  "apikey": API_CUR
}
currency_options = {'TRY':'Turkey', 'ARS':'Argentina', 'RUB':'Russia', 'KRW':'South Korea', 'EUR':'EU', 'CNY':'China', 'INR':'India'}
c = st.selectbox(label = 'Wählen Sie eine Stadt aus', options =currency_options.keys())
end_date = ddt.today().strftime('%Y-%m-%d')
dt = ddt.today()
dt = dt.replace(year=dt.year-1)
start_date = dt.strftime('%Y-%m-%d')
url = f"https://api.apilayer.com/exchangerates_data/timeseries?start_date={start_date}&end_date={end_date}&base=USD&symbols={c}"
urlData = requests.request("GET", url, headers=headers, data = payload).content
rawData = pd.read_json(io.StringIO(urlData.decode('utf-8')))
df = rawData.rates.apply(lambda x: x[c]).reset_index()
df.columns = ['ds','y']


df['ds'] = pd.to_datetime(df['ds'])
col1, col2, col3, col4 = st.columns(4)

now = df.y.values[-1]
key = c
val = round(  now - df.y.values[0],2)
delta_current ='The current {} is {} comparing the same day a years ago'.format(key,val, "more" if val >= 0 else "less")
col1.metric("Current",  f'{round(now,2)}', df[df.ds == df.ds.max()]['ds'].dt.strftime("%d %b, %Y").values[0], "inverse" if val >= 0 else "normal", delta_current)

val = round(df.y.max() - now,2)
delta_current ='The maximum value for {} in this year was {}, and comparing today {} {}'.format(key,df[df.y == df.y.max()]['ds'].dt.strftime('%m-%d').values[0],val, "more" if val >= 0 else "less")
col2.metric("Max", f'{round(df.y.max(),2)}', df[df.y == df.y.max()]['ds'].dt.strftime("%d %b, %Y").values[0], 'inverse', delta_current)

val = round(df.y.min() - now,2)
delta_current ='The minimum value for {} in this year was {}, and comparing today {} {}'.format(key,df[df.y == df.y.min()]['ds'].dt.strftime('%m-%d').values[0],val, "more" if val >= 0 else "less")
col3.metric("Min", f'{round(df.y.min(), 2)}', df[df.y == df.y.min()]['ds'].dt.strftime("%d %b, %Y").values[0], 'normal', delta_current)


val = round(df.y.rolling(30).mean().values[-1],2)
delta_current ='The mean for the last 30 days for {} is {}'.format(key,val )
col4.metric("Mean in last 30 days",  val, '' ,"inverse" if val >= 0 else "normal", delta_current )

m = Prophet(changepoint_prior_scale=0.75, changepoint_range=0.9)
m.fit(df)
future = m.make_future_dataframe(periods=3, freq="B")
forecast = m.predict(future)
fig_ = m.plot(forecast)
a = add_changepoints_to_plot(fig_.gca(), m, forecast, threshold=0.35)
c1, c2 = st.columns([3, 1])
df['str_time'] = df.apply(lambda x: x.ds.strftime("%d %b, %Y"), 1)

with c1:
    st.pyplot(fig_)
    
with c2:
    c2_x = c2.expander('Values')
    temp = df.rename(columns = {'str_time':'date', 'y':'values'}).tail(14).sort_values('ds',ascending=False)[['date', 'values']].reset_index(drop = True)
    temp.index +=1
    with c2_x:
        c2_x.table(temp.style.format({"values":"{:.5}"}))
    
    

    
col1, col2 = st.columns((4, 8))
col1_x = col1.expander('Changes Points')


chage_points_year = df.loc[df["ds"].isin(m.changepoints)].ds.dt.year.values
chage_points_month = df.loc[df["ds"].isin(m.changepoints)].ds.dt.month.values

df_m= df.loc[df["ds"].isin(m.changepoints)]
df_m['chages'] = m.params['delta'].mean(0)
df_m['chages_abs'] = abs(m.params['delta'].mean(0))
df_m = df_m[df_m.chages_abs > 0.35].rename(columns = {'str_time':'date', 'y':'values'})[['date', 'values']].reset_index(drop = True)

with col1_x:
     col1_x.table(df_m)

# url = "http://api.nytimes.com/svc/archive/v1/{}/{}.json?api-key={}"




# points = df.loc[df["ds"].isin(m.changepoints)].reset_index(drop = True)

# d = datetime.timedelta(days = 3)

# expand00 = chage_points['date'].values[0]
# col2_00 = col2.expander(expand00)
# with col2_00:
#     url_0 = url.format(chage_points_year[0], chage_points_month[0], API_NEWS)
#     items = requests.get(url_0)
#     data = items.json()
#     ny = pd.json_normalize(data['response']['docs'])
#     ny['time'] = pd.to_datetime(ny.pub_date.str[:10])
#     df0 =ny[(ny.time <(points['ds'][0] + d)) & (ny.time > (points['ds'][0] - d))]
#     eco = df0[df0['abstract'].apply(lambda x: True if currency_options[c].lower() in x.lower() else False)]
#     if len(eco) > 0:
#         eco = eco[['abstract', 'web_url', 'time']].rename(columns = {'abstract':'Info','web_url':'Url'} ).set_index('time')
#     st.write(eco)   
# expand01 = chage_points['date'].values[1]    
# col2_01 = col2.expander(expand01)
# with col2_01:
#     url_1 = url.format(chage_points_year[1], chage_points_month[1], API_NEWS)
#     items = requests.get(url_1)
#     data = items.json()
#     ny = pd.json_normalize(data['response']['docs'])
#     ny['time'] = pd.to_datetime(ny.pub_date.str[:10])
#     df0 =ny[(ny.time <(points['ds'][0] + d)) & (ny.time > (points['ds'][0] - d))]
#     eco = df0[df0['abstract'].apply(lambda x: True if currency_options[c].lower() in x.lower() else False)]
#     if len(eco) > 0:
#         eco = eco[['abstract', 'web_url', 'time']].rename(columns = {'abstract':'Info','web_url':'Url'} ).set_index('time')
#     st.write(eco)  
# expand02 = chage_points['date'].values[2]    
# col2_02 = col2.expander(expand02)
# with col2_02:
#     url_2 = url.format(chage_points_year[2], chage_points_month[2], API_NEWS)
#     items = requests.get(url_2)
#     data = items.json()
#     ny = pd.json_normalize(data['response']['docs'])
#     ny['time'] = pd.to_datetime(ny.pub_date.str[:10])
#     df0 =ny[(ny.time <(points['ds'][0] + d)) & (ny.time > (points['ds'][0] - d))]
#     eco = df0[df0['abstract'].apply(lambda x: True if currency_options[c].lower() in x.lower() else False)]
#     if len(eco) > 0:
#         eco = eco[['abstract', 'web_url', 'time']].rename(columns = {'abstract':'Info','web_url':'Url'} ).set_index('time')
#     st.write(eco)  
    
# expand03 = chage_points['date'].values[3]    
# col2_03 = col2.expander(expand03)
# with col2_03:
#     url_3 = url.format(chage_points_year[3], chage_points_month[3], API_NEWS)
#     items = requests.get(url_3)
#     data = items.json()
#     ny = pd.json_normalize(data['response']['docs'])
#     ny['time'] = pd.to_datetime(ny.pub_date.str[:10])
#     df0 =ny[(ny.time <(points['ds'][0] + d)) & (ny.time > (points['ds'][0] - d))]
#     eco = df0[df0['abstract'].apply(lambda x: True if currency_options[c].lower() in x.lower() else False)]
#     if len(eco) > 0:
#         eco = eco[['abstract', 'web_url', 'time']].rename(columns = {'abstract':'Info','web_url':'Url'} ).set_index('time')
#     st.write(eco) 
    
# expand04 = chage_points['date'].values[4]    
# col2_04 = col2.expander(expand04)
# with col2_04:
#     url_4 = url.format(chage_points_year[4], chage_points_month[2], API_NEWS)
#     items = requests.get(url_4)
#     data = items.json()
#     ny = pd.json_normalize(data['response']['docs'])
#     ny['time'] = pd.to_datetime(ny.pub_date.str[:10])
#     df0 =ny[(ny.time <(points['ds'][0] + d)) & (ny.time > (points['ds'][0] - d))]
#     eco = df0[df0['abstract'].apply(lambda x: True if currency_options[c].lower() in x.lower() else False)]
#     if len(eco) > 0:
#         eco = eco[['abstract', 'web_url', 'time']].rename(columns = {'abstract':'Info','web_url':'Url'} ).set_index('time')
#     st.write(eco) 
    


