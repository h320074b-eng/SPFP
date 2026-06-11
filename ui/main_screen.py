import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from data.stock_data import StockData

class MainScreen:

    # コンストラクタ
    def __init__(self):
        self.stock_data = StockData()

    # 画面表示関数
    def show(self):

        st.title("株価変動予測アプリ")

        ticker = st.text_input(
            "銘柄",
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

        ma_period = st.selectbox(
            "移動平均期間",
            [
            5,
            25,
            50,
            75,
            100,
            200
            ],
            index=1  # 25日を初期値
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

            # 最新の株価5日分
            st.dataframe(csv_data.tail())

            # 株価推移グラフ
            graph_data = csv_data.reset_index()
            fig = px.line(
                graph_data,
                x="Date",
                y="Close",
                title=f"{ticker} 株価推移"
            )

            # ローソク足
            fig.add_trace(
                go.Candlestick(
                    x=graph_data["Date"],
                    open=graph_data["Open"],
                    high=graph_data["High"],
                    low=graph_data["Low"],
                    close=graph_data["Close"],
                    name="株価"
                )
            )

            # 移動平均線
            graph_data[f"MA{ma_period}"] = (
                graph_data["Close"]
                .rolling(window=ma_period)
                .mean()
            )

            fig.add_trace(
                go.Scatter(
                    x=graph_data["Date"],
                    y=graph_data[f"MA{ma_period}"],
                    mode="lines",
                    name=f"MA{ma_period}"
                )
            )
            st.plotly_chart(
                fig,
                use_container_width=True
            )
