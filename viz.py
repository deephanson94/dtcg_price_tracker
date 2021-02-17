import streamlit as st
import numpy as np 
import pandas as pd
import altair as alt

bt_list = ['BT1', 'BT2','BT3','BT4','BT5','ST1','ST2','ST3','ST4','ST5','ST6','P']

st.title('DTCG prices (YEN)')

# read in
df = pd.read_csv('weekly_prices.csv')
df = df.drop(columns=['card_id_aa', 'level'])



# filter
st.header("Search by digimon name")
digi_name = st.text_input("Digimon name in eng:")
expander1 = st.beta_expander("Advanced filtering", expanded=True)
# container1.subheader("Advanced filtering")
col1, col2, col3 = expander1.beta_columns([1,1,3])
bt_version = col1.selectbox("Version", list(['(All)']) + bt_list)
AA = col2.selectbox("Parallel art", ['(All)', 'Yes', 'No'])
shop = col3.multiselect("Shop name", ['bigweb', 'yuyutei'], default=['bigweb', 'yuyutei'])
# xxx = col3.selectbox("xxxxxxx", ['(All)','XXX', 'YYY'])

digi_name = digi_name.strip()

st.header('Table')

# display df
if digi_name:
    df = df[df['name_eng'].str.contains(digi_name, case=False)]
    if bt_version != '(All)':
        df = df[df['card_id'].str.contains(bt_version)]
    if AA != '(All)':
        AA = AA == 'Yes'
        df = df[df['AA'] == AA]
    df = df[df['shop'].isin(shop)]
    dft = df.copy()
    latest_updated_dt = dft.columns[-1]
    dft['latest'] = dft[latest_updated_dt]
    latest_updated_dt = latest_updated_dt.replace('p_', '')
    latest_updated_dt = latest_updated_dt[0:4] + '-' + latest_updated_dt[4:6] + '-' + latest_updated_dt[6:]
    latest_updated_dt = pd.to_datetime(latest_updated_dt)
    st.text("Latest updated date: " + str(latest_updated_dt.strftime('%b-%d')))
    st.dataframe(dft[['card_id', 'name_eng', 'AA', 'rarity', 'shop', 'latest']])

    # draw!
    dfv = df.copy()
    dfv = dfv.replace(0, np.nan)
    dfv['bt_name'] = dfv['card_id'] + " | " + dfv['name_eng'] + " | " + dfv['rarity']

    st.header('Plot')
    selected_bt_name = st.selectbox("Plot digimon:", dfv['bt_name'].unique().tolist())
    
    dfv = dfv.loc[dfv.bt_name == selected_bt_name]
    dfv = dfv.melt(id_vars=['bt_name','card_id', 'name_eng', 'name_jap','AA','rarity', 'shop'], var_name='Date', value_name='Price')
    # modify date to datetime
    dfv['Date'] = dfv['Date'].str.replace(r'^p_', '')
    dfv['Date'] = pd.to_datetime(dfv['Date'].str[0:4] + '-' + dfv['Date'].str[4:6] + '-' + dfv['Date'].str[6:])
    dfv_normal = dfv.loc[dfv.AA == 0]
    dfv_AA = dfv.loc[dfv.AA == 1]

    # c = alt.Chart(dfv_normal).mark_line().encode(
    #     x='Date',
    #     y='Price',
    #     color='name_eng',
    #     tooltip=['shop']
    # )
    st.subheader('Normal art')
    c = alt.Chart(dfv_normal).mark_line(interpolate='linear', point=True).encode(
        x='Date',
        y=alt.X('Price', scale=alt.Scale(zero=False, padding=1)),
        color='shop',
        text='Price',
        tooltip=['Date', 'Price', 'shop']
    )
    t = c.mark_text(align='center', baseline='middle', fontSize=10, dy=-10).encode(
        text='Price',
    )
    st.altair_chart(c+t, use_container_width=True)
    
    st.subheader('Alternate art')
    c = alt.Chart(dfv_AA).mark_line(interpolate='linear', point=True).encode(
        x='Date',
        y=alt.X('Price', scale=alt.Scale(zero=False, padding=1)),
        color='shop',
        tooltip=['Date', 'Price', 'shop']
    )
    t = c.mark_text(align='center', baseline='middle', fontSize=10, dy=-10).encode(
        text='Price',
    )
    st.altair_chart(c+t, use_container_width=True)
    
    st.subheader('Normal + AA')
    c = alt.Chart(dfv).mark_circle(interpolate='linear', point=True).encode(
        x='Date',
        y=alt.X('Price', scale=alt.Scale(zero=False, padding=1)),
        color='shop',
        size=alt.Size('AA', scale=alt.Scale(5)),
        tooltip=['Date', 'Price', 'AA']
    )
    t = alt.Chart(dfv).mark_text(align='center', baseline='middle', fontSize=10, dy=-10).encode(
        x='Date',
        y=alt.X('Price', scale=alt.Scale(zero=False, padding=1)),
        text='Price',
    )
    st.altair_chart(c, use_container_width=True)
