import datetime
import os
import time
import traceback
import nasdaqdatalink
import numpy as np
import requests
import pandas as pd
import json
import sys
import math
import inspect

from index.stock_index import stock_index_calc

sys.path.append("..")
import yahoo.PyStockDividend as yahoo
import system.fin_Utility as utility

'''
Note: 
    The site is blocking requests from python. Refer to explanation.
'''


class HistoryDataArgs:
    k_line_type = "day"
    k_line_number = 1000
    ''' 默认三年数据'''

    def __init__(self, args):
        if len(args) == 0:
            return
        if len(args) >= 1:
            self.k_line_type = args[0]
            if len(args) >= 2:
                try:
                    self.k_line_number = int(args[1])
                except Exception as e:
                    print(f"无法将|{args[1]}|转换为整数");
                    self.k_line_number = 1000
        return


class NasdaqFStockDivindent:
    default_data_dir = "../data"
    dividend_plan_file = "symbolsHasDividendPlan.csv"
    dividend_full_vision_fle = "nasdq_full_vision.csv"
    dividend_plan_df = None

    all_api_invoked = 0

    def print_stacktrace(self, exception):
        stacktrace = exception.__traceback__

        for frame in inspect.getinnerframes(stacktrace):
            filename = frame.filename
            lineno = frame.lineno
            function = frame.function
            code_context = frame.code_context
            code_context = code_context[0].strip() if code_context else "No code context"
            print(f"File \"{filename}\", line {lineno}, in {function}")
            print(f"  {code_context}")


    def loadDividentDataFromCsv(self):
        self.default_data_dir

    def get_stock_divident(self):
        symbol_file = os.path.join(self.default_data_dir, self.dividend_plan_file)
        print(f"try to read {symbol_file}")
        self.dividend_plan_df = pd.read_csv(symbol_file)
        return self.dividend_plan_df

    def get_stock_info(self, symbol):
        urls = ["stocks", "etf", "equity"]
        url = f"https://api.nasdaq.com/api/quote/{symbol}/summary?assetclass=stocks"
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        }
        current_json = ""
        try:
            is_find = False
            current_type = ""
            for u in urls:
                url = f"https://api.nasdaq.com/api/quote/{symbol}/summary?assetclass={u}"
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    current_json = data
                else:
                    continue
                if 'status' in data and 'rCode' in data['status'] and data['status']['rCode'] == 200:
                    is_find = True
                    current_type = u
                    break
            if not is_find:
                return None
            rslt = {'symbol': symbol, 'price': 0, 'industry': None, 'dividend_yield_Rate': 0, 'type': current_type}
            if 'data' in data and 'summaryData' in data['data'] \
                    and 'Industry' in data['data']['summaryData']:
                rslt['industry'] = data['data']['summaryData']['Industry']['value']
                rslt['price'] = data['data']['summaryData']['PreviousClose']['value']
                rslt['dividend_Ex_Date'] = data['data']['summaryData']['ExDividendDate']['value']
                rslt['dividend_yield_Rate'] = data['data']['summaryData']['Yield']['value']
                rslt['indicated_Annual_Dividend'] = data['data']['summaryData']['AnnualizedDividend']['value']
                if 'announcement_Date' in data['data']['summaryData']:
                    rslt['announcement_Date'] = data['data']['summaryData']['announcement_Date']['value']
                if 'Yield' in data['data']['summaryData']:
                    rslt['dividend_yield_Rate'] = data['data']['summaryData']['Yield']['value']
                '''修正比率'''
                yield_value = utility.fin_Utilities.convert_string_float(data['data']['summaryData']['Yield']['value'])
                if not math.isnan(yield_value):
                    try:
                        d = utility.fin_Utilities.convert_string_float(
                            data['data']['summaryData']['PreviousClose']['value'])
                        f = utility.fin_Utilities.convert_string_float(
                            data['data']['summaryData']['AnnualizedDividend']['value'])
                        v = f / d
                        rslt['dividend_yield_Rate'] = v
                    except Exception as ex:
                        print(f"get_stock_info|Error: {ex}")
                return rslt
            return None
        except Exception as e:
            print(f"Log:Error: {e}|source|{current_json}")
            return None

    def get_calendar_dividends(self, tmpDate):
        url = f"https://api.nasdaq.com/api/calendar/dividends?date={tmpDate}"
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'calendar' in data['data']:
                    dividends_data = data['data']['calendar']['rows']
                    # Extract relevant information into a Pandas DataFrame
                    # non_dividends_data = pd.Series(dividends_data)
                    # dividends_df = pd.DataFrame(**dividends_data, **non_dividends_data.to_dict())
                    dividends_df = pd.DataFrame(dividends_data)

                    # Display the DataFrame
                    print(dividends_df)

                    data_dir = os.path.join("..\\data\\", f'nasdaq_dividends_{tmpDate}.csv')
                    # Optionally, you can save the DataFrame to a CSV file
                    dividends_df.to_csv(data_dir, index=False)
                    return dividends_df
                else:
                    print("No dividends information found for the specified date.")
                    return None
            else:
                print(f"Error: Failed to fetch data. Status Code: {response.status_code}")
                return None
        except Exception as e:
            print(f"get_calendar_dividends|Error:|{tmpDate}|{url}|\r\n{e}|{e.__traceback__}\r\nException done")
            self.print_stacktrace(e)
            traceback.print_exc()
            return None

    def getBusinessDaysInFuture(self, period, startDate=pd.Timestamp.today()):
        today = startDate.normalize()
        return pd.date_range(start=today, periods=period, freq='B').strftime('%Y-%m-%d')

    def getLatestData(self, period):
        days = self.getBusinessDaysInFuture(period)

        for day in days:
            print(f"going to get data|{day}|")
            # get all calendar info
            df_divident_day = self.get_calendar_dividends(day)
            # loop and fetch data from nasdaq

    def getAheadDate(self, dt, delta, fmt='%Y-%m-%d'):
        d = dt - datetime.datetime.timedelt(days=delta)
        # 转换格式
        return datetime.datetime.strftime(d, fmt)

    def getDividend_full_vision(self, default_PreviewDate, startDate=pd.Timestamp.today(),
                                start_date_str=None,
                                targetFileName="nasdq_full_vision.csv"):
        if start_date_str:
            try:
                startDate = pd.to_datetime(start_date_str, format='%Y-%m-%d')
            except Exception as e:
                print(e)
        days = self.getBusinessDaysInFuture(default_PreviewDate, startDate)
        date_fmt = datetime.datetime.strftime(startDate, '%Y%m%d')
        targetFileName = f"nasdq_full_vision_{date_fmt}.csv"
        print(f"will fetch dates:{days}")
        # get data via loop and save to //tempData
        '''算法：
        1， 获得指定时间段的分红信息（从nasdaq）
        2， 将返回的dataframe，merge到 symbolsHasDividendPlan.csv 中
        3， 如果symbolsHasDividendPlan没有
        '''
        oneRowSumData = {}
        invoke_times = 0
        data_dir = os.path.join("..\\data\\dividends\\", targetFileName)
        dividend_full_vision = pd.DataFrame(
            columns=["Symbol", "type", "last_check_time", "last_price", "dividend_Ex_Date", "dividend_yield_Rate",
                     "record_Date", "announcement_Date", "indicated_Annual_Dividend", "industry", "payment_Date",
                     "dividend"])
        k_start_date = datetime.datetime.now()
        for oneday in days:
            # 是否是周末
            if pd.to_datetime(oneday).weekday() >= 5:
                continue
            dividend_plan = self.get_calendar_dividends(oneday)
            if dividend_plan is None:
                print(f"{oneday} is none, continue")
                continue
            for index, row in dividend_plan.iterrows():
                symbol = row['symbol']
                try:
                    announcement_Date = datetime.datetime.strptime(row['announcement_Date'], '%m/%d/%Y')
                except Exception as e:
                    print(f"Error, can't convert date|{row['announcement_Date']}|{e}")
                    continue
                '''
                # 日线数据
                announcement_Date_10 = self.getAheadDate(announcement_Date, 10)
                dividend_Ex_Date = datetime.datetime.strptime(row['dividend_Ex_Date'], '%m/%d/%Y')
                dividend_Ex_Date_10 = self.getAheadDate(dividend_Ex_Date, -11)
                # 10天前 （2周），以及除权后的10天数据
                # 获得日线数据
                df_k_day = self.get_kLine(symbol, announcement_Date_10, dividend_Ex_Date_10)
                if df_k_day is not None:
                    #需要处理的数据， 1，前10个K线分成两份，计算最大值和
                    print(df_k_day)
                '''
                stock_info = self.get_stock_info(symbol)
                if stock_info is None:
                    continue
                oneRowSumData['Symbol'] = symbol
                oneRowSumData['type'] = stock_info['type']
                oneRowSumData['last_check_time'] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                oneRowSumData['dividend_Ex_Date'] = row['dividend_Ex_Date']
                oneRowSumData['announcement_Date'] = row['announcement_Date']

                oneRowSumData['indicated_Annual_Dividend'] = row['indicated_Annual_Dividend']
                if stock_info is not None:
                    oneRowSumData['last_price'] = stock_info['price']
                    oneRowSumData['industry'] = stock_info['industry']
                    oneRowSumData['dividend_yield_Rate'] = stock_info['dividend_yield_Rate']
                    if 'announcement_Date' in stock_info:
                        oneRowSumData['announcement_Date'] = stock_info['announcement_Date']
                # append to full_vision table
                # new_row = pd.Series(oneRowSumData, name=len(dividend_full_vision))
                dividend_full_vision.loc[len(dividend_full_vision)] = oneRowSumData
                # dividend_full_vision = dividend_full_vision.append(new_row, ignore_index=True)
                # dividend_full_vision = pd.concat([dividend_full_vision, new_row], ignore_index=True)
                # dividend_full_vision = pd.concat([dividend_full_vision, oneRowSumData], ignore_index=True)
                # dividend_full_vision.append(oneRowSumData, ignore_index=True)
                invoke_times = invoke_times + 1
                print(f"#{invoke_times}|{symbol}|{oneRowSumData}")

                # 获得日线，存贮
                #self.get_k_line(symbol, )
                # 计算macd，
                # 将declarationDate和exDate，close，macd结合起来，成交笔数--如果笔数很好一般不予考虑

                if invoke_times > 50:
                    invoke_times = 0
                    print(f"nasdaq apis are invoked over 50 times||{invoke_times}, sleep ")
                    dividend_full_vision.to_csv(data_dir, mode='a', header=True, index=False)
                    # 需要clean数据，否则会持续将现有数据重复添加
                    dividend_full_vision = pd.DataFrame(columns=dividend_full_vision.columns)
                    time.sleep(50)
                else:
                    time.sleep(1)
        dividend_full_vision.to_csv(data_dir, header=True)
        return dividend_full_vision

    '''
        args 格式： day 1000
        其中day 可以为 60min, hour, 30min
        1000 是距今多少天
    '''
    def get_k_line_by_args(self, args):
        k_history_info = HistoryDataArgs(args)
        target_k_file_dir = "E:\\python\\history_data"
        '''
            算法：
            1，打开最新的dividend文件
            2，获得股息文件的symbol
            3，循环获取K线数据，存盘到外挂硬盘        
        '''
        file_name = os.path.join("..\\data\\historyData", f'nasdq_full_vision.csv')
        if not os.path.exists(file_name):
            print(f"不存在该文件|{file_name}|，该文件是最新的dividends\\nasdq_full_vision下的最新文件。\r\n将该文件paste到history_data目录，改名即可")
            return False
        pd_full_vision = pd.read_csv(file_name)
        '''get date'''
        current_date = datetime.datetime.now()
        date_days_ago = current_date - datetime.timedelta(k_history_info.k_line_number)
        from_date = date_days_ago.strftime("%Y-%m-%d")
        to_date = current_date.strftime("%Y-%m-%d")
        i_count = 0
        i_total_count = 0
        for symbol in pd_full_vision['Symbol'].unique():
            print(f"获取K线数据|{symbol}|")
            i_total_count += 1

            if i_total_count > 50:
                print(f"已经处理了|{i_total_count}|个，休息一下")
                i_total_count = 0
                time.sleep(10)

            try:
                k = self.get_k_line_and_normalization(symbol, from_date, to_date, target_k_file_dir, k_history_info.k_line_number)
                if k is None:
                    continue
                # 获得该商品的dividend 历史记录
                dividend = self.get_dividend_by_symbol(symbol)
                if dividend is None:
                    continue
                # 生成macd文件
                index = stock_index_calc()
                macd = index.macd(symbol, k, True, 'close', dividend_data=dividend)
                i_count += 1
            except Exception as e:
                print(f"|{symbol}|get history data|Error: {e}")
                continue
        print(f"get {i_count}|history files")
        return True

    def get_k_line_and_normalization(self, symbol, from_date, to_date, target_k_file_dir, count=1000):
        k = self.get_k_line(symbol, from_date, to_date, count)
        if k is None:
            return None
        target_file_name = os.path.join(target_k_file_dir, f"days\\{symbol}.csv")
        k['close'] = pd.to_numeric(k['close'].str.replace('$', ''), errors='coerce')
        k['open'] = pd.to_numeric(k['open'].str.replace('$', ''), errors='coerce')
        k['high'] = pd.to_numeric(k['high'].str.replace('$', ''), errors='coerce')
        k['low'] = pd.to_numeric(k['low'].str.replace('$', ''), errors='coerce')
        k.to_csv(target_file_name)
        return k

    '''
    获得日线数据
    from_date format: yyyymmdd
    '''
    def get_k_line(self, symbol, from_date, to_date, count=100):
        print(f"获得日线：{symbol}|{from_date}|{to_date}|{count}")
        url = f"https://api.nasdaq.com/api/quote/{symbol}/historical?assetclass=stocks&fromdate={from_date}&limit={count}&todate={to_date}"
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
            df_history = None
            if 'data' in data and 'tradesTable' in data['data'] and 'rows' in data['data']['tradesTable']:
                df_history = pd.DataFrame(data['data']['tradesTable']['rows'])
                return df_history
            else:
                return None
        except Exception as e:
            print(f"get_k_line|Error: {e}")
            return None

    '''
    get s&p's symbols
    '''

    def get_SAndPSymbol(self):
        data_dir = '..\\data\\'
        pth = os.path.join(data_dir, 'SAndP.csv')
        df_SAndP_Symbol = pd.read_csv(pth, header=True)
        return df_SAndP_Symbol

    def getSAndPDivident_full_vision(self):
        try:
            '''算法：
            1， 获得所有s&p的代码， 从csv文件中
            2， 循环获取股票的summary            
            '''
            symbols = self.get_SAndPSymbol()
            target_pd = None
            iLoopCnt = 0
            for symbol in symbols['Symbol']:
                print(f"going to get s&p symbol|{symbol}|")
                # get stock info
                stock_info = self.get_stock_info(symbol)
                if target_pd is None:
                    target_pd = stock_info
                else:  # merge result
                    target_pd = pd.concat([target_pd, stock_info], ignore_index=True)
                if iLoopCnt >= 50:
                    time.sleep(20)
                else:
                    time.sleep(2)
            print(f"have done all s and p stocks |{len(target_pd)}|Rows, begin to merge to target")
            # read file
            target_file_name = os.path.join(self.default_data_dir, self.dividend_full_vision_fle)
            df_full_vision = pd.read_csv(target_file_name)
            merged_df = pd.merge(target_pd, df_full_vision, on='symbol', how='outer', suffixes=('_new', '_old'))
            df_full_vision.update(merged_df[["last_price_new", "dividend_Ex_Date_new", "dividend_yield_Rate_new",
                                             "industry_new"]].rename(columns={"last_price": "last_price_new",
                                                                              "dividend_Ex_Date": "dividend_Ex_Date_new",
                                                                              "dividend_yield_Rate": "dividend_yield_Rate_new",
                                                                              "industry": "industry_new"}))
            df_full_vision = df_full_vision.append(merged_df.loc[merged_df['symbol'].isin(target_pd['symbol'])
                                                                 & merged_df['symbol'].isna(),
                                                                 ['symbol', '']])
            df_full_vision.to_csv(target_file_name)
            return target_pd
        except Exception as e:
            print(f"getSAndPDivident_full_vision|Error: {e}")
        return None

    def convertCurrencyToFloat(self, currencyStr):
        if pd.notna(currencyStr):
            if "(" in currencyStr:
                return currencyStr.replace("($", "-").replace(")", "")
            else:
                return currencyStr.replace("$", "").replace(")", "")
        else:
            return currencyStr

    def getEarningTablesByStartDate(self, startDate, period, saveToCSVDirectly=True):
        timestamp = pd.to_datetime(startDate, format='%Y-%m-%d')
        days = self.getBusinessDaysInFuture(period, timestamp)
        df = None
        total_df = None
        for d in days:
            df = self.getEarningTable(d, isWithDividend=True)
            print(f"have saved {d} earning file")
            time.sleep(1)
            if total_df is None:
                total_df = df
            else:
                total_df = total_df._append(df, ignore_index=True)
        total_df = total_df.drop(columns=['dividend_yield_Rate_x', 'dividend_x'])
        file_name = os.path.join("..\\data\\earningTable", f'earnings_dividend_{startDate}_{period}.csv')
        total_df.to_csv(file_name)
        return total_df

    '''
    该方法先获得指定时间段的日历表，
    然后从dividend 链接中获得最新的数据，
      最近一年的分红次数，平均值，最后一次股息-通过平均值和股息的对比可以知道公司是上升还是下降，
      去年eps--》说明该公司是否盈利，不盈利的公司不要，最新价
    第一阶段，从这个表中获取下阶段的股息，以确定是否存在购买机会
    
    '''

    def getEarningTable(self, str_date, saveToCSVDirectly=True, isWithDividend=False):
        # https://api.nasdaq.com/api/calendar/earnings?date=2023-11-29
        print(f"getEarningTable begin|{str_date}")
        url = f"https://api.nasdaq.com/api/calendar/earnings?date={str_date}"
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
            rslt = {'symbol': "", 'fiscalQuarterEnding': "", 'industry': None, 'lastYearEPS': 0,
                    'dividend_yield_Rate': 0, 'declare_date': None}
            rslt_df = pd.DataFrame(rslt, index=[0])
            df_divident = None
            '''這裏有兩種模式
            如果是历史模式，即年报数据已经公布，将显示 eps，否知没有该项
            从一般理解来看，高的eps同时比预估“epsForecast”将预示更大的机会
            因此应该在每天收市后运行该程序获得最新的投资机会
            '''
            if 'data' in data and 'rows' in data['data']:
                allRows = pd.DataFrame(data['data']['rows'])
                allRows['industry'] = ''
                allRows['dividend_yield_Rate'] = ''
                allRows['declare_date'] = str_date
                allRows['dividend'] = np.NAN
                '''过滤所有的eps 或者epsForecast 为负数的'''
                # allRows_new = allRows[(allRows['eps'].apply(lambda x: x[1:] if pd.notna(x) and '(' in x else
                # x).astype(float) >= 0) & (allRows['epsForecast'].apply(lambda x: x[1:] if pd.notna(x) and '(' in x
                # else x).astype(float) >= 0)]
                if 'eps' in allRows.columns:
                    allRows['epsFix'] = allRows['eps'].apply(
                        lambda x: x.replace("($", "-").replace(")", "") if pd.notna(x) and '(' in x else x.replace("$",
                                                                                                                   "").replace(
                            ")", ""))
                else:
                    allRows['epsFix'] = '0'

                allRows['epsForecastFix'] = allRows['epsForecast'].apply(
                    lambda x: x.replace("($", "-").replace(")", "") if pd.notna(x) and '(' in x else x.replace("$",
                                                                                                               "").replace(
                        ")", ""))
                # 过滤小于0 的
                allRows = allRows[allRows['epsFix'].apply(
                    lambda x: float(x) if x.replace('.', '', 1).lstrip('-').isdigit() else None).ge(0)]
                if isWithDividend:
                    for index, oneRow in allRows.iterrows():
                        '''获得dividend 信息'''
                        print(f"将获得股息|{oneRow['symbol']}|")
                        dividend = self.get_dividend_by_symbol(oneRow['symbol'])
                        if dividend is not None:
                            print(f"获得股息数据|{oneRow['symbol']}|")
                            dividend['symbol'] = oneRow['symbol']
                            '''将该列数据附加在该行'''
                            if df_divident is None:
                                df_divident = pd.DataFrame(dividend)
                            else:
                                '''添加到df_dividend'''
                                # df_divident = df_divident.append(dividend, ignore_index=True)
                                df_divident = df_divident._append(dividend, ignore_index=True)
                        time.sleep(1)
                        '''获得股票的基本信息'''
                        print(f"将获得股票基本信息|{oneRow['symbol']}|")
                        df_summary = self.get_stock_info(oneRow['symbol'])
                        df_divident['dividend_yield_Rate'] = df_summary['dividend_yield_Rate']
                        df_divident['price'] = df_summary['price']
                        df_divident['industry'] = df_summary['industry']

                print("合并两个df")
                if df_divident is None:
                    merged_dividend_earning = allRows
                else:
                    merged_dividend_earning = pd.merge(allRows, df_divident, on='symbol', how='left')
                print(merged_dividend_earning.info)
                if saveToCSVDirectly:
                    fileName = os.path.join("..\\data\\earningTable", f'nasdaq_earnings_dividend_{str_date}.csv')
                    allRows.to_csv(fileName, header=True)
                    # return                                                                                                                            
                return merged_dividend_earning
        except Exception as e:
            print(f"Error of getEarningTable|{e}")
            traceback.print_exc()
            return None

    '''获得某只股票的股息历史记录
    sample： https://api.nasdaq.com/api/quote/JCI/dividends?assetclass=stocks
                {
                    "exOrEffDate": "06/27/1997",
                    "type": "Cash",
                    "amount": "$0.05",
                    "declarationDate": "06/11/1997",
                    "recordDate": "07/01/1997",
                    "paymentDate": "08/01/1997",
                    "currency": "USD"
                }
    '''

    def get_dividend_by_symbol(self, symbol, save_to_csv_directly=True, rows=1, save_yield=0.05):
        #  https://api.nasdaq.com/api/quote/JCI/dividends?assetclass=stocks
        print(f"get_dividend_by_symbol begin|{symbol}")
        url = f"https://api.nasdaq.com/api/quote/{symbol}/dividends?assetclass=stocks"
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()

            if 'data' in data and 'dividends' in data['data'] and 'rows' in data['data']['dividends']:
                allRows = pd.DataFrame(data['data']['dividends']['rows'])
                dividends_df = pd.DataFrame(allRows)
                dividends_df['yield'] = data['data']['yield']
                if save_to_csv_directly:
                    fileName = os.path.join("..\\data\\dividends\\", f'dividends_{symbol}.csv')
                    try:
                        percentage_float = float(data['data']['yield'].rstrip('%'))
                    except Exception as ex:
                        percentage_float = -1.0
                    if percentage_float >= save_yield:
                        allRows.to_csv(fileName, header=True)
                dividends_df = dividends_df.rename(columns={"amount": "dividend", "yield": "dividend_yield_Rate"})
                '''获取指定条数'''
                if rows <= 0:
                    return dividends_df
                else:
                    return dividends_df.head(rows)
            else:
                return None

        except Exception as e:
            print(f"Error of get_dividend_by_symbol|{e}")
            return None

    def main(self):
        arguments = sys.argv[1:]
        print("command line:", arguments)
        if arguments[0].upper() == "-T" or arguments[0].upper() == "-TIME":
            # 获得指定时间段的calendar数据
            # 示例 -T 2023-11-30 10 dividend20231130.csv
            startDate = arguments[1]
            period = arguments[2]
            checkStep = 1
            try:
                period = int(period)
                checkStep = 2
                print("将处理日期")
                startDate = pd.to_datetime(startDate,
                                           format='%Y-%m-%d')  # datetime.datetime.strptime(startDate, '%Y-%m-%d')
            except Exception as e:
                if checkStep == 1:
                    period = 6  # default
                    print(f"{arguments[2]} 需要是整数")
                else:
                    startDate = pd.Timestamp.today()
                    print(f"日期格式是 yyyy-mm-dd,但是|{arguments[1]}|，默认今天")
            targetFileName = arguments[3]
            if targetFileName is None:
                targetFileName = f"dividends{arguments[1]}.csv"
            # nsdaq = NasdaqFStockDivindent()
            df = self.getDividend_full_vision(period, startDate, targetFileName)
            return df


if __name__ == '__main__':
    nsdaq = NasdaqFStockDivindent()
    # get the future ten days list
    currentFullVision = nsdaq.main()
    # currentFullVision = nsdaq.getDividend_full_vision(6)
    print(currentFullVision)
