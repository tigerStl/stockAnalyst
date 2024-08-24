import sys
from datetime import datetime

import pandas as pd

sys.path.append("..")
import nasdaq.PyNasdaq as nsdq


def test_nasdq_summary_api(symbol='USB'):
    nsdqsum = nsdq.NasdaqFStockDivindent()
    usb_info = nsdqsum.get_stock_info(symbol)
    print(usb_info)


def test_nasdaq_get_full_vision(previewDatePeriod, today=pd.Timestamp.today(), start_date_str=None):
    nsdq_sum = nsdq.NasdaqFStockDivindent()
    if start_date_str:
        full_vision = nsdq_sum.getDividend_full_vision(previewDatePeriod, start_date_str=start_date_str)
    else:
        full_vision = nsdq_sum.getDividend_full_vision(previewDatePeriod, today=today)

    return full_vision


def test_nasdaq_get_SandP_divindend_fullvision():
    nsdq_sum = nsdq.NasdaqFStockDivindent()
    SAndP_fullvision = nsdq_sum.getSAndPDivident_full_vision()
    return SAndP_fullvision


def test_getKLine():
    nsdq_k = nsdq.NasdaqFStockDivindent()
    df = nsdq_k.get_kLine('USB', '2023-08-01', '2023-11-26')
    print(df)


def test_getEarningTable(earningDate, period=15):
    nsdp_earning = nsdq.NasdaqFStockDivindent()
    # df = nsdp_earning.getEarningTable(earningDate)
    df = nsdp_earning.getEarningTablesByStartDate(earningDate, period)
    print(df)


def test_read_devidend_and_get_kline(argv):
    nsdq_his = nsdq.NasdaqFStockDivindent()
    nsdq_his.get_k_line_by_args(argv)


def print_usage():
    print("usage:")
    print("\tunitTestPy dividend <StartDate as yyyy-mm-dd>")


''''
常用的参数格式
 dividend 20240613 60
或者  Kline day 1000
'''
if __name__ == '__main__':
    # test_nasdq_summary_api()
    print(sys.argv)
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == 'dividend':
            # 获得该指定日期内的 股息数据
            try:
                if len(sys.argv) == 2:
                    # Get the current date
                    current_date = datetime.now()

                    # Convert to 'yyyyMMdd' format as a string
                    start_date = current_date.strftime('%Y-%m-%d')
                    period = 30
                else:
                    start_date = sys.argv[2]
                    period = 30
                    if len(sys.argv) == 4:
                        try:
                            period = int(sys.argv[3])
                        except ValueError:
                            period = 30
                # test_nasdaq_get_full_vision(30, start_date_str='2023-12-28')
                test_nasdaq_get_full_vision(period, start_date_str=start_date)
            except Exception as e:
                print_usage()
        elif sys.argv[1].lower() == 'kline':
            '''示例 Kline day 1000'''
            print("将获取日线数据.....")
            test_read_devidend_and_get_kline(sys.argv[2:])

        print(sys.argv[1])
    else:
        print(sys.argv)
        startDate = "2024-05-20"
        df = test_nasdaq_get_full_vision(15, pd.to_datetime(startDate))
        # df_SAndP = test_nasdaq_get_SandP_divindend_fullvision()
        # test_getKLine()
        # startDateForEarningTable = "2023-12-16"
        # test_getEarningTable(startDateForEarningTable)
    print("done")
