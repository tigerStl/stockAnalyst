import re
import sys
import math


class fin_Utilities:
    def __init__(self):
        pass

    @staticmethod
    def convertCurrencyValues(currency_string):
        match = re.search(r'\(([^)]+)\)', currency_string)
        if match:
            # Get the numeric value from the match
            numeric_value = float(match.group(1))
            # Make the value negative (since it is enclosed in parentheses)
            numeric_value = -numeric_value
            # print("Numeric Value:", numeric_value)
            return numeric_value
        else:
            # print("Invalid format")
            return math.nan

    @staticmethod
    def convert_string_float(str_src):
        try:
            return float(str_src.replace('%', '').replace('$', '').replace(',', ''))
        except:
            return math.nan
