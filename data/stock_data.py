import yfinance as yf

class StockData:
    # コンストラクタ
    def __int__(self):
        self.df = None
    
    # 株価データの取得処理
    # デフォルトでは1年分のデータを取得する。
    def load_stock_data(
            self,
            ticker,
            period="1y"
    ):
        self.df = yf.download(
            ticker,
            period=period,
            auto_adjust=True
        )
        if self.df is None:
            return False

        # 不要なヘッダの削除
        self.df = self.df.reset_index().copy()
        self.df.columns = ['Date', "Close", "High", "Low", "Open", "Volume"]
        return True

    # 読み込みデータの取得
    def get_dataframe(self):
        return self.df