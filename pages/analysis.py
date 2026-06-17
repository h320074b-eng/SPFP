from datetime import date, timedelta
import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.express as px
import re

def set_stocks():
    default_stock_code = st.session_state.get("df_stocks", [])
    use_default = st.checkbox(
    "銘柄検索ページの結果を利用",
    value=True
)


if __name__=="__main__":
    st.title("株価分析")
    
    ###-< 銘柄コードの受付 >-###
    st.subheader("解析対象銘柄")
    default_codes = st.session_state.get("df_stocks", [])
    default_codes = [str(code) for code in default_codes]
    use_default = st.checkbox(
        "銘柄検索の結果を利用する",
        value = True
    )
    
    manual_codes_text = st.text_area(
        "追加・手入力する証券コード",
        placeholder=""
    )
    manual_codes = [
        code.strip()
        for code in re.split(r"[\s,、]+", manual_codes_text)
        if code.strip()
    ]
    
    if use_default:
        target_codes = default_codes + manual_codes
    else:
        target_codes = manual_codes
    target_codes = sorted(set(target_codes))
    
    st.write(f"解析対象: {len(target_codes)} 件")
    st.write(target_codes)
    
    
    ###-< 対象期間の受付 >-###
    st.subheader("解析対象 期間")
    today = date.today()

    period_type = st.radio(
        "期間",
        ["短期", "中期", "長期"],
        index=1,  # デフォルトは中期
        horizontal=True,
        captions=[
            "過去7日",
            "過去30日",
            "過去365日"
        ]
    )

    if period_type == "短期":
        dt = 7
        d_min = today - timedelta(days=dt * 5)
    elif period_type == "中期":
        dt = 30
        d_min = today - timedelta(days=dt * 10)
    else:
        dt = 365
        d_min = today - timedelta(days=dt * 3)

    start, end = st.slider(
        "取得期間を調整",
        min_value=today - timedelta(days=dt * 10),
        max_value=today,
        value=(today - timedelta(days=dt), today),
        format="YYYY-MM-DD"
    )

    start = pd.to_datetime(start)
    end = pd.to_datetime(end)
    
    
    ###-< データの取得 >-###
    st.subheader("株価データ")
    if st.button("株価データを取得"):
        if len(target_codes) == 0:
            st.warning("証券コードを入力してください")
            st.stop()

        close_df = pd.DataFrame()

        for code in target_codes:
            symbol = f"{code}.T"

            try:
                df_price = yf.download(
                    symbol,
                    start=start,
                    end=end
                )

                df_price = df_price.sort_index()

                close_df[code] = df_price["Close"]

            except Exception as e:
                st.warning(f"{code} の取得に失敗しました orz..")
                st.write(e)

        if len(close_df.columns) > 0:
            #st.dataframe(close_df, use_container_width=True)

            st.write("終値チャート")

            fig = px.line(
                close_df,
                x=close_df.index,
                y=close_df.columns,
                labels={
                    "index": "Date",
                    "value": "Close",
                    "variable": "Code"
                },
                title="終値チャート"
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.error("株価データを取得できませんでした orz..")