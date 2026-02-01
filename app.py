import streamlit as st
st.set_page_config(layout='wide')   # ページをワイド表示に設定（デフォルトは狭い）

import pandas as pd
import plotly.express as px



# ====== データの読み込み ====================
# sheet_name: エクセルファイルから読み込むシートを指定（デフォルトはシート1）
# header: 項目列を指定

# 高等学校数データ（シート1: 本校＋分校の合計を使用）
df_hs = pd.read_excel('files/都道府県別_学校数(高).xlsx', header=5)

# 大学数データ
df_uni = pd.read_excel('files/都道府県別_学校数(大)_2025.xlsx', header=5)

# 大学進学率データ（国立・公立・私立高校）
df_rate1 = pd.read_excel('files/都道府県別_卒業後状況_2025.xlsx', sheet_name=0, header=5)   # 国立高校卒業者（シート1）
df_rate2 = pd.read_excel('files/都道府県別_卒業後状況_2025.xlsx', sheet_name=1, header=5)   # 公立高校卒業者（シート2）
df_rate3 = pd.read_excel('files/都道府県別_卒業後状況_2025.xlsx', sheet_name=2, header=5)   # 私立高校卒業者（シート3）



# ===== データ整形 ====================
# 都道府県名の列の列名を「都道府県」に統一する（あとで merge する際に必要）
df_hs = df_hs.rename(columns={'区分.1': '都道府県', '計': '学校数'})
df_uni = df_uni.rename(columns={'区分.1': '都道府県', '計': '学校数'})

# 3つの大学進学率データ（df_rate1, df_rate2, df_rate3）を仮のリスト df としてまとめ、同じ前処理をループで適用する
for df in [df_rate1, df_rate2, df_rate3]:
    df.rename(columns={'区分': '都道府県','計': '卒業者数','A大学等進学者': '大学進学者数'},    # 変更が df に入った状態
              inplace=True      # df_rate1, df_rate2, df_rate3 に変更を反映する
              )



# ===== 大学進学率の計算 ====================
# 国立・公立・私立高校の卒業者数・進学者数を合計
# 3つの表（df_rate1, df_rate2, df_rate3）が同じ構成だから、df_rate1 をベースとしてコピーし（=枠組みの設定）、国公私の合計値を上書きして総計を作成
df_rate_total = df_rate1[['都道府県', '卒業者数', '大学進学者数']].copy()
df_rate_total['卒業者数'] = (df_rate1['卒業者数'] + df_rate2['卒業者数'] + df_rate3['卒業者数'])
df_rate_total['大学進学者数'] = (df_rate1['大学進学者数'] + df_rate2['大学進学者数'] + df_rate3['大学進学者数'])

# 進学率(%) = 大学進学者数 / 卒業者数 * 100
df_rate_total['大学進学率'] = (df_rate_total['大学進学者数'] / df_rate_total['卒業者数'] * 100)



# ===== 学校数データと進学率データを結合 ====================
# pd.merge: 共通のキー列（今回は「都道府県」）で2つのデータフレームを結合する関数
df_hs_merged = pd.merge(df_hs,              # 高校数
                        df_rate_total,      # 進学率
                        on='都道府県',       # 共通の項目名「都道府県」のデータを結合する
                        how='inner'         # 両方のデータにある都道府県だけ残す
                        )
df_uni_merged = pd.merge(df_uni,            # 大学数
                         df_rate_total,
                         on='都道府県',
                         how='inner'
                         )



# ===== タイトル・概要・目的 ====================
st.title('🏫 学校数と大学進学率の関係を見てみよう')
st.divider()        # 未使用UI(1)：区切り線

st.subheader('📌 アプリについて')
st.markdown('''
            このアプリでは、都道府県ごとの**高校や大学の数**と**大学進学率**のデータを使って、「学校の数と進学率は関係あるのか？」を簡単にチェックできます。
            グラフやランキングで、直感的に県ごとの違いを比べてみましょう。
            ''')

st.subheader('🎯 目的')
st.markdown('''
            - 学校数が多い県は進学率が高いのか調べる
            - データを見ながら傾向をつかむ
            - 「学校数が少ないけど進学率が高い県」など、意外な特徴を発見する
            ''')
st.divider()



# ===== 使い方 ====================
with st.popover('⚒️ 使い方'):       # 未使用UI(2)：開閉可能なコンテナを挿入
    st.markdown('''
               **① 学校の種類を選ぶ**  
                - 左側のラジオボタンで「高等学校数」または「大学数」を選択  
                - データ表やグラフも自動で切り替わる

                **② 散布図で関係を確認**  
                - 横軸：学校数、縦軸：大学進学率    
                - 各都道府県のデータをホバーすると数値を確認可能  
                - 学校数と進学率の間の傾向やばらつきを確認

                **③ ランキングで特徴的な県を見る**  
                - 上位／下位を選択して、棒グラフで表示  
                - スライドバーで表示する都道府県数を指定
                - (学校の種類は①で選択したデータを使用)
                - 棒の色やラベルで1位やワーストがすぐわかる
                ''')



# ===== タブ1: 散布図 ====================
tab1, tab2 = st.tabs(['学校数と進学率', '進学率ランキング'])     # 未使用UI(3)：タブを作成

with tab1:
    col1_left, col1_right = st.columns([1, 2])      # 条件選択と結果表示をカラムに分ける

    # 左カラム（条件選択）
    with col1_left:
        st.subheader('条件選択')
        
        # 高校か大学か選択（ラジオボタン）
        school_type = st.radio('データの選択',
                               ['高等学校数', '大学数'])
        
        if school_type == '高等学校数':
            df_school = df_hs_merged        # 高校数と進学率の結合ファイルを、グラフ用データファイルに設定
            st.caption('※ 高等学校数は本校＋分校の合計です')    # 未使用UI(4)：注釈を追記
        else:
            df_school = df_uni_merged       # 大学数と進学率の結合ファイルを、グラフ用データファイルに設定
            st.caption('※ 大学数は都道府県内の大学設置数です')
        
        # データ表を表示するかどうか（チェックボックス）
        show_data = st.checkbox('データ表を表示する')
        if show_data:
            st.dataframe(df_school[['都道府県', '学校数', '大学進学率']],
                         height=200,         # データフレームの表示エリアの高さを指定（表示範囲200pxで内部スクロール可能に）
                         hide_index=True     # インデックス（行番号）を隠す
                         )
            
    # 右カラム（結果表示）
    with col1_right:
        st.subheader(f'📉{school_type}と大学進学率の関係')
        fig_scatter = px.scatter(df_school,
                                 x='学校数',
                                 y='大学進学率',
                                 hover_name='都道府県',     # ホバーの見出しに都道府県名を表示
                                 width=500,
                                 labels={'学校数': f'{school_type}（校）', '大学進学率': '大学進学率（％）'}
                                 )
        st.plotly_chart(fig_scatter)



# ===== タブ2: ランキング ====================
with tab2:
    col2_left, col2_right = st.columns([1, 2])

    # 左カラム（条件選択）
    with col2_left:
        st.subheader('条件選択')
        st.write(f'学校数データ: 「{school_type}」を選択中')
        st.caption('学校数データの種類を変更したい方は[学校数と進学率]より選択してください')

        # 上位か下位か選択（ラジオボタン）
        rank_type = st.radio('ランキングの種類',
                             ['上位', '下位'])
        
        # 表示する県数を指定（スライドバー）
        top_n = st.slider(label='表示する都道府県の数',
                          min_value=5,
                          max_value=20,
                          value=10)
        
        # データを大学進学率でソートして抽出し、グラフ用データファイルに設定
        if rank_type == '上位':
            df_rank = df_school.sort_values(by='大学進学率',     # df_school を「大学進学率」の順で並び替え
                                            ascending=False     # 大きい順（上位）
                                            ).head(top_n)       # 並び替えた上位 top_n 個だけ抽出
        else:
            df_rank = df_school.sort_values(by='大学進学率',
                                            ascending=True      # 小さい順（下位）
                                            ).head(top_n)
            
        # 行番号をresetして順位列作成
        df_rank = df_rank.reset_index(drop=True)  # 元の行番号をリセット。drop=True で元のインデックス列を削除
        df_rank['順位'] = [f'{i}位' for i in df_rank.index + 1]     # 新しい列「順位」を作成
            
        # データ表を表示するかどうか（チェックボックス）
        show_data_rank = st.checkbox('ランキング表を表示する')
        if show_data_rank:
            st.dataframe(df_rank[['順位', '都道府県', '学校数', '大学進学率']],
                         height=200,         # データフレームの表示エリアの高さを指定（表示範囲200pxで内部スクロール可能に）
                         hide_index=True     # インデックス（行番号）を隠す
                         )
   
    # 右カラム（結果表示）
    with col2_right:
        st.subheader('🏆大学進学率ランキング')
        st.write('本ランキングは大学進学率の高い順（または低い順）に都道府県を並べ、その県における学校数を棒の長さで示しています。')
        
        # 1位／ワースト1位を色分け
        df_rank['color'] = '2位以降'
        if rank_type == '上位':
            df_rank.loc[0, 'color'] = '🏅1位'
        else:
            df_rank.loc[0, 'color'] = '💀ワースト1位'

        fig_bar = px.bar(df_rank,
                         x='都道府県',
                         y='学校数',
                         text=df_rank['順位'],  # 各都道府県ごとにラベルとして「順位」列の値を表示
                         color='color',
                         color_discrete_map={'2位以降': 'lightblue', '🏅1位': 'red', '💀ワースト1位': 'blue'},
                         hover_name='都道府県',
                         hover_data={'都道府県': False, 'color': False, '大学進学率': True, '学校数': True, '順位': False},     # ホバーに表示するデータを指定（表示：True、非表示：False）
                         title=(f'【{rank_type}{top_n}位を表示】'),
                         labels={'都道府県': '', '学校数': f'{school_type}（校）'}
                         )
        st.plotly_chart(fig_bar)
        st.caption('※ 棒グラフ上の数値は大学進学率の順位を表します')
st.divider()



# ===== データ情報 ====================
st.subheader('🔍 データについて')
st.markdown('''
            - 高等学校数・大学数データ：e-Stat「学校基本調査」より取得（2026年1月31日）
            - 大学進学率データ：同上（大学進学率は、国立・公立・私立高校の卒業者数・大学進学者数を合計して算出）
            - データの単位：学校数（校）、人数（人）、進学率（％）
            ''')
st.divider()



# ===== 可視化結果の考察 ====================
st.subheader('💡可視化結果の考察')
st.markdown(''' 
            散布図やランキングを見てみると、いくつか面白い傾向が見えてきます。
            
            - 全体的には、学校数が多い県ほど大学進学率がやや高め、という傾向がみられます（弱い相関）。
            - 例外もあって、東京都は学校数も進学率もダントツで、学校数だけで進学率を語るのは難しそうです。
            ちなみに学校数は、同程度の進学率を誇る京都の約3～4倍です。
            - 北海道は高等学校数は東京に次いで2位、大学数も4位ですが、進学率は下から15位と低めです。 
            このことから、進学率には学校数だけでなく、地域の教育環境や家庭環境など他の要因も関わっていることが考えられます。

            📝まとめ
            - 学校数が多いと進学率が高めの傾向はある  
            - でも東京都や北海道のように「学校数と進学率の関係だけでは説明できない県」もある  
            - 進学率には学校数以外の要素も影響している可能性が高い
            ''')