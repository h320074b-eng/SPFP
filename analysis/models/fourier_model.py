from analysis.models.base_model import BaseModel
import pandas as pd
import numpy as np

# FFT解析⇒周期抽出⇒未来予測
class FourierModel(BaseModel):

    def train(self, df):
        pass

    def predict(self, df, param):
        # 日数を作る
        x = np.arange(len(df["Close"]))
        # 一次近似
        coef = np.polyfit(
            x,
            df["Close"],
            1
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
                - prediction[len(df)-1]
            )

        return prediction + offset