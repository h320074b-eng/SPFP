import streamlit as st
import pandas as pd

LINK = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"


def mk_syoken_df(url=LINK):
        df = pd.read_excel(url)
        df["コード"] = df["コード"].astype(str)
        return df
    
    
def mk_industry_list(df, selection="17業種区分"):
    industry_list = sorted(df[selection].dropna().unique())
    selected = st.multiselect(
        f"{selection} を選択",
        options=industry_list,
        default=[]
    )
    return selected 
    

if __name__=="__main__":
    st.title("銘柄検索")
    st.write(f"東証上場銘柄一覧")
    st.write(f"({LINK})")
    
    keyword = st.text_input("証券コード・銘柄名で検索")
    
    df_syoken = mk_syoken_df()
    selected_17indust = mk_industry_list(df_syoken, selection="17業種区分")
    selected_33indust = mk_industry_list(df_syoken, selection="33業種区分")
    
    ###-< search >-###
    df_result = df_syoken.copy()
    if keyword:
        df_result = df_result[
            df_result["コード"].str.contains(keyword, case=False, na=False)
            | df_result["銘柄名"].str.contains(keyword, case=False, na=False)
        ]
    if selected_17indust:
        df_result = df_result[
            df_result["17業種区分"].isin(selected_17indust)
        ]
    if selected_33indust:
        df_result = df_result[
            df_result["33業種区分"].isin(selected_33indust)
        ]
    
    st.write(f"{len(df_result)} 件")
    st.dataframe(df_result, use_container_width=True)
    
    st.session_state["df_stocks"] = df_result["コード"].tolist()