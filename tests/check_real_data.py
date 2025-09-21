#!/usr/bin/env python
"""Check real Tesla stock data from Yahoo Finance."""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Tesla 실제 데이터 가져오기
ticker = yf.Ticker('TSLA')

# 1년 데이터
end_date = datetime.now()
start_date = end_date - timedelta(days=365)
hist = ticker.history(start=start_date, end=end_date)

print('Tesla 실제 가격 데이터:')
print(f'현재가: ${hist["Close"].iloc[-1]:.2f}')
print(f'52주 최고가: ${hist["High"].max():.2f}')
print(f'52주 최저가: ${hist["Low"].min():.2f}')
print(f'데이터 기간: {hist.index[0].date()} ~ {hist.index[-1].date()}')
print(f'데이터 개수: {len(hist)}일')

# 최근 5일 종가
print('\n최근 5일 종가:')
for i in range(-5, 0):
    print(f'{hist.index[i].date()}: ${hist["Close"].iloc[i]:.2f}')

# 정보 가져오기
info = ticker.info
print('\n주요 지표:')
print(f'PER: {info.get("trailingPE", "N/A")}')
print(f'PBR: {info.get("priceToBook", "N/A")}')
print(f'시가총액: ${info.get("marketCap", 0)/1e9:.1f}B')
