import streamlit as st
import pandas as pd
import plotly.express as px

# データの読み込み（header で項目名の行を指定）
df_hs = pd.read_excel("files/都道府県別_学校数(高).xlsx", header=5)         # シート3枚。今回は1枚目（本校+分校）のデータを使用
df_uni = pd.read_excel("files/都道府県別_学校数(大)_2025.xlsx", header=5)
df_rate1 = pd.read_excel("files/都道府県別_卒業後状況_2025.xlsx", sheet_name=0, header=5)   # 国立高校卒業者（シート1）
df_rate2 = pd.read_excel("files/都道府県別_卒業後状況_2025.xlsx", sheet_name=1, header=5)   # 公立高校卒業者（シート2）
df_rate3 = pd.read_excel("files/都道府県別_卒業後状況_2025.xlsx", sheet_name=2, header=5)   # 私立高校卒業者（シート3）




# merge するために都道府県を示す項目名を「都道府県」に統一する。
# merge後のデータの扱いやすさのために、使用するデータは項目名を変える。
df_hs = df_hs.rename(columns={'区分.1': '都道府県',
                              '計': '学校数'
                              })

df_uni = df_uni.rename(columns={'区分.1': '都道府県',
                                '計': '学校数'
                                })

for df in [df_rate1, df_rate2, df_rate3]:
    df.rename(columns={'区分': '都道府県',
                       '計': '卒業者数',
                       'A大学等進学者': '大学進学者数'
                       }, 
                       inplace=True)



# 国立・公立・私立の人数を合計して全体進学率を算出
df_rate_total = df_rate1[['都道府県', '卒業者数', '大学進学者数']].copy()

# 国立・公立・私立の卒業者数の合計
df_rate_total['卒業者数'] = (df_rate1['卒業者数'] + df_rate2['卒業者数'] + df_rate3['卒業者数'])
# 国立・公立・私立の大学進学率の合計
df_rate_total['大学進学者数'] = (df_rate1['大学進学者数'] + df_rate2['大学進学者数'] + df_rate3['大学進学者数'])
# 進学率(%) = 大学進学者数 / 卒業者数 * 100
df_rate_total['大学進学率'] = (df_rate_total['大学進学者数'] / df_rate_total['卒業者数'] * 100)



# merge（=学校数と進学率の表を1つにする）
df_hs_merged = pd.merge(df_hs,          # 高校数
                        df_rate_total,        # 進学率
                        on='都道府県',   # 2つのデータで共通の項目名「都道府県」で一致するデータをくっつける
                        how='inner'     # 2つのデータにある県のみを残す
                        )

df_uni_merged = pd.merge(df_uni,        # 大学数
                         df_rate_total,
                         on='都道府県',
                         how='inner'
                         )




# 高等学校数と大学数のどちらのデータを用いるか
df_school = st.radio('条件を選択してください',
                  ['高等学校数', '大学数'])
if df_school == '高等学校数':
    df_school = df_hs_merged
else:
    df_school = df_uni_merged


fig = px.scatter(df_school,
                 x='大学進学率',
                 y='学校数',
                 hover_name='都道府県')
st.plotly_chart(fig)
