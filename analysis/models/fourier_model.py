from analysis.models.base_model import BaseModel
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

# FFT解析⇒周期抽出⇒未来予測
class FourierModel(BaseModel):
    TEST_DAYS = 30

    def train(self, df):
        pass

    def predict(self, df, param):
        logger.info("予測開始")
        # 近似の値を取得する
        degree = self._select_best_degree(df)
        logger.info(f"近似に用いる次数:%d", degree)
        # 日数を作る
        x = np.arange(len(df["Close"]))
        # 近似処理
        coef = np.polyfit(
            x,
            df["Close"],
            degree
        )
        # トレンドを取得する
        trend = np.polyval(
            coef,
            x
        )
        # トレンド除去
        signal = df["Close"] - trend
        # 
        fft_result = np.fft.fft(signal)
        fft_result[0] = 0

        # 未来日数分延長
        extended_x = np.arange(
            len(signal) + param["future_days"]
        )
        reconstructed = np.zeros(
            len(extended_x)
        )

        n = len(signal)

        # 上位10成分のみ使用
        top_n = 10

        indexes = np.argsort(
            np.abs(fft_result)
        )[-top_n:]

        for idx in indexes:
            amplitude = (
                np.abs(fft_result[idx])
                / n
            )
            phase = np.angle(
                fft_result[idx]
            )

            frequency = idx / n

            reconstructed += (
                amplitude
                * np.cos(
                    2 * np.pi
                    * frequency
                    * extended_x
                    + phase
                )
            )
        # トレンドを戻す
        extended_trend = np.polyval(
            coef,
            extended_x
        )

        prediction = (
            reconstructed
            + extended_trend
        )

        offset = (
            df["Close"].iloc[-1]
            - prediction[n-1]
        )

        return prediction + offset
    
    # 一次近似と二次近似について過去一か月のデータをテストデータ、それ以前の
    def _select_best_degree(self, df):
        # テストデータ
        train_df = df.iloc[:-self.TEST_DAYS]
        test_df = df.iloc[-self.TEST_DAYS:]

        # 実データ
        actual = test_df["Close"].values

        # 一次近似
        pred_deg1 = self._forcast(
            train_df,
            degree=1
        )
        # 二次近似
        pred_deg2 = self._forcast(
            train_df,
            degree=2
        )
        # 直近30の予測を抜き出す
        pred_deg1 = pred_deg1[-self.TEST_DAYS:]
        pred_deg2 = pred_deg2[-self.TEST_DAYS:]

        # MAE計算
        mae_deg1 = np.mean(
            np.abs(actual - pred_deg1)
        )
        logger.info(f"1次近似によるMAE:%.2f", mae_deg1)
        mae_deg2 = np.mean(
            np.abs(actual - pred_deg2)
        )
        logger.info(f"2次近似によるMAE:%.2f", mae_deg2)
        logger.info(f"平均株価={test_df['Close'].mean():.2f}")

        if mae_deg1 <= mae_deg2:
            return 1
        return 2

    def _forcast(self, train, degree):
        # 現在より30日以前の終値を学習データとして先頭30日分を試験データとする。
        # 近似処理
        train_len = np.arange(len(train["Close"]))
        coef = np.polyfit(
            train_len,
            train["Close"],
            degree
        )

        # トレンドを取得する
        trend = np.polyval(
            coef,
            train_len
        )
        # トレンド除去
        signal = train["Close"] - trend
        # 
        fft_result = np.fft.fft(signal)
        fft_result[0] = 0

        n = len(signal)

        # 予測日数分延長
        extended_x = np.arange(
            len(signal) + self.TEST_DAYS
        )
        reconstructed = np.zeros(
            len(extended_x)
        )

        # 上位10成分のみ使用
        top_n = 10

        indexes = np.argsort(
            np.abs(fft_result)
        )[-top_n:]

        for idx in indexes:
            amplitude = (
                np.abs(fft_result[idx])
                / n
            )
            phase = np.angle(
                fft_result[idx]
            )

            frequency = idx / n

            reconstructed += (
                amplitude
                * np.cos(
                    2 * np.pi
                    * frequency
                    * extended_x
                    + phase
                )
            )
        # トレンドを戻す
        extended_trend = np.polyval(
            coef,
            extended_x
        )

        prediction = (
            reconstructed
            + extended_trend
        )

        offset = (
            train["Close"].iloc[-1]
            - prediction[n-1]
        )

        return prediction + offset