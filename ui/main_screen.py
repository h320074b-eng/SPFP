import streamlit as st
import plotly.express as px

from data.stock_data import StockData

class MainScreen:

    # コンストラクタ
    def __init__(self):
        self.stock_data = StockData()

    # 画面表示関数
    def show(self):

        st.title("株価変動予測アプリ")

        ticker = st.text_input(
            "ティッカーシンボル",
            value="7203.T"
        )

        period = st.selectbox(
            "取得期間",
            [
                "1mo",
                "3mo",
                "6mo",
                "1y",
                "2y",
                "5y"
            ],
            index=3
        )

        if st.button("データ取得"):
            with st.spinner("取得中..."):
                df = self.stock_data.load_stock_data(
                    ticker = ticker,
                    period = period
                )
            if df is False:
                st.error("データを取得できませんでした")
                return
            
            st.success("取得完了")

            csv_data = self.stock_data.get_dataframe()
            st.dataframe(csv_data.tail())

            graph_data = csv_data.reset_index()
            fig = px.line(
                graph_data,
                x="Date",
                y="Close",
                title=f"{ticker} 株価推移"
            )
            st.plotly_chart(
                fig,
                use_container_width=True
            )

