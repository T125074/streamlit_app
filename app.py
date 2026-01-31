import streamlit as st
import pandas as pd

hs_df = pd.read_excel("files/都道府県別_学校数(高).xlsx")
uni_df = pd.read_excel("files/都道府県別_学校数(大)_2025.xlsx")
rate_df = pd.read_excel("files/都道府県別_卒業後状況_2025.xlsx")

st.write("高校数データ")
st.write(hs_df.head())

st.write("大学数データ")
st.write(uni_df.head())

st.write("進学率データ")
st.write(rate_df.head())
