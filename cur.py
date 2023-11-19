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
import plotly.express as px
import plotly.graph_objects as go

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


c = "USD"
end_date = ddt.today().strftime('%Y-%m-%d')
dt = ddt.today()
dt = dt.replace(month=dt.month-1)
start_date = dt.strftime('%Y-%m-%d')
url = f"https://api.apilayer.com/exchangerates_data/timeseries?start_date={start_date}&end_date={end_date}&base=EUR&symbols={c}"
urlData = requests.request("GET", url, headers=headers, data = payload).content
rawData = pd.read_json(io.StringIO(urlData.decode('utf-8')))
df = rawData.rates.apply(lambda x: x[c]).reset_index()
df.columns = ['ds','y']


df['ds'] = pd.to_datetime(df['ds'])

col1, col2, col3, col4 = st.columns(4)

now = df.y.values[-1]
key = c
val = round(  now - df.y.values[0],2)
delta_current ='The current {} is {} comparing the same day a month ago'.format(key,val, "more" if val >= 0 else "less")
col1.metric("Current",  f'{round(now,2)}', df[df.ds == df.ds.max()]['ds'].dt.strftime("%d %b, %Y").values[0], "inverse" if val >= 0 else "normal", delta_current)

val = round(df.y.max() - now,2)
delta_current ='The maximum value for {} in this month was {}, and comparing today {} {}'.format(key,df[df.y == df.y.max()]['ds'].dt.strftime('%m-%d').values[0],val, "more" if val >= 0 else "less")
col2.metric("Max", f'{round(df.y.max(),2)}', df[df.y == df.y.max()]['ds'].dt.strftime("%d %b, %Y").values[0], 'inverse', delta_current)

val = round(df.y.min() - now,2)
delta_current ='The minimum value for {} in this year was {}, and comparing today {} {}'.format(key,df[df.y == df.y.min()]['ds'].dt.strftime('%m-%d').values[0],val, "more" if val >= 0 else "less")
col3.metric("Min", f'{round(df.y.min(), 2)}', df[df.y == df.y.min()]['ds'].dt.strftime("%d %b, %Y").values[0], 'normal', delta_current)


val = round(df.y.rolling(7).mean().values[-1],2)
delta_current ='The mean for the last 7 days for {} is {}'.format(key,val )
col4.metric("Mean in last 7 days",  val, '' ,"inverse" if val >= 0 else "normal", delta_current )

m = Prophet(changepoint_prior_scale=0.01, changepoint_range=0.95, n_changepoints=3 )
m.fit(df)
future = m.make_future_dataframe(periods=2, freq="B")
forecast = m.predict(future)



fig_ = m.plot(forecast)

a = add_changepoints_to_plot(fig_.gca(), m, forecast, threshold= 0.01)
plt.title('USD to EUR Exchange Rate Trends: One-Month Overview with Two-Day Forecast')
plt.xlabel('Date')


plt.ylabel('Value')


plt.legend(['Actual', 'Prediction', 'Prediction Components', 'Trend', 'Change in Trend'])

    
c1, c2 = st.columns([3, 1])
frc = forecast.iloc[:, [0,15]].rename(columns = {'yhat':'y'}).tail(2)
df = pd.concat([df,frc], ignore_index=True)

df['str_time'] = df.apply(lambda x: x.ds.strftime("%d %b, %Y"), 1)

with c1:
    st.pyplot(fig_)
    exp = st.expander('Explantion')
    with exp:
        
        st.write("""This comprehensive graph provides an in-depth analysis of the Euro (EUR) to US Dollar (USD) exchange rate. The blue line depicts the historical exchange rate trends, showcasing observed values over time. The red line represents the underlying predictions captured forecasting model, offering insights into long-term patterns.Key features include the shaded region around the prediction line, illustrating the uncertainty associated with the forecast. Notably, the graph extends into a two-day prediction period providing a forward projection based on historical patterns.The highlighted areas on the graph signify significant changes in trends. Down the page, you'll find news highlights corresponding to these specific dates, offering contextual information on events that may have influenced the observed shifts in the exchange rate trends.""")
with c2:
    c2_x = c2.expander('Values')
    temp = df.rename(columns = {'str_time':'date', 'y':'values'}).tail(14).sort_values('ds',ascending=False)[['date', 'values']].reset_index(drop = True)
    temp.index +=1
    with c2_x:
        c2_x.table(temp)
    
    

    
col1, col2 = st.columns((4, 8))
col1_x = col1.expander('Changes Points')


chage_points_year = df.loc[df["ds"].isin(m.changepoints)].ds.dt.year.values
chage_points_month = df.loc[df["ds"].isin(m.changepoints)].ds.dt.month.values

df_m= df.loc[df["ds"].isin(m.changepoints)]
df_m['chages'] = m.params['delta'].mean(0)
df_m['chages_abs'] = abs(m.params['delta'].mean(0))

df_ny = df_m[df_m.chages_abs > 0.01]
chage_points_year = df_ny.ds.dt.year.values
chage_points_month = df_ny.ds.dt.month.values
points = df_ny.apply(lambda x: x.ds.strftime("%y%m%d"), 1)
points_list = points.values

def make_clickable(link,text):
    # target _blank to open new window
    # extract clickable text to display for your link
    return f'<a target="_blank" href="{link}">{text}</a>'

df_m = df_m[df_m.chages_abs > 0.01].rename(columns = {'str_time':'date', 'y':'values'})[['date', 'values']].reset_index(drop = True)



with col1_x:
     col1_x.table(df_m.head(3))
        
        

with col1_x:
    if len(points_list) > 0:
        expand00 = df_m['date'].values[0]
        col2_00 = col2.expander(f"News on {expand00}")
        with col2_00:
            url = f"https://www.tagesschau.de/api2u/news?date={points_list[0]}&ressort=wirtschaft"


            request = requests.get(url)
            response = request.json()

            title_list = []
            date_list = []
            web_list = []

            news_num = len(response['news'])

            for i in range(news_num):
                date_list.append(response['news'][i]['date'])
                title_list.append(response['news'][i]['title'])
                web_list.append(response['news'][i]['detailsweb'])


            news = pd.DataFrame({'Date': date_list,
                               'Title': title_list,
                               'Web': web_list,
                               })
            news['News Title'] = news[['Web', 'Title']].apply(lambda x: make_clickable(x['Web'], x['Title']), 1)

            news['Date'] = news['Date'].apply(lambda x: pd.to_datetime(x).strftime("%d %b, %Y"))
            news.index +=1
            news_ = news[['Date', 'News Title', 'Web']]
            news_ = news_.to_html(escape=False, index=False)
            st.write(news_, unsafe_allow_html=True)
#             st.markdown(
#         f"""
#         <div style="max-width: 600px;">
#             {news_}
#         </div>
#         """,
#         unsafe_allow_html=True
#     )
             
            #st.write(news[['Date', 'Title', 'Web']])
           
        if len(points_list) > 1:
            expand01 = df_m['date'].values[1]
            col2_01 = col2.expander(f"News on {expand01}")
            with col2_01:
                url = f"https://www.tagesschau.de/api2u/news?date={points_list[1]}&ressort=wirtschaft"


                request = requests.get(url)
                response = request.json()

                title_list = []
                date_list = []
                web_list = []

                news_num = len(response['news'])

                for i in range(news_num):
                    date_list.append(response['news'][i]['date'])
                    title_list.append(response['news'][i]['title'])
                    web_list.append(response['news'][i]['detailsweb'])


                news = pd.DataFrame({'Date': date_list,
                                   'Title': title_list,
                                   'Web': web_list,
                                   })
                news['News Title'] = news[['Web', 'Title']].apply(lambda x: make_clickable(x['Web'], x['Title']), 1)

                news['Date'] = news['Date'].apply(lambda x: pd.to_datetime(x).strftime("%d %b, %Y"))
                news.index +=1
                news_ = news[['Date', 'News Title']]
                news_ = news_.to_html(escape=False)
                st.write(news_, unsafe_allow_html=True)
    else:
        col2_00 = col2.expander("")
        with col2_00:
            st.write("No Change in Trend")
        
