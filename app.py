import streamlit as st
import numpy as np
import pandas as pd
from pybit import usdt_perpetual
from tradingview_ta import *
import datetime as dt

st.set_page_config(page_icon="https://i.seadn.io/gae/TSWyyWt2lATg1Ecc1i76ju5QtnhKQgT1F5mH4f8OEqpO-Jt4gy_c86zwnpS_23VKDg6nht0pQzezTQnxVU-plTmeCPuvlbqVqH6H?auto=format&w=256", page_title="Grug's Lair volatility script")

st.sidebar.image(
    "https://i.seadn.io/gae/TSWyyWt2lATg1Ecc1i76ju5QtnhKQgT1F5mH4f8OEqpO-Jt4gy_c86zwnpS_23VKDg6nht0pQzezTQnxVU-plTmeCPuvlbqVqH6H?auto=format&w=256",
    width=50,
)
st.sidebar.header('Intro')
st.sidebar.markdown(">Like it says in the book: 'We are blessed... and cursed'")
st.sidebar.markdown("In crypto we are blessed with high volatility, which at the same time means that")
st.sidebar.markdown("1. entry points for high leveraged positions should be chosen with special care")
st.sidebar.markdown("2. opportunities appear and fade away very quickly")

st.sidebar.header('How can you use this tool?')
st.sidebar.markdown("- The color of the cells 'period' is most blue for those cells which have the biggest volatility value; the color of the cells 'period_p' is near red when value is near 0 and green when value is near 1.")
st.sidebar.markdown('- In the bull market you can make a small list of the coins that "have not yet run" for further analysis by choosing small-valued timeframe columns, such as "1D"; you can also choose use the coins that might have completed their retracement')
st.sidebar.markdown('- ...?')

st.sidebar.header('How does it work?')
st.sidebar.markdown('Feel free to join the [Lair](https://discord.com/invite/gDyJBYUNDq) and read the full script code!')

c1, c2 = st.columns([1, 8])

# with c1:
#     st.image(
#         "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/240/apple/285/chart-increasing_1f4c8.png",
#         width=90,
#     )

st.markdown(
    """# **Crypto Volatility Dashboard**
A an app pulling the prices from [ByBit](https://www.bybit.com/future-activity/en-US/developer) to explore the volatility of each coin.
"""
)

st.header("**Combined Table**")

# Load market data from Binance API
# df = pd.read_json("https://api.binance.com/api/v3/ticker/24hr")

session_unauth = usdt_perpetual.HTTP(endpoint="https://api.bybit.com")
all_symbols = pd.json_normalize(session_unauth.query_symbol()['result'])
coin_names = all_symbols.loc[all_symbols['name'].str[-1:]=='T', 'name'].to_list()[:5]

dfs = {}
dfs_daily = {}
volatility_daily = []
volatility = []
for coin in coin_names:
  tickers = session_unauth.query_kline(
    symbol=coin,
    interval=5,
    limit=144,
    from_time=int(dt.datetime.now().timestamp()-60*144)
)['result']
  tickers_daily = session_unauth.query_kline(
    symbol=coin,
    interval='D',
    limit=200,
    from_time=int(dt.datetime.now().timestamp()-60*60*24*200)
)['result']
  df = pd.DataFrame(tickers, columns = ['open_time', 'volume', 'open', 'high', 'low', 'close', 'turnover'])
  df['open_time'] = pd.to_datetime(df['open_time'], unit = 's')
  dfs[coin] = df

  df_daily = pd.DataFrame(tickers_daily, columns = ['open_time', 'volume', 'open', 'high', 'low', 'close', 'turnover'])
  df_daily['open_time'] = pd.to_datetime(df_daily['open_time'], unit = 's')
  dfs_daily[coin] = df

  last_price =  df.iloc[-1:]['close'].to_list()[0]
  volatility_row = {'symbol': coin}
  volatility_row_daily = {'symbol': coin}
  volatility_row['last_price'] = last_price
  for min in [1, 3, 6, 12, 24, 48, 144]:
    local_high = df.iloc[-min:]['high'].max()
    local_low = df.iloc[-min:]['low'].min()
    volatility_row[str(min*5)+'m'] = local_high/local_low - 1
    try:
      volatility_row[str(min*5) + 'm_p'] = (last_price - local_low)/(local_high - local_low)
    except:
      try:
        volatility_row[str(min*5) + 'm_p'] = (last_price - df.iloc[-min-1:]['low'].min())/(df.iloc[-min-1:]['high'].max() - df.iloc[-min-1:]['low'].min())
      except:
        continue

  for day in [1, 2, 3, 5, 10, 15, 30, 60, 90, 200]:
    local_high = df_daily.iloc[-day:]['high'].max()
    local_low = df_daily.iloc[-day:]['low'].min()
    volatility_row_daily[str(day)+'D'] = local_high/local_low - 1
    try:
      volatility_row_daily[str(day)+'D_p'] = (last_price - local_low)/(local_high - local_low)
    except:
      try:
        volatility_row_daily[str(day)+'D_p'] = (last_price - df.iloc[-min-1:]['low'].min())/(df.iloc[-min-1:]['high'].max() - df.iloc[-min-1:]['low'].min())
      except:
        continue
  volatility_daily.append(volatility_row_daily)
  volatility.append(volatility_row)
  
st.markdown(f"""Last update is: {dt.datetime.now().replace(microsecond=0)} UTC""")

tas_list = []
pss_week = get_multiple_analysis(screener="crypto", interval=Interval.INTERVAL_1_WEEK, symbols=["BYBIT:"+i+".P" for i in coin_names])
pss_day = get_multiple_analysis(screener="crypto", interval=Interval.INTERVAL_1_DAY, symbols=["BYBIT:"+i+".P" for i in coin_names])
pss_4hours = get_multiple_analysis(screener="crypto", interval=Interval.INTERVAL_4_HOURS , symbols=["BYBIT:"+i+".P" for i in coin_names])
pss_1hour = get_multiple_analysis(screener="crypto", interval=Interval.INTERVAL_1_HOUR , symbols=["BYBIT:"+i+".P" for i in coin_names])

for coin in ["BYBIT:"+i+".P" for i in coin_names]:
  try: 
    pss_week_ = pss_week[coin].indicators
  except:
    pss_week_ = {}
  try: 
    pss_day_ = pss_day[coin].indicators
  except:
    pss_day_ = {}
  try: 
    pss_4hours_ = pss_4hours[coin].indicators
  except:
    pss_4hours_ = {}
  try: 
    pss_1hour_ = pss_1hour[coin].indicators
  except:
    pss_1hour_ = {}
  tas_list.append([coin[6:-2], pss_week_.get('SMA200'), pss_day_.get('SMA200'), pss_4hours_.get('SMA100'), pss_1hour_.get('SMA100'), pss_day_.get('RSI'),  
                   pss_4hours_.get('RSI'), pss_1hour_.get('RSI')])
technicals = pd.DataFrame(tas_list, columns = ['symbol', 'SMA200W', 'SMA200D', 'SMA400H', 'SMA100H', 'RSID', 'RSI4H', 'RSIH']).set_index('symbol')

df = technicals.join(pd.DataFrame(volatility).set_index('symbol')).join(pd.DataFrame(volatility_daily).set_index('symbol')).sort_values(['3D'], ascending = False)
for sma_ in ['SMA200W',	'SMA200D',	'SMA400H',	'SMA100H']:
  df[sma_] = df['last_price']/df[sma_]
df = df.drop(columns = ['last_price'])

# Custom function for rounding values
def round_value(input_value):
    if input_value.values > 1:
        a = float(round(input_value, 2))
    else:
        a = float(round(input_value, 8))
    return a


crpytoList = {
    "Price 1": "BTCBUSD",
    "Price 2": "ETHBUSD",
    "Price 3": "BNBBUSD",
    "Price 4": "XRPBUSD",
    "Price 5": "ADABUSD",
    "Price 6": "DOGEBUSD",
    "Price 7": "SHIBBUSD",
    "Price 8": "DOTBUSD",
    "Price 9": "MATICBUSD",
}

# col1, col2, col3 = st.columns(3)

# for i in range(len(crpytoList.keys())):
#     selected_crypto_label = list(crpytoList.keys())[i]
#     selected_crypto_index = list(df.symbol).index(crpytoList[selected_crypto_label])
#     selected_crypto = st.sidebar.selectbox(
#         selected_crypto_label, df.symbol, selected_crypto_index, key=str(i)
#     )
#     col_df = df[df.symbol == selected_crypto]
#     col_price = round_value(col_df.weightedAvgPrice)
#     col_percent = f"{float(col_df.priceChangePercent)}%"
#     if i < 3:
#         with col1:
#             st.metric(selected_crypto, col_price, col_percent)
#     if 2 < i < 6:
#         with col2:
#             st.metric(selected_crypto, col_price, col_percent)
#     if i > 5:
#         with col3:
#             st.metric(selected_crypto, col_price, col_percent)

st.header("")

# st.download_button(
#    label="Download data as CSV",
#    data=df,
#    #file_name='large_df.csv',
#    # mime='text/csv'
#    )


@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")


csv = convert_df(df)

# st.download_button(
#     label="Download data as CSV",
#     data=csv,
#     file_name="large_df.csv",
#     mime="text/csv",
# )

def style_bigger(v, border, props=''):
    return props if v > border else None
def style_smaller(v, border, props=''):
    return props if v < border else None

df = technicals.join(pd.DataFrame(volatility).set_index('symbol')).join(pd.DataFrame(volatility_daily).set_index('symbol')).sort_values(['3D'], ascending = False)
for sma_ in ['SMA200W',	'SMA200D',	'SMA400H',	'SMA100H']:
  df[sma_] = df['last_price']/df[sma_]
df = df.drop(columns = ['last_price'])
# df_styled = df.style.background_gradient(subset=['5m']).format(precision=2)
# df_styled = df.style.background_gradient(subset=['5m']).format(precision=3)
df_styled = df.style.format(precision=3)
for col in df.columns[:]:
  if col[0] == 'S':
    df_styled = df_styled.highlight_between(left=0.9, right=1.1, axis=1, props='color:white; background-color:purple;', subset=[col])
  elif col[0] == 'R':
    df_styled = df_styled.applymap(style_bigger, border = 70, props='color:red;', subset=[col])
    df_styled = df_styled.applymap(style_smaller, border = 0.3, props='color:green;', subset=[col])
  elif col[-1] != 'p':
    df_styled = df_styled.background_gradient(cmap = 'Blues', subset=[col])
  else:
    df_styled = df_styled.background_gradient(cmap = 'RdYlGn', subset=[col])
df_styled = df_styled.set_sticky(axis=0).set_sticky(axis=1)

st.dataframe(df_styled, height=500)


# st.markdown(
#     """
# <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
# <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
# <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
# """,
#     unsafe_allow_html=True,
# )
