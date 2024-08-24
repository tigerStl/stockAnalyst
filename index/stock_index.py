import os

import pandas as pd
import matplotlib.pyplot as plt


class stock_index_calc:
    def macd(self, symbol, hist_data, generate_signal, default_column="close", ema_middle=12, ema_long=26, ema_short=9,
             dividend_data=None):
        '''
        算法：
            1， 计算
            2, 存盘到 symblo_macd.csv 文件

        '''
        date_column_name = 'date'
        df = pd.DataFrame()
        df[date_column_name] = pd.to_datetime(hist_data[date_column_name])
        df['macd_middle'] = None
        df['macd_long'] = None
        df['MACD'] = None
        df['MACD_SINGAL'] = None
        df[default_column] = hist_data[default_column]
        df.set_index(date_column_name, inplace=True)

        df['macd_middle'] = df[default_column].ewm(span=ema_middle, adjust=False).mean()
        df['macd_long'] = df[default_column].ewm(span=ema_long, adjust=False).mean()
        df['MACD'] = df['macd_middle'] - df['macd_long']
        df['MACD_SINGAL'] = df['MACD'].ewm(span=ema_short, adjust=False).mean()

        '''save to file'''
        target_k_file_dir = "E:\\python\\history_data\\days\\index\\macd\\"
        targetFileName = f"{symbol}_macd.csv"
        data_dir = os.path.join(target_k_file_dir, targetFileName)

        history = pd.DataFrame(hist_data)
        history[date_column_name] = pd.to_datetime(history[date_column_name])
        history = history.drop(default_column, axis=1)
        m = pd.merge(df, history, on=date_column_name)

        # 处理dividend 数据
        if dividend_data is not None:
            # 将dividend的发布数据和
            declaration = self.merge_dividend_index(pd_idx=m, pd_dividend=dividend_data,
                                                    column_idx_key="date", column_dividend_key="declarationDate",
                                                    attached_column="amount")
            ex_date = self.merge_dividend_index(pd_idx=m, pd_dividend=dividend_data,
                                                column_idx_key="date", column_dividend_key="exOrEffDate",
                                                attached_column="amount")
            # 合并该两矩阵
            columns = m.columns.tolist()
            m = pd.merge(declaration, ex_date, on="date")
            columns.append("exOrEffDate")
            m = m[[m]]

        m.to_csv(data_dir)
        return m

    def merge_dividend_index(self, pd_idx, pd_dividend, column_idx_key="date", column_dividend_key="date",
                             attached_column="amount"):
        pd_idx[column_idx_key] = pd.to_datetime(pd_idx[column_idx_key])
        pd_dividend[column_dividend_key] = pd.to_datetime(pd_dividend[column_dividend_key])

        # 处理相关的日期的链接
        pd_idx_dividend = pd.merge_asof(pd_idx, pd_dividend, left_on=column_idx_key, right_on=column_dividend_key,
                                        how='left')
        # drop不相干的columns
        c = pd_idx.columns.tolist()
        c.append(column_dividend_key)
        c.append(attached_column)

        return pd_idx_dividend[[c]]
