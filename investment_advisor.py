# 기본 라이브러리
import os
import logging
import datetime
from datetime import datetime, timedelta
import json
import platform
from typing import Any, Dict, Tuple
from pydantic import Field
from abc import ABC, abstractmethod

# 데이터 처리 및 시각화 라이브러리
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 금융 데이터 관련 라이브러리
import yfinance as yf
import FinanceDataReader as fdr
from pykrx import stock
import ta

# 웹 스크래핑 관련 라이브러리
import requests
from bs4 import BeautifulSoup

# Streamlit 관련
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

# 환경 변수 및 설정 관련
from dotenv import load_dotenv
from pydantic import Field

# OpenAI 및 LangChain 관련
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool

# 주석 처리된 라이브러리 (필요시 주석 해제)
# from langchain_anthropic import ChatAnthropic

# 환경 설정
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


# 환경 변수 처리 함수
def get_env_variable(var_name: str) -> str:
    value = os.getenv(var_name)
    if value is None:
        value = st.secrets.get(var_name)
    if value is None:
        st.error(f"{var_name}가 설정되지 않았습니다.")
        st.stop()
    return value


# API 키 설정
OPENAI_API_KEY = get_env_variable("OPENAI_API_KEY")
ALPHA_VANTAGE_API_KEY = get_env_variable("ALPHA_VANTAGE_API_KEY")

# LangChain 설정
os.environ["LANGCHAIN_TRACING_V2"] = (
    "true" if get_env_variable("LANGCHAIN_TRACING_V2") == "true" else "false"
)

os.environ["LANGCHAIN_ENDPOINT"] = get_env_variable("LANGCHAIN_ENDPOINT")
os.environ["LANGCHAIN_API_KEY"] = get_env_variable("LANGCHAIN_API_KEY")


# 한글 폰트 설정
if platform.system() == "Darwin":  # macOS
    plt.rcParams["font.family"] = "AppleGothic"
elif platform.system() == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
else:
    plt.rcParams["font.family"] = "NanumGothic"


# 한국 주식 데이터 가져오기
def get_korea_stock_data(ticker: str) -> Dict[str, Any]:
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        df = fdr.DataReader(ticker, start_date, end_date)

        if df.empty:
            raise ValueError(f"주가 데이터를 가져올 수 없습니다: {ticker}")

        last_price = df["Close"].iloc[-1]
        high_52week = df["High"].max()
        low_52week = df["Low"].min()

        # 베타 계산
        kospi = fdr.DataReader("KS11", start_date, end_date)
        returns = df["Close"].pct_change().dropna()
        market_returns = kospi["Close"].pct_change().dropna()
        covariance = returns.cov(market_returns)
        market_variance = market_returns.var()
        beta = round(covariance / market_variance, 2)

        # 재무 정보 가져오기
        today = datetime.now().strftime("%Y%m%d")
        financial_data = stock.get_market_fundamental_by_ticker(date=today)

        if ticker in financial_data.index:
            stock_data = financial_data.loc[ticker]
            info = {
                "현재가": last_price,
                "PER": stock_data.get("PER", None),
                "PBR": stock_data.get("PBR", None),
                "ROE": stock_data.get("ROE", None),
                "배당수익률": stock_data.get("DIV", None),
                "시가총액": stock_data.get("MARCAP", None),
                "52주 최고가": high_52week,
                "52주 최저가": low_52week,
                "베타": beta,
            }
        else:
            info = {
                "현재가": last_price,
                "PER": None,
                "PBR": None,
                "ROE": None,
                "배당수익률": None,
                "시가총액": None,
                "52주 최고가": high_52week,
                "52주 최저가": low_52week,
                "베타": beta,
            }

        return {k: v if v is not None else "정보 없음" for k, v in info.items()}
    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {str(e)}")
        return {}


def convert_to_yahoo_ticker(company: str, market: str) -> str:
    if market == "한국":
        # 네이버 금융 검색 API를 사용하여 종목 코드 찾기
        search_url = f"https://finance.naver.com/search/searchList.nhn?query={company}"
        response = requests.get(search_url)
        soup = BeautifulSoup(response.text, "html.parser")

        # 첫 번째 검색 결과의 종목 코드 가져오기
        first_result = soup.select_one("td.tit > a")
        if first_result:
            href = first_result["href"]
            ticker = href.split("code=")[1]
            return ticker
        else:
            return company  # 검색 결과가 없으면 입력값 그대로 반환
    return company


# 기본 Agent
class InvestmentAgent(BaseTool, ABC):
    name: str = Field(...)
    description: str
    prompt: PromptTemplate
    weight: float = Field(default=1.0)
    llm: Any = Field(
        default_factory=lambda: ChatOpenAI(
            model_name="gpt-4o-mini-2024-07-18", temperature=0.1
        )
    )

    def __init__(self, **data):
        super().__init__(**data)
        if "llm" not in data:
            self.llm = ChatOpenAI(model_name="gpt-4o-mini-2024-07-18", temperature=0.1)

    @abstractmethod
    def _run(self, query: str, market: str) -> str:
        return self.llm.invoke(self.prompt.format(query=query, market=market)).content

    def get_data(self, company: str, market: str) -> pd.DataFrame:
        try:
            if market == "한국장":
                end_date = datetime.now()
                start_date = end_date - timedelta(days=365)
                df = fdr.DataReader(company, start_date, end_date)
            else:
                df = yf.Ticker(company).history(period="1y")

            if df.empty:
                raise ValueError(f"주가 데이터를 가져올 수 없습니다: {company}")
            return df
        except Exception as e:
            logger.error(f"Error fetching data for {company}: {str(e)}")
            raise


# 기업 분석가 Agent
class CompanyAnalystAgent(InvestmentAgent):
    name: str = Field(default="기업분석가")
    description: str = "기업의 재무, 경영 전략, 시장 포지션을 분석합니다."
    prompt: PromptTemplate = PromptTemplate(
        input_variables=["company", "financials", "key_stats", "market"],
        template="""
        {market} 시장의 {company}에 대한 다음 재무 데이터와 주요 통계를 바탕으로 종합적인 기업 분석을 수행해주세요:
        
        재무 데이터: {financials}
        주요 통계: {key_stats}
        
        1. 재무 상태 분석:
           - 수익성, 성장성, 안정성 측면에서 기업의 재무 상태를 평가해주세요.
           - 주요 재무 비율(예: ROE, 부채비율 등)의 의미를 설명하고 해석해주세요.

        2. 경영 전략 분석:
            - 기업의 주요 사업 부문과 각 부문의 성과를 분석해주세요.
            - 기업의 경쟁 우위와 시장 포지셔닝을 평가해주세요.

        3. 시장 환경 분석:
            - 기업이 속한 산업의 현재 상황과 향후 전망을 제시해주세요.
            - 주요 경쟁사와의 비교 분석을 수행해주세요.

        4. 투자 관점 분석:
            - PER, PBR 등 주요 투자 지표를 해석하고, 기업의 현재 주가 수준에 대한 의견을 제시해주세요.
            - 기업의 배당 정책과 주주 가치 창출 능력을 평가해주세요.

        5. 리스크 요인:
            - 기업이 직면한 주요 리스크 요인을 식별하고 설명해주세요.

        6. 향후 전망:
            

        7. 최종 투자 의견:
            - 위의 분석을 종합하여 최종적으로 투자 의견(강력 매수, 매수, 보유, 매도, 강력 매도)을 제시하고 그 이유를 상세히 설명해주세요.

        분석은 객관적이고 데이터에 기반한 것이어야 하며, 투자자가 정보에 입각한 결정을 내릴 수 있도록 충분한 근거를 제공해야 합니다.
        """,
    )

    def _run(self, company: str, market: str) -> str:
        financials, key_stats = self.get_data(company, market)
        analysis = self.llm.invoke(
            self.prompt.format(
                company=company,
                financials=str(financials),
                key_stats=str(key_stats),
                market=market,
            )
        ).content
        return f"## 기업분석가의 의견\n\n{analysis}"

    def get_data(
        self, company: str, market: str
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        if market == "한국장":
            today = datetime.now().strftime("%Y%m%d")
            try:
                financials = stock.get_market_fundamental_by_ticker(today)
                logger.info(f"Fetched financial data: {financials}")
                if company in financials.index:
                    company_financials = financials.loc[company]
                else:
                    logger.warning(f"Company {company} not found in financial data")
                    company_financials = pd.Series()
            except Exception as e:
                logger.error(f"재무 데이터 가져오기 실패: {str(e)}")
                financials = {}

            key_stats = {
                "PER": financials.get("PER", "N/A"),
                "PBR": financials.get("PBR", "N/A"),
                "ROE": financials.get("ROE", "N/A"),
            }
        else:
            ticker = yf.Ticker(company)
            financials = (
                ticker.financials.to_dict() if not ticker.financials.empty else {}
            )
            info = ticker.info
            key_stats = {
                "PER": info.get("trailingPE", "N/A"),
                "PBR": info.get("priceToBook", "N/A"),
                "ROE": info.get("returnOnEquity", "N/A"),
            }

        return financials, key_stats


# 산업 전문가 Agent
class IndustryExpertAgent(InvestmentAgent):
    name: str = Field(default="산업전문가")
    description: str = "산업 트렌드, 기술 발전, 규제 환경을 평가합니다."
    prompt: PromptTemplate = PromptTemplate(
        input_variables=["industry", "market"],
        template="{market} 시장의 {industry} 산업의 트렌드, 기술 발전, 규제 환경을 평가해주세요.",
    )

    def _run(self, industry: str, market: str) -> str:
        analysis = self.llm.invoke(
            self.prompt.format(industry=industry, market=market)
        ).content
        return f"## 산업전문가의 의견\n\n{analysis}"

    def get_data(self, industry: str) -> Dict[str, Any]:
        # 예시 데이터를 반환합니다. 실제 구현시 API를 통해 데이터를 가져와야 합니다.
        return {
            "trend": "성장중",
            "tech_advancement": "AI 통합",
            "regulatory_environment": "규제 강화 중",
        }


# 거시경제 전문가 Agent
class MacroeconomistAgent(InvestmentAgent):
    name: str = Field(default="거시경제전문가")
    description: str = (
        "금리, 인플레이션, 경제 성장, 실업률과 같은 거시경제 지표를 분석합니다."
    )
    prompt: PromptTemplate = PromptTemplate(
        input_variables=["economy", "indicators"],
        template="{economy} 시장의 현재 거시경제 지표와 잠재적 영향을 분석해주세요. 지표: {indicators}",
    )

    def _run(self, economy: str, market: str) -> str:
        indicators = self.get_economic_indicators(market)
        analysis = self.llm.invoke(
            self.prompt.format(economy=market, indicators=str(indicators))
        ).content

        indicator_text = "\n".join(
            [f"{key}: {value}" for key, value in indicators.items()]
        )

        return f"## 거시경제전문가의 의견\n\n{analysis}\n\n현재 거시경제 지표:\n{indicator_text}"

    @staticmethod
    def get_economic_indicators(market: str) -> Dict[str, Any]:
        base_url = "https://www.alphavantage.co/query"

        indicators = {}

        if market == "한국장":
            country = "KOR"
        else:
            country = "USA"

        try:
            # GDP 데이터 가져오기
            params = {
                "function": "REAL_GDP",
                "interval": "annual",
                "apikey": ALPHA_VANTAGE_API_KEY,
            }
            if country == "KOR":
                params["country"] = "KOR"
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            logger.info(f"GDP API Response: {data}")
            if "data" in data:
                gdp = float(data["data"][0]["value"])
                gdp_growth = (
                    (gdp - float(data["data"][1]["value"]))
                    / float(data["data"][1]["value"])
                    * 100
                )
                indicators["GDP 성장률"] = f"{gdp_growth:.2f}%"
            else:
                indicators["GDP 성장률"] = "데이터 없음"

            # 인플레이션 데이터 가져오기
            params["function"] = "INFLATION"
            if country == "KOR":
                params["country"] = "KOR"
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Inflation API Response: {data}")
            if "data" in data:
                inflation = float(data["data"][0]["value"])
                indicators["인플레이션"] = f"{inflation:.2f}%"
            else:
                indicators["인플레이션"] = "데이터 없음"

            # 금리 데이터 가져오기
            if country == "USA":
                params["function"] = "FEDERAL_FUNDS_RATE"
            else:
                params["function"] = "INTEREST_RATE"
                params["country"] = "KOR"
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Interest Rate API Response: {data}")
            if "data" in data:
                interest_rate = float(data["data"][0]["value"])
                indicators["금리"] = f"{interest_rate:.2f}%"
            else:
                indicators["금리"] = "데이터 없음"

            # 실업률 데이터 가져오기
            params["function"] = "UNEMPLOYMENT"
            if country == "KOR":
                params["country"] = "KOR"
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Unemployment API Response: {data}")
            if "data" in data:
                unemployment = float(data["data"][0]["value"])
                indicators["실업률"] = f"{unemployment:.2f}%"
            else:
                indicators["실업률"] = "데이터 없음"

        except requests.RequestException as e:
            logger.error(f"API 요청 중 오류 발생: {str(e)}")
            indicators = {
                "GDP 성장률": "데이터 가져오기 실패",
                "인플레이션": "데이터 가져오기 실패",
                "금리": "데이터 가져오기 실패",
                "실업률": "데이터 가져오기 실패",
            }
        except Exception as e:
            logger.error(f"예상치 못한 오류 발생: {str(e)}")
            indicators = {
                "GDP 성장률": "데이터 처리 중 오류",
                "인플레이션": "데이터 처리 중 오류",
                "금리": "데이터 처리 중 오류",
                "실업률": "데이터 처리 중 오류",
            }

        logger.info(f"최종 경제 지표: {indicators}")
        return indicators


# 기술 분석가 Agent
class TechnicalAnalystAgent(InvestmentAgent):
    name: str = Field(default="기술분석가")
    description: str = "주가 움직임과 패턴에 대한 기술적 분석을 수행합니다."
    prompt: PromptTemplate = PromptTemplate(
        input_variables=["company", "technical_data", "market"],
        template="""
        {company}의 다음 데이터를 바탕으로 종합적인 기술적 분석을 수행해주세요: {technical_data}
        
        1. 현재 가격, 추천 구매 가격, 추천 손절 가격, 추천 익절 가격을 제시하고, 그 근거를 설명해주세요.
           주식의 가격대에 따라 구매 타이밍을 더 유연하게 조정해주세요. 
           예를 들어, 고가 주식의 경우 단순히 현재 가격의 95%가 아닌, 
           최근의 가격 변동성, 지지선, 이동평균선 등을 고려하여 더 현실적인 구매 가격을 제안해주세요.
        2. 단기(1-3개월), 중기(3-6개월), 장기(6-12개월) 전망을 각각 제시해주세요.
        3. 주요 기술적 지표(이동평균선, RSI, MACD 등)의 현재 상태와 의미를 설명해주세요.
        4. 해당 주식의 현재 추세(상승, 하락, 횡보)와 향후 예상되는 추세 변화에 대해 분석해주세요.
        5. 주요 지지선과 저항선을 식별하고, 이에 따른 매매 전략을 제안해주세요.
        6. 거래량 분석을 통해 현재 가격 움직임의 신뢰도를 평가해주세요.
        7. 시장 전체의 기술적 동향과 비교하여 이 주식의 상대적 강도를 평가해주세요.
        8. 최종적으로 투자 결정(강력 매수, 매수, 보유, 매도, 강력 매도)을 제시하고 그 이유를 상세히 설명해주세요.

        PER과 같은 가치 지표도 고려하여 분석해주세요. 시장: {market}
        분석은 객관적이고 데이터에 기반한 것이어야 하며, 투자자가 정보에 입각한 결정을 내릴 수 있도록 충분한 근거를 제공해야 합니다.
        """,
    )

    def _run(self, company: str, market: str) -> str:
        technical_data = self.get_data(company, market)
        technical_data = {
            k: self._convert_to_python_type(v) for k, v in technical_data.items()
        }
        analysis = self.llm.invoke(
            self.prompt.format(
                company=company, technical_data=str(technical_data), market=market
            )
        ).content
        return f"## 기술분석가의 의견\n\n{analysis}"

    def _convert_to_python_type(self, value):
        if isinstance(value, (np.int64, np.int32, np.int16, np.int8)):
            return int(value)
        elif isinstance(value, (np.float64, np.float32)):
            return float(value)
        elif isinstance(value, np.bool_):
            return bool(value)
        elif isinstance(value, np.datetime64):
            return value.astype(datetime.datetime)
        else:
            return value

    def get_data(self, company: str, market: str) -> Dict[str, Any]:
        hist = super().get_data(company, market)

        # 기술적 지표 계산
        hist["SMA_50"] = ta.trend.sma_indicator(hist["Close"], window=50)
        hist["SMA_200"] = ta.trend.sma_indicator(hist["Close"], window=200)
        hist["RSI"] = ta.momentum.rsi(hist["Close"], window=14)
        macd = ta.trend.MACD(hist["Close"])
        hist["MACD"] = macd.macd()
        hist["MACD_Signal"] = macd.macd_signal()

        current_price = hist["Close"].iloc[-1]
        sma_50 = hist["SMA_50"].iloc[-1]
        sma_200 = hist["SMA_200"].iloc[-1]
        rsi = hist["RSI"].iloc[-1]
        macd_line = hist["MACD"].iloc[-1]
        macd_signal = hist["MACD_Signal"].iloc[-1]

        # 지지선과 저항선 계산
        support_level = hist["Low"].tail(30).min()
        resistance_level = hist["High"].tail(30).max()

        # 가격 제안 계산
        buy_price = current_price * 0.95
        take_profit_price = current_price * 1.1
        stop_loss_price = current_price * 0.9

        price_suggestion = f"""
        매수 가격: {buy_price:.2f}
        매도 가격: {take_profit_price:.2f}
        손절 가격: {stop_loss_price:.2f}
        근거: 현재 가격을 기준으로 5% 하락 시 매수, 10% 상승 시 매도, 10% 하락 시 손절을 제안합니다.
        이는 일반적인 가이드라인이며, 실제 투자 결정 시 추가적인 분석이 필요합니다.
        """

        return {
            "현재가": current_price,
            "추천 구매 가격": buy_price,
            "추천 익절 가격": take_profit_price,
            "추천 손절 가격": stop_loss_price,
            "SMA_50": sma_50,
            "SMA_200": sma_200,
            "RSI": rsi,
            "MACD": macd_line,
            "MACD_Signal": macd_signal,
            "거래량": hist["Volume"].iloc[-1] if "Volume" in hist.columns else "N/A",
            "20일 평균 거래량": (
                hist["Volume"].rolling(window=20).mean().iloc[-1]
                if "Volume" in hist.columns
                else "N/A"
            ),
            "지지선": support_level,
            "저항선": resistance_level,
            "가격_제안_근거": price_suggestion,
        }


# 리스크 관리자 Agent
class RiskManagerAgent(InvestmentAgent):
    name: str = Field(default="리스크관리자")
    description: str = "잠재적 리스크를 평가하고 리스크 관리 전략을 제안합니다."
    prompt: PromptTemplate = PromptTemplate(
        input_variables=["company", "risk_data", "market"],
        template="{company}의 잠재적 리스크를 평가하고 리스크 관리 전략을 제안해주세요. 리스크 데이터: {risk_data}, 시장: {market}",
    )

    def _run(self, company: str, market: str) -> str:
        risk_data = self.get_data(company, market)
        analysis = self.llm.invoke(
            self.prompt.format(company=company, risk_data=str(risk_data), market=market)
        ).content
        return f"## 리스크관리자의 의견\n\n{analysis}"

    def get_data(self, company: str, market: str) -> Dict[str, Any]:
        if market == "한국장":
            # 주식 데이터 가져오기
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            df = fdr.DataReader(company, start_date, end_date)
            if df.empty:
                logger.error(f"주가 데이터를 가져올 수 없습니다: {company}")
                return {
                    "Beta": "N/A",
                    "52주 최고가": "N/A",
                    "52주 최저가": "N/A",
                }

            # 벤치마크 지수(KOSPI) 데이터 가져오기
            kospi = fdr.DataReader(
                "KS11", start_date, end_date
            )  # 코스피 지수 코드: 'KS11'
            if kospi.empty:
                logger.error("코스피 지수 데이터를 가져올 수 없습니다.")
                return {
                    "Beta": "N/A",
                    "52주 최고가": df["High"].rolling(window=252).max().iloc[-1],
                    "52주 최저가": df["Low"].rolling(window=252).min().iloc[-1],
                }

            # 일일 수익률 계산
            df_returns = df["Close"].pct_change().dropna()
            kospi_returns = kospi["Close"].pct_change().dropna()

            # 데이터 정렬 및 동기화
            combined_data = pd.concat([df_returns, kospi_returns], axis=1)
            combined_data.columns = ["Stock", "Market"]
            combined_data.dropna(inplace=True)

            # 베타 계산
            cov = combined_data.cov().iloc[0, 1]
            market_var = combined_data["Market"].var()
            beta = round(cov / market_var, 2)  # 소수점 둘째자리에서 반올림

            return {
                "Beta": beta,
                "52주 최고가": df["High"].rolling(window=252).max().iloc[-1],
                "52주 최저가": df["Low"].rolling(window=252).min().iloc[-1],
            }
        else:
            ticker = yf.Ticker(company)
            info = ticker.info
            return {
                "Beta": info.get("beta", "N/A"),
                "52주 최고가": info.get("fiftyTwoWeekHigh", "N/A"),
                "52주 최저가": info.get("fiftyTwoWeekLow", "N/A"),
            }


# 중재자 Agent
class MediatorAgent(InvestmentAgent):
    name: str = Field(default="중재자")
    description: str = "다른 Agent들의 의견을 종합하여 최종 투자 결정을 내립니다."
    prompt: PromptTemplate = PromptTemplate(
        input_variables=[
            "company_analysis",
            "macro_analysis",
            "technical_analysis",
            "risk_analysis",
            "market",
        ],
        template="""
        다음 분석을 바탕으로 최종 투자 추천을 해주세요:
        
        기업 분석: {company_analysis}
        거시경제 분석: {macro_analysis}
        기술적 분석: {technical_analysis}
        리스크 분석: {risk_analysis}
        시장: {market}
        
        추천에 대한 자세한 설명을 제공해주세요.
        """,
    )

    def __init__(self, **data):
        super().__init__(**data)
        if "llm" not in data:
            self.llm = ChatOpenAI(model_name="gpt-4o-mini-2024-07-18", temperature=0.1)

    def _run(self, inputs: Dict[str, str]) -> str:
        return self.llm.invoke(self.prompt.format(**inputs)).content


def get_korea_stock_history(company: str, analysis_period: int) -> pd.DataFrame:
    end_date = datetime.now()
    start_date = end_date - timedelta(days=analysis_period * 30)  # 대략적인 월 수 계산

    try:
        df = fdr.DataReader(company, start_date, end_date)
        df.rename(
            columns={
                "Open": "Open",
                "High": "High",
                "Low": "Low",
                "Close": "Close",
                "Volume": "Volume",
                "Change": "Change",
            },
            inplace=True,
        )
        return df
    except Exception as e:
        logger.error(f"한국 주식 히스토리 데이터를 가져오는 중 오류 발생: {str(e)}")
        return pd.DataFrame()


# 투자 의사 결정 시스템
class InvestmentDecisionSystem:
    def __init__(self):
        self.agents = {
            "미국장": [
                CompanyAnalystAgent(),
                IndustryExpertAgent(),
                MacroeconomistAgent(),
                TechnicalAnalystAgent(),
                RiskManagerAgent(),
                MediatorAgent(),
            ],
            "한국장": [
                TechnicalAnalystAgent(),
                IndustryExpertAgent(),
                MacroeconomistAgent(),
                RiskManagerAgent(),
                MediatorAgent(),
            ],
        }

    def make_decision(
        self, company: str, industry: str, market: str, analysis_period: int
    ) -> Tuple[str, Dict[str, str], Dict[str, Any], pd.DataFrame]:
        logger.info(f"Starting analysis for {company} in {market} market")
        company = company.strip()
        progress_placeholder = st.empty()

        stop_analysis = st.button("분석 중지")

        info, hist = self.fetch_stock_data(company, market, analysis_period)

        if hist.empty or not info:
            logger.error(f"주가 데이터를 가져올 수 없습니다: {company}")
            return (
                None,
                None,
                {"error": f"주가 데이터를 가져올 수 없습니다: {company}"},
                None,
            )

        results = self.run_agent_analysis(
            company, industry, market, stop_analysis, progress_placeholder
        )

        if results is None:
            logger.error("분석이 중지되었습니다.")
            return None, None, {"error": "분석이 중지되었습니다."}, None

        final_decision = self.get_final_decision(results, market)
        additional_data = self.process_additional_data(info, market)

        technical_result = results.get("기술분석가", "")

        # 기술분석가 결과를 문자열로 처리
        technical_data = {}
        if isinstance(technical_result, str):
            technical_data = {"analysis": technical_result}
        elif isinstance(technical_result, dict):
            technical_data = technical_result

        # 한국장인 경우 key_stats를 빈 딕셔너리로 설정
        key_stats = {}
        if market != "한국장":
            company_analyst = CompanyAnalystAgent()
            _, key_stats = company_analyst.get_data(company, market)

        if hist is not None and not hist.empty:
            logger.info("Starting review_metrics_and_charts")
            self.review_metrics_and_charts(
                additional_data, hist, company, market, technical_data, key_stats
            )
            logger.info("Finished review_metrics_and_charts")
        else:
            logger.error(f"히스토리 데이터가 비어 있습니다: {company}")

        logger.info(f"Analysis completed for {company}")

        return final_decision, results, additional_data, hist

    def fetch_stock_data(
        self, company: str, market: str, analysis_period: int
    ) -> Tuple[Dict[str, Any], pd.DataFrame]:
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=analysis_period * 30)

            if market == "한국장":
                info = get_korea_stock_data(company)
                df = fdr.DataReader(company, start_date, end_date)
                if df.empty:
                    raise ValueError(f"주가 데이터를 가져올 수 없습니다: {company}")
            else:
                ticker = yf.Ticker(company)
                # 티커 정보를 가져오는 부분 수정
                df = ticker.history(start=start_date, end=end_date)

                if df.empty:
                    raise ValueError(f"주가 데이터를 가져올 수 없습니다: {company}")

                info = ticker.info
                info = {
                    "현재가": df["Close"].iloc[-1],
                    "PER": info.get("trailingPE", None),
                    "PBR": info.get("priceToBook", None),
                    "ROE": info.get("returnOnEquity", None),
                    "배당수익률": info.get("dividendYield", None),
                    "시가총액": info.get("marketCap", None),
                    "52주 최고가": info.get("fiftyTwoWeekHigh", None),
                    "52주 최저가": info.get("fiftyTwoWeekLow", None),
                    "베타": info.get("beta", None),
                }

            info = {
                k: v if v is not None and not pd.isna(v) else "정보 없음"
                for k, v in info.items()
            }

            return info, df

        except ValueError as ve:
            logger.error(f"Value Error: {str(ve)}")
            return {}, pd.DataFrame()
        except requests.RequestException as re:
            logger.error(f"Request Error: {str(re)}")
            return {}, pd.DataFrame()
        except Exception as e:
            logger.error(f"Unexpected Error: {str(e)}")
            return {}, pd.DataFrame()

    def process_additional_data(
        self, info: Dict[str, Any], market: str
    ) -> Dict[str, Any]:
        currency = "원" if market == "한국장" else "$"

        def format_value(value, is_percentage=False):
            if isinstance(value, (int, float)) and not pd.isna(value):
                if is_percentage:
                    return f"{value:.2f}%"
                return (
                    f"{value:,.0f}{currency}"
                    if market == "한국장"
                    else f"{currency}{value:,.2f}"
                )
            return "정보 없음"

        return {
            "현재가": format_value(info.get("현재가")),
            "PER": format_value(info.get("PER")),
            "PBR": format_value(info.get("PBR")),
            "ROE": format_value(info.get("ROE"), is_percentage=True),
            "배당수익률": format_value(info.get("배당수익률"), is_percentage=True),
            "시가총액": format_value(info.get("시가총액")),
            "52주 최고가": format_value(info.get("52주 최고가")),
            "52주 최저가": format_value(info.get("52주 최저가")),
            "베타": format_value(info.get("베타")),
        }

    def review_metrics_and_charts(
        self,
        additional_data: Dict[str, Any],
        hist: pd.DataFrame,
        company: str,
        market: str,
        technical_data: Dict[str, Any],
        key_stats: Dict[str, Any],
    ):
        logger.info("Starting review_metrics_and_charts")

        if market == "한국장":
            review_price_trend(hist, company, market, additional_data)
            review_macd_indicator(hist)
            review_additional_metrics(additional_data)
            provide_investment_opinion_korea(
                additional_data, hist, company, technical_data, market
            )
        else:
            review_key_metrics(additional_data, hist, market, key_stats)
            review_price_trend(hist, company, market, additional_data)
            review_macd_indicator(hist)
            review_additional_metrics(additional_data)
            provide_investment_opinion(
                additional_data, hist, company, technical_data, market
            )

        logger.info("Finished review_metrics_and_charts")

    def run_agent_analysis(
        self,
        company: str,
        industry: str,
        market: str,
        stop_analysis: bool,
        progress_placeholder: DeltaGenerator,
    ):
        results = {}
        agents = self.agents[market]
        with st.expander("전문가 분석 과정", expanded=True):
            for i, agent in enumerate(agents[:-1]):  # MediatorAgent 제외
                if stop_analysis:
                    st.warning("분석이 중지되었습니다.")
                    return None
                progress_placeholder.text(
                    f"{agent.name}가 분석 중입니다... ({i+1}/{len(agents)-1})"
                )
                try:
                    if agent.name == "산업전문가":
                        results[agent.name] = agent._run(industry, market)
                    elif agent.name == "거시경제전문가":
                        results[agent.name] = agent._run(market, market)
                    else:
                        results[agent.name] = agent._run(company, market)
                    st.markdown(results[agent.name])
                except Exception as e:
                    st.error(f"{agent.name} 분석 중 오류 발생: {str(e)}")
                    results[agent.name] = f"분석 실패: {str(e)}"
        return results

    def get_final_decision(self, results: Dict[str, str], market: str) -> str:
        progress_placeholder = st.empty()
        progress_placeholder.text("중재자가 최종 결정을 내리고 있습니다...")

        mediator_prompt = PromptTemplate(
            input_variables=[
                "company_analysis",
                "industry_analysis",
                "macro_analysis",
                "technical_analysis",
                "risk_analysis",
                "market",
            ],
            template="""
            다음 분석을 바탕으로 종합적이고 균형 잡힌 최종 투자 추천을 제공해주세요:
            
            기업 분석: {company_analysis}
            산업 분석: {industry_analysis}
            거시경제 분석: {macro_analysis}
            기술적 분석: {technical_analysis}
            리스크 분석: {risk_analysis}
            시장: {market}
            
            다음 사항을 포함하여 상세한 투자 의견을 제시해주세요:
            1. 투자 추천 등급 (강력 매수 / 매수 / 보유 / 매도 / 강력 매도)
            2. 단기, 중기, 장기 전망
            3. 주요 매수 근거 및 위험 요소
            4. 적정 매수 가격 범위 및 목표 가격
            5. 손절 가격 및 제안하는 투자 비중
            6. 대안 투자 옵션 (있다면)
            7. 투자자의 위험 성향에 따른 차별화된 조언

            투자 결정에 대한 근거를 명확히 제시하고, 각 분석 결과의 중요도를 고려하여 종합적인 의견을 제시해주세요.
            또한, 이 추천이 투자자의 개인적인 재무 상황과 목표에 따라 달라질 수 있음을 명시해주세요.
            """,
        )

        mediator_inputs = {
            "company_analysis": results.get("기업분석가", "분석 데이터 없음"),
            "industry_analysis": results.get("산업전문가", "분석 데이터 없음"),
            "macro_analysis": results.get("거시경제전문가", "분석 데이터 없음"),
            "technical_analysis": results.get("기술분석가", "분석 데이터 없음"),
            "risk_analysis": results.get("리스크관리자", "분석 데이터 없음"),
            "market": market,
        }

        # MediatorAgent is now the last item in the agents list for the specific market
        mediator_agent = self.agents[market][-1]
        final_decision = mediator_agent.llm.invoke(
            mediator_prompt.format(**mediator_inputs)
        ).content
        progress_placeholder.empty()

        return final_decision

    def process_additional_data(
        self, info: Dict[str, Any], market: str
    ) -> Dict[str, Any]:
        currency = "원" if market == "한국장" else "$"

        def currency_format(x, c):
            if isinstance(x, (int, float)):
                return f"{x:,.0f}{c}" if market == "한국장" else f"{c}{x:,.2f}"
            return f"{x}{c}" if market == "한국장" else f"{c}{x}"

        market_cap = info.get("시가총액", "정보 없음")
        if market_cap != "정보 없음" and isinstance(market_cap, (int, float)):
            market_cap = (
                f"{market_cap:,.0f}{currency}"
                if market == "한국장"
                else f"{currency}{market_cap:,.0f}"
            )

        return {
            "현재가": currency_format(info.get("현재가", "정보 없음"), currency),
            "PER": info.get("PER", "정보 없음"),
            "PBR": info.get("PBR", "정보 없음"),
            "ROE": info.get("ROE", "정보 없음"),
            "배당수익률": info.get("배당수익률", "정보 없음"),
            "시가총액": market_cap,
            "52주 최고가": currency_format(
                info.get("52주 최고가", "정보 없음"), currency
            ),
            "52주 최저가": currency_format(
                info.get("52주 최저가", "정보 없음"), currency
            ),
            "베타": info.get("베타", "정보 없음"),
        }

    def update_weights(self, accuracy_scores: Dict[str, float]):
        for agent in self.agents[:-1]:
            if agent.name in accuracy_scores:
                agent.weight = accuracy_scores[agent.name]


# 주요 지표 및 그래프 리뷰 함수들
def get_metric_description(key: str) -> str:
    descriptions = {
        "현재가": "현재 주식의 거래 가격",
        "PER": "주가수익비율, 주가를 주당순이익으로 나눈 값",
        "PBR": "주가순자산비율, 주가를 주당순자산으로 나눈 값",
        "ROE": "자기자본이익률, 당기순이익을 자기자본으로 나눈 값",
        "배당수익률": "주당 배당금을 주가로 나눈 비율",
        "시가총액": "발행주식수와 주가를 곱한 총 시장 가치",
        "52주 최고가": "최근 52주 동안의 최고 주가",
        "52주 최저가": "최근 52주 동안의 최저 주가",
        "베타": "시장 대비 주가 변동성을 나타내는 지표",
    }
    return descriptions.get(key, "설명 없음")


def review_key_metrics(
    additional_data: Dict[str, Any],
    hist: pd.DataFrame,
    market: str,
    key_stats: Dict[str, Any],
):
    if market == "한국장":
        st.write("한국장에서는 주요 지표 상세 분석을 제공하지 않습니다.")
        return

    with st.expander("주요 지표 상세 분석", expanded=True):
        table = "| 지표 | 값 | 설명 |\n|------|----|----|"

        # CompanyAnalystAgent에서 가져온 데이터 추가
        for key, value in key_stats.items():
            if isinstance(value, float):
                if key in ["PER", "PBR"]:
                    value = f"{value:.2f}배"
                elif key in ["ROE", "Dividend Yield"]:
                    value = f"{value:.2f}%"
            description = get_metric_description(key)
            table += f"\n| {key} | {value} | {description} |"

        # 기존 additional_data 처리
        for key, value in additional_data.items():
            if key not in key_stats:
                description = get_metric_description(key)
                table += f"\n| {key} | {value} | {description} |"

        st.markdown(table)


def review_price_trend(
    hist: pd.DataFrame, company: str, market: str, additional_data: Dict[str, Any]
):
    currency = "원" if market == "한국장" else "$"
    with st.expander("주가 트렌드 상세 분석"):
        current_price = hist["Close"].iloc[-1]
        sma_50 = hist["Close"].rolling(window=50).mean().iloc[-1]
        sma_200 = hist["Close"].rolling(window=200).mean().iloc[-1]

        if market == "한국장":
            st.write(f"현재 주가: {current_price:,.0f}{currency}")
            st.write(f"50일 이동평균: {sma_50:,.0f}{currency}")
            st.write(f"200일 이동평균: {sma_200:,.0f}{currency}")
        else:
            st.write(f"현재 주가: {currency}{current_price:,.2f}")
            st.write(f"50일 이동평균: {currency}{sma_50:,.2f}")
            st.write(f"200일 이동평균: {currency}{sma_200:,.2f}")

        if current_price > sma_50 > sma_200:
            st.write(
                "📈 상승 추세: 현재 가격이 50일 및 200일 이동평균선 위에 있어 강세장을 시사합니다."
            )
        elif current_price < sma_50 < sma_200:
            st.write(
                "📉 하락 추세: 현재 가격이 50일 및 200일 이동평균선 아래에 있어 약세장을 시사합니다."
            )
        else:
            st.write(
                "➡️ 횡보 추세: 현재 가격이 이동평균선 사이에 있어 명확한 추세가 보이지 않습니다. 추가적인 모멘텀을 확인해야 합니다."
            )

        high_52week = additional_data.get("52주 최고가", "정보 없음")
        low_52week = additional_data.get("52주 최저가", "정보 없음")

        st.write(f"52주 최고가: {high_52week}")
        st.write(f"52주 최저가: {low_52week}")

        if high_52week != "정보 없음" and isinstance(current_price, (int, float)):
            high_52week_value = float(
                high_52week.replace(currency, "").replace(",", "")
            )
            st.write(
                f"현재 가격은 52주 최고가 대비 {((current_price - high_52week_value) / high_52week_value * 100):.2f}% 위치에 있습니다."
            )


def review_macd_indicator(hist: pd.DataFrame):
    with st.expander("MACD 지표 상세 분석"):
        macd = ta.trend.MACD(hist["Close"])
        macd_line = macd.macd().iloc[-1]
        signal_line = macd.macd_signal().iloc[-1]

        st.write(f"MACD 라인: {macd_line:.4f}")
        st.write(f"시그널 라인: {signal_line:.4f}")

        if macd_line > signal_line:
            st.write(
                "📈 MACD가 시그널 라인을 상향 돌파했습니다. 이는 단기적인 상승 추세의 시작을 의미할 수 있습니다."
            )
            if macd_line > 0:
                st.write(
                    "또한, MACD가 0선 위에 있어 중장기적인 상승 추세를 지지하고 있습니다."
                )
            else:
                st.write(
                    "하지만 MACD가 아직 0선 아래에 있어 중장기적인 하락 추세에서 벗어나지 못했을 수 있습니다."
                )
        elif macd_line < signal_line:
            st.write(
                "📉 MACD가 시그널 라인을 하향 돌파했습니다. 이는 단기적인 하락 추세의 시작을 의미할 수 있습니다."
            )
            if macd_line < 0:
                st.write(
                    "또한, MACD가 0선 아래에 있어 중장기적인 하락 추세를 지지하고 있습니다."
                )
            else:
                st.write(
                    "하지만 MACD가 아직 0선 위에 있어 중장기적인 상승 추세가 유지될 수 있습니다."
                )
        else:
            st.write(
                "➡️ MACD와 시그널 라인이 교차하고 있습니다. 추세 전환의 가능성을 지켜봐야 합니다."
            )


def review_additional_metrics(additional_data: Dict[str, Any]):
    st.write("### 추가 지표 분석")
    st.write(f"시가총액: {additional_data.get('시가총액', 'N/A')}")
    st.write(f"베타: {additional_data.get('베타', 'N/A')}")

    beta = additional_data.get("베타")
    if beta is not None and beta != "N/A":
        beta = float(beta)
        if beta > 1.5:
            st.write(
                "🚨 베타가 1.5를 초과하여 시장 대비 변동성이 매우 높습니다. 주의가 필요합니다."
            )
        elif 1 < beta <= 1.5:
            st.write("⚠️ 베타가 1과 1.5 사이로, 시장 대비 약간 높은 변동성을 보입니다.")
        elif 0.5 <= beta <= 1:
            st.write("✅ 베타가 0.5와 1 사이로, 적정한 수준의 변동성을 보입니다.")
        else:
            st.write("🔹 베타가 0.5 미만으로, 시장 대비 낮은 변동성을 보입니다.")
    else:
        st.write("베타 데이터를 사용할 수 없습니다.")


def safe_float(value):
    if isinstance(value, (int, float)):
        return float(value)
    elif isinstance(value, str):
        # Remove currency symbols and commas
        value = value.replace("$", "").replace("원", "").replace(",", "")
        if value.lower() == "n/a" or value.lower() == "정보 없음":
            return -1.0  # or you could return None
        try:
            return float(value.replace("%", ""))
        except ValueError:
            return -1.0  # or you could return None
    else:
        return -1.0  # or you could return None


def provide_investment_opinion_korea(
    additional_data: Dict[str, Any],
    hist: pd.DataFrame,
    company: str,
    technical_data: Dict[str, Any],
    market: str,
):
    st.write("### 종합 투자 의견")
    st.write(
        f"{company}에 대한 종합적인 분석 결과, 다음과 같은 투자 의견을 제시합니다:"
    )

    current_price = hist["Close"].iloc[-1]
    sma_50 = hist["Close"].rolling(window=50).mean().iloc[-1]
    sma_200 = hist["Close"].rolling(window=200).mean().iloc[-1]
    macd = ta.trend.MACD(hist["Close"])
    macd_line = macd.macd().iloc[-1]
    signal_line = macd.macd_signal().iloc[-1]

    # 투자 추천 등급 결정
    if current_price < sma_50 < sma_200 and macd_line < signal_line:
        recommendation = "강력 매수"
    elif current_price < sma_50 and macd_line > signal_line:
        recommendation = "매수"
    elif sma_50 < current_price < sma_200 and macd_line > signal_line:
        recommendation = "보유"
    elif current_price > sma_200 and macd_line < signal_line:
        recommendation = "매도"
    else:
        recommendation = "관망"

    # 가격 목표 설정
    currency = "원"
    buy_price = current_price * 0.95
    sell_price = current_price * 1.1
    stop_loss_price = current_price * 0.9

    # 가격 목표를 통화 기호와 함께 형식화
    buy_target = f"{buy_price:,.0f}{currency}"
    sell_target = f"{sell_price:,.0f}{currency}"
    stop_loss = f"{stop_loss_price:,.0f}{currency}"

    opinion = f"""
    ### 1. 투자 추천 등급: {recommendation}

    ### 2. 전망
    - **단기(1-3개월)**: {"상승 모멘텀" if current_price > sma_50 else "하락 추세"}가 있어 보입니다.
    - **중기(3-6개월)**: {"상승세 지속 가능성" if current_price > sma_200 else "하락세 지속 가능성"}이 있습니다.
    - **장기(6-12개월)**: 기업의 펀더멘털과 시장 상황에 따라 달라질 수 있습니다.

    ### 3. 주요 기술적 지표
    - **현재가**: {additional_data['현재가']}
    - **52주 최고가**: {additional_data['52주 최고가']}
    - **52주 최저가**: {additional_data['52주 최저가']}
    - **베타**: {additional_data['베타']}

    ### 4. 가격 목표
    - **적정 매수 가격**: {buy_target}
    - **목표 가격**: {sell_target}
    - **손절 가격**: {stop_loss}

    ### 5. 투자 전략
    1. {recommendation} 전략을 고려하되, {buy_target} 근처에서 매수 기회를 노려볼 수 있습니다.
    2. 매수 후 {sell_target}을 목표로 하되, 시장 상황에 따라 유동적으로 대응하세요.
    3. 주가가 {stop_loss} 이하로 하락하면 손실 최소화를 위해 매도를 고려하세요.
    4. 산업 동향과 기업의 실적 발표, 주요 뉴스를 지속적으로 모니터링하세요.
    5. 포트폴리오 다각화를 통해 리스크를 분산시키는 것이 중요합니다.

    ### 6. 추가 고려사항
    - 한국 시장의 특성상 글로벌 경제 상황과 지정학적 리스크에 민감할 수 있습니다.
    - 외국인 투자자들의 매매 동향을 주시할 필요가 있습니다.
    - 기업의 지배구조와 관련된 이슈들도 주가에 영향을 줄 수 있으므로 관심을 가져야 합니다.
    """

    st.write(opinion)

    st.write(
        "⚠️ 주의: 이 분석은 AI에 의해 생성된 것으로, 전문 금융 자문가의 의견을 대체할 수 없습니다. 실제 투자 결정 전에는 반드시 추가적인 리서치와 전문가의 조언을 구하시기 바랍니다."
    )


def provide_investment_opinion(
    additional_data: Dict[str, Any],
    hist: pd.DataFrame,
    company: str,
    technical_data: Dict[str, Any],
    market: str,
):
    st.write("### 종합 투자 의견")
    st.write(
        f"{company}에 대한 종합적인 분석 결과, 다음과 같은 투자 의견을 제시합니다:"
    )

    current_price = hist["Close"].iloc[-1]
    sma_50 = hist["Close"].rolling(window=50).mean().iloc[-1]
    sma_200 = hist["Close"].rolling(window=200).mean().iloc[-1]
    macd = ta.trend.MACD(hist["Close"])
    macd_line = macd.macd().iloc[-1]
    signal_line = macd.macd_signal().iloc[-1]

    per_value = safe_float(additional_data.get("PER", "N/A"))
    pbr_value = safe_float(additional_data.get("PBR", "N/A"))
    roe_value = safe_float(additional_data.get("ROE", "N/A"))
    dividend_yield_value = safe_float(additional_data.get("배당수익률", "N/A"))

    # 투자 추천 등급 결정
    if current_price < sma_50 < sma_200 and macd_line < signal_line:
        recommendation = "강력 매수"
    elif current_price < sma_50 and macd_line > signal_line:
        recommendation = "매수"
    elif sma_50 < current_price < sma_200 and macd_line > signal_line:
        recommendation = "보유"
    elif current_price > sma_200 and macd_line < signal_line:
        recommendation = "매도"
    else:
        recommendation = "관망"

    # 52주 최고가와 최저가 가져오기
    high_52week = additional_data.get("52주 최고가", "정보 없음")
    low_52week = additional_data.get("52주 최저가", "정보 없음")

    # 가격 목표 설정
    currency = "원" if market == "한국장" else "$"
    buy_price = current_price * 0.95
    sell_price = current_price * 1.1
    stop_loss_price = current_price * 0.9

    # 가격 목표를 통화 기호와 함께 형식화
    buy_target = (
        f"{buy_price:,.0f}{currency}"
        if market == "한국장"
        else f"{currency}{buy_price:.2f}"
    )
    sell_target = (
        f"{sell_price:,.0f}{currency}"
        if market == "한국장"
        else f"{currency}{sell_price:.2f}"
    )
    stop_loss = (
        f"{stop_loss_price:,.0f}{currency}"
        if market == "한국장"
        else f"{currency}{stop_loss_price:.2f}"
    )

    opinion = f"""
    투자 추천 등급: {recommendation}
    
    1. 현재가: {additional_data['현재가']}
    2. PER (주가수익비율): {additional_data['PER']}
    3. PBR (주가순자산비율): {additional_data['PBR']}
    4. ROE (자기자본이익률): {additional_data['ROE']}
    5. 배당 수익률: {additional_data['배당수익률']}
    6. 52주 최고가: {high_52week}
    7. 52주 최저가: {low_52week}
    8. 시가총액: {additional_data['시가총액']}
    9. 베타: {additional_data['베타']}
        
    가격 목표:
    - 매수 목표가: {buy_target}
    - 매도 목표가: {sell_target}
    - 손절가: {stop_loss}

    현재 주가 추세와 기술적 지표를 고려할 때, """

    if current_price > sma_50:
        opinion += "단기적으로는 상승 모멘텀이 있어 보입니다."
    else:
        opinion += "단기적으로는 하락 추세에 있습니다."

    opinion += "\n\n"

    if per_value == -1 or pbr_value == -1:
        opinion += "PER 또는 PBR 데이터가 없어 정확한 평가가 어렵습니다."
    elif per_value > 20 or pbr_value > 2:
        opinion += "PER과 PBR이 다소 높은 편이어서, 고평가 리스크에 주의해야 합니다."
    elif per_value < 10 or pbr_value < 1:
        opinion += "PER과 PBR이 낮은 편이어서, 저평가 가능성이 있습니다."
    else:
        opinion += "PER과 PBR이 적정 수준에 있어 보입니다."

    opinion += "\n\n"

    if roe_value == -1 or dividend_yield_value == -1:
        opinion += "ROE 또는 배당수익률 데이터가 없어 정확한 평가가 어렵습니다."
    elif roe_value > 15 and dividend_yield_value > 3:
        opinion += "ROE와 배당 수익률을 고려하면, 기업의 수익성과 주주 환원 정책은 양호한 편입니다."
    elif roe_value < 10 or dividend_yield_value < 1:
        opinion += "ROE와 배당 수익률이 낮은 편이어서, 기업의 수익성과 주주 환원 정책에 주의가 필요합니다."
    else:
        opinion += "ROE와 배당 수익률은 보통 수준입니다."

    opinion += "\n\n"

    if macd_line > signal_line:
        opinion += "MACD 지표는 단기적인 상승 신호를 보이고 있으나, 전반적인 시장 상황과 함께 고려해야 합니다."
    else:
        opinion += "MACD 지표는 단기적인 하락 신호를 보이고 있으나, 전반적인 시장 상황과 함께 고려해야 합니다."

    opinion += f"""

    투자 전략:
    1. {recommendation} 전략을 고려하되, {buy_target} 근처에서 매수 기회를 노려볼 수 있습니다.
    2. 매수 후 {sell_target}을 목표로 하되, 시장 상황에 따라 유동적으로 대응하세요.
    3. 주가가 {stop_loss} 이하로 하락하면 손실 최소화를 위해 매도를 고려하세요.
    4. 산업 동향과 기업의 실적 발표, 주요 뉴스를 지속적으로 모니터링하세요.
    5. 포트폴리오 다각화를 통해 리스크를 분산시키는 것이 중요합니다.
    """

    st.write(opinion)

    st.write(
        "⚠️ 주의: 이 분석은 AI에 의해 생성된 것으로, 전문 금융 자문가의 의견을 대체할 수 없습니다. 실제 투자 결정 전에는 반드시 추가적인 리서치와 전문가의 조언을 구하시기 바랍니다."
    )


def recommend_similar_stocks(company: str, market: str) -> pd.DataFrame:
    if market == "한국장":
        st.warning("현재 한국 시장에 대한 섹터 정보를 가져올 수 없습니다.")
        return pd.DataFrame()
    else:
        # 미국 시장의 경우 S&P 500 기업 목록 사용
        sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        try:
            sp500_table = pd.read_html(sp500_url)
            sp500_df = sp500_table[0]

            # 입력된 회사의 섹터를 찾기
            ticker = company.upper()
            company_info = sp500_df[sp500_df["Symbol"] == ticker]
            if company_info.empty:
                st.warning("입력한 티커가 S&P 500 목록에 없습니다.")
                return pd.DataFrame()

            # 'GICS Sector' 컬럼이 있는지 확인
            if "GICS Sector" not in sp500_df.columns:
                st.warning("S&P 500 데이터에 섹터 정보가 없습니다.")
                return pd.DataFrame()

            company_sector = company_info["GICS Sector"].values[0]

            # 동일 섹터의 다른 종목 추천
            similar_stocks = sp500_df[sp500_df["GICS Sector"] == company_sector]
            # 입력된 회사 제외
            similar_stocks = similar_stocks[similar_stocks["Symbol"] != ticker]

            # 재무 지표 가져오기
            financial_data = []
            for symbol in similar_stocks["Symbol"].tolist():
                try:
                    stock_info = yf.Ticker(symbol).info
                    pe_ratio = stock_info.get("trailingPE", None)
                    market_cap = stock_info.get("marketCap", None)
                    roe = stock_info.get("returnOnEquity", None)
                    if pe_ratio and market_cap:
                        financial_data.append(
                            {
                                "티커": symbol,
                                "회사명": stock_info.get("shortName", symbol),
                                "PER": pe_ratio,
                                "ROE": roe,
                                "시가총액": market_cap,
                            }
                        )
                except Exception as e:
                    continue

            # 데이터프레임으로 변환
            financial_df = pd.DataFrame(financial_data)
            if financial_df.empty:
                st.warning("재무 데이터를 가져올 수 없습니다.")
                return pd.DataFrame()

            # 시가총액 상위 5개 종목 추천
            top_stocks = financial_df.sort_values(by="시가총액", ascending=False).head(
                5
            )

            # 추천 이유 추가
            top_stocks["추천 이유"] = top_stocks.apply(
                lambda x: f"동일 섹터 내 시가총액 상위 기업으로 안정성이 높음", axis=1
            )

            # 필요한 열만 선택
            top_stocks = top_stocks[
                ["티커", "회사명", "PER", "ROE", "시가총액", "추천 이유"]
            ]

            return top_stocks

        except Exception as e:
            st.error(f"S&P 500 데이터를 가져오는 중 오류가 발생했습니다: {str(e)}")
            return pd.DataFrame()


# 금일의 추천 종목 기능
def recommend_today_stocks(market: str) -> pd.DataFrame:
    """
    금일의 추천 종목을 반환합니다.
    """
    if market == "한국장":
        # 예시로 PER이 낮고 거래량이 많은 상위 5개 종목 추천
        today = datetime.now().strftime("%Y%m%d")
        data = stock.get_market_fundamental_by_ticker(today)

        # Volume 컬럼 추가를 위해 거래량 데이터 가져오기
        volume_data = stock.get_market_trading_value_by_ticker(today)
        data = data.join(volume_data["거래량"])

        # 필터링
        recommended = data[(data["PER"] < 10) & (data["거래량"] > 1000000)]
        recommended = recommended.sort_values(by="거래량", ascending=False).head(5)
        recommended = recommended[["PER", "거래량"]]
        recommended.index.name = "티커"
        recommended.reset_index(inplace=True)

        # 추천 이유 추가
        recommended["추천 이유"] = "PER이 낮고 거래량이 많아 저평가된 성장주로 판단"

        return recommended

    else:
        # 미국장의 경우 S&P 500 종목 중에서 RSI가 30 이하인 과매도 종목 추천
        sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        sp500_table = pd.read_html(sp500_url)
        sp500_df = sp500_table[0]
        tickers = sp500_df["Symbol"].tolist()

        recommended = []

        for ticker in tickers:
            try:
                # 티커 수정: '.'을 '-', '$' 제거
                yf_ticker = ticker.replace(".", "-").replace("$", "")
                stock_data = yf.Ticker(yf_ticker).history(period="ytd")
                if stock_data.empty:
                    continue
                rsi = ta.momentum.RSIIndicator(stock_data["Close"]).rsi().iloc[-1]
                macd = ta.trend.MACD(stock_data["Close"])
                macd_line = macd.macd().iloc[-1]
                macd_signal = macd.macd_signal().iloc[-1]

                if rsi < 30 and macd_line > macd_signal:
                    recommended.append(
                        {
                            "티커": ticker,
                            "RSI": round(rsi, 2),
                            "추천 이유": f"RSI {round(rsi, 2)}로 과매도 상태이며, MACD가 시그널 라인을 상향 돌파하여 상승 모멘텀 기대",
                        }
                    )

            except Exception as e:
                continue

            if len(recommended) >= 5:
                break

        recommended_df = pd.DataFrame(recommended)
        return recommended_df


# Streamlit UI
def main():
    st.set_page_config(layout="wide", page_title="AI 투자 자문 서비스")

    # CSS 스타일
    st.markdown(
        """
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 10px rgba(0,0,0,0.2);
    }
    .selected {
        background-color: #FF4B4B !important;
        color: white !important;
    }
    .custom-info {
        background-color: #e1f5fe;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 5px solid #03a9f4;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.sidebar.title("AI 투자 자문 서비스")
    st.sidebar.write("다양한 전문가 의견을 종합한 투자 분석 서비스")

    # 시장 선택 버튼
    st.sidebar.markdown("### 시장 선택")
    col1, col2 = st.sidebar.columns(2)

    if "market" not in st.session_state:
        st.session_state.market = "미국장"
    if "analysis_started" not in st.session_state:
        st.session_state.analysis_started = False

    if col1.button(
        "미국장",
        key="us_market",
        help="미국 주식 시장 선택",
        disabled=st.session_state.analysis_started,
    ):
        st.session_state.market = "미국장"
    if col2.button(
        "한국장",
        key="kr_market",
        help="한국 주식 시장 선택",
        disabled=st.session_state.analysis_started,
    ):
        st.session_state.market = "한국장"

    # 선택된 버튼 스타일
    st.markdown(
        f"""
    <script>
        function updateButtonStyles() {{
            var buttons = window.parent.document.querySelectorAll('.stButton button');
            buttons.forEach(function(btn) {{
                if (btn.innerText === '{st.session_state.market}') {{
                    btn.classList.add('selected');
                }} else {{
                    btn.classList.remove('selected');
                }}
            }});
        }}
        updateButtonStyles();
        var observer = new MutationObserver(updateButtonStyles);
        observer.observe(window.parent.document.body, {{ childList: true, subtree: true }});
    </script>
    """,
        unsafe_allow_html=True,
    )

    # 회사 티커 입력
    company = st.sidebar.text_input("회사 티커 입력", help="티커 코드를 입력해주세요")

    # 티커 검색 안내
    if st.session_state.market == "미국장":
        ticker_search_url = "https://finance.yahoo.com/lookup"
        ticker_guide = "예: 애플(Apple)의 티커는 AAPL입니다."
    else:
        ticker_search_url = "https://finance.naver.com/item/main.naver"
        ticker_guide = "예: 삼성전자의 티커는 005930입니다."

    st.sidebar.markdown(
        f"""
    <div class="custom-info">
        <p>{ticker_guide}</p>
        <p>회사의 티커를 모르시나요? <a href="{ticker_search_url}" target="_blank">여기서 검색해보세요!</a></p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 산업 선택
    industries = [
        "기술",
        "금융",
        "헬스케어",
        "소비재",
        "에너지",
        "통신",
        "산업재",
        "유틸리티",
        "부동산",
        "원자재",
    ]

    industry = st.sidebar.selectbox("산업 선택", options=industries)

    # 분석 기간 선택
    analysis_period = st.sidebar.slider("분석 기간 (개월)", 1, 60, 12)

    if st.sidebar.button("분석 시작", key="start_analysis"):
        if not company:
            st.error("회사 티커를 입력해주세요.")
            return

        with st.spinner("다중 에이전트 분석 진행 중..."):
            system = InvestmentDecisionSystem()
            try:
                decision, results, additional_data, hist = system.make_decision(
                    company, industry, st.session_state.market, analysis_period
                )

                if (
                    decision is None
                    or additional_data is None
                    or "error" in additional_data
                ):
                    st.error(
                        f"데이터 분석 중 오류 발생: {additional_data.get('error', '알 수 없는 오류')}"
                    )
                    return

                # 탭 생성
                tabs = [
                    "종합 분석",
                    "기술적 분석",
                    "에이전트 상세 분석",
                    "재무 지표",
                    "동일 섹터 추천 종목",
                    "금일의 추천 종목",
                ]
                tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(tabs)

                with tab1:
                    display_summary(decision, additional_data, st.session_state.market)

                with tab2:
                    display_technical_analysis(
                        hist,
                        company,
                        st.session_state.market,
                        results.get("기술분석가", {}),
                    )

                with tab3:
                    display_agent_analysis(results)

                with tab4:
                    display_financial_metrics(additional_data)

                with tab5:
                    similar_stocks = recommend_similar_stocks(
                        company, st.session_state.market
                    )
                    st.header("동일 섹터 추천 종목")
                    if not similar_stocks.empty:
                        st.table(similar_stocks)
                    else:
                        st.write("추천 종목이 없습니다.")

                with tab6:
                    today_recommendations = recommend_today_stocks(
                        st.session_state.market
                    )
                    st.header("금일의 추천 종목")
                    if not today_recommendations.empty:
                        st.table(today_recommendations)
                    else:
                        st.write("추천 종목이 없습니다.")

            except Exception as e:
                st.error(f"분석 중 오류 발생: {str(e)}")
                logging.exception("Unexpected error during analysis")
                return

    # 서비스 사용 방법
    with st.sidebar.expander("서비스 사용 방법"):
        st.markdown(
            """
        1. 시장을 선택합니다 (미국장 또는 한국장).
        2. 회사 티커를 입력합니다 (필요시 티커 검색 링크 사용).
        3. 산업을 선택합니다.
        4. 분석 기간을 설정합니다.
        5. '분석 시작' 버튼을 클릭합니다.
        6. 결과를 확인하고 각 탭의 상세 정보를 검토합니다.
        """
        )


def display_summary(decision, additional_data, market):
    st.header("종합 투자 의견")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(decision)

    with col2:
        st.subheader("주요 지표")
        if market == "한국장":
            filtered_data = {
                k: v
                for k, v in additional_data.items()
                if v != "0.0" and v != "정보 없음" and v != 0 and v != "0원"
            }
            for key, value in filtered_data.items():
                st.metric(label=key, value=value)
        else:
            for key, value in additional_data.items():
                st.metric(label=key, value=value)


def display_technical_analysis(
    hist: pd.DataFrame, company: str, market: str, technical_data: dict
):
    if hist.empty:
        st.error("주가 데이터를 가져올 수 없습니다.")
        return

    st.header("기술적 분석")

    currency = "원" if market == "한국장" else "$"

    # 이동평균 계산
    hist["SMA_50"] = hist["Close"].rolling(window=50).mean()
    hist["SMA_200"] = hist["Close"].rolling(window=200).mean()

    # 캔들차트 추가
    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=False,  # 각 서브플롯마다 x축 표시
        vertical_spacing=0.09,
        subplot_titles=("캔들차트", "MACD", "RSI", "거래량"),
        row_heights=[0.5, 0.2, 0.2, 0.2],  # 각 그래프의 높이 비율을 조정합니다
    )

    # 캔들차트
    fig.add_trace(
        go.Candlestick(
            x=hist.index,
            open=hist["Open"],
            high=hist["High"],
            low=hist["Low"],
            close=hist["Close"],
            name="캔들차트",
            increasing_line_color="red",
            decreasing_line_color="blue",
        ),
        row=1,
        col=1,
    )

    # 이동평균선 추가
    fig.add_trace(
        go.Scatter(
            x=hist.index,
            y=hist["SMA_50"],
            name="50일 이동평균",
            line=dict(color="orange", width=1),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=hist.index,
            y=hist["SMA_200"],
            name="200일 이동평균",
            line=dict(color="purple", width=1),
        ),
        row=1,
        col=1,
    )

    # 지지선과 저항선 추가
    if isinstance(technical_data, dict):
        support_level = technical_data.get("지지선")
        resistance_level = technical_data.get("저항선")
        if support_level and not isinstance(support_level, str):
            fig.add_hline(
                y=support_level, line_dash="dash", line_color="green", row=1, col=1
            )
        if resistance_level and not isinstance(resistance_level, str):
            fig.add_hline(
                y=resistance_level, line_dash="dash", line_color="red", row=1, col=1
            )

    # MACD
    macd = ta.trend.MACD(hist["Close"])
    hist["MACD"] = macd.macd()
    hist["MACD_Signal"] = macd.macd_signal()
    hist["MACD_Hist"] = macd.macd_diff()

    fig.add_trace(
        go.Scatter(x=hist.index, y=hist["MACD"], name="MACD", line=dict(color="blue")),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=hist.index,
            y=hist["MACD_Signal"],
            name="Signal Line",
            line=dict(color="red"),
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=hist.index,
            y=hist["MACD_Hist"],
            name="MACD Histogram",
            marker_color="green",
        ),
        row=2,
        col=1,
    )

    # RSI
    rsi = ta.momentum.RSIIndicator(hist["Close"]).rsi()
    hist["RSI"] = rsi

    fig.add_trace(
        go.Scatter(x=hist.index, y=hist["RSI"], name="RSI", line=dict(color="purple")),
        row=3,
        col=1,
    )
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

    # 거래량
    if "Volume" in hist.columns:
        fig.add_trace(
            go.Bar(
                x=hist.index,
                y=hist["Volume"],
                name="거래량",
                marker_color="orange",
                opacity=0.5,
            ),
            row=4,
            col=1,
        )
    else:
        st.warning("거래량 데이터를 가져올 수 없습니다.")

    # 각 서브플롯의 x축 레이블 표시
    for i in range(1, 5):
        fig.update_xaxes(row=i, col=1, showticklabels=True)

    # 레이아웃 업데이트
    fig.update_layout(
        height=1500,
        title_text=f"{company} 기술적 분석",
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )

    # y축 레이블 설정
    fig.update_yaxes(title_text="가격", row=1, col=1)
    fig.update_yaxes(title_text="MACD", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1)
    fig.update_yaxes(title_text="거래량", row=4, col=1)

    st.plotly_chart(fig, use_container_width=True)

    # 가격 제안 정보 표시
    st.subheader("가격 제안")
    current_price = hist["Close"].iloc[-1]

    def format_price(price):
        if market == "한국장":
            return f"{price:,.0f}{currency}"
        else:
            return f"{currency}{price:,.2f}"

    st.write(f"현재 가격: {format_price(current_price)}")

    # 기본 가격 제안 계산
    buy_price = current_price * 0.95
    take_profit_price = current_price * 1.1
    stop_loss_price = current_price * 0.9

    if isinstance(technical_data, dict):
        for price_type, default_value in [
            ("추천 구매 가격", buy_price),
            ("추천 익절 가격", take_profit_price),
            ("추천 손절 가격", stop_loss_price),
        ]:
            price = technical_data.get(price_type, default_value)
            if price != "정보 없음" and not isinstance(price, str):
                change_percent = (price / current_price - 1) * 100
                st.write(
                    f"{price_type}: {format_price(price)} (현재 가격 대비 {change_percent:.2f}%)"
                )
            else:
                st.write(f"{price_type}: {format_price(default_value)} (기본 추천)")

        price_suggestion = technical_data.get("가격_제안_근거", "")
        if price_suggestion:
            st.write("가격 제안 근거:")
            st.write(price_suggestion)

    else:
        st.write(f"추천 구매 가격: {format_price(buy_price)} (현재 가격 대비 -5%)")
        st.write(
            f"추천 익절 가격: {format_price(take_profit_price)} (현재 가격 대비 +10%)"
        )
        st.write(
            f"추천 손절 가격: {format_price(stop_loss_price)} (현재 가격 대비 -10%)"
        )
        st.write(
            "주의: 이 가격 제안은 기본적인 계산에 기반합니다. 실제 투자 결정 시 추가적인 분석이 필요합니다."
        )

    # 각 그래프에 대한 설명을 토글로 추가
    with st.expander("캔들차트 설명"):
        st.markdown(
            """
        **캔들차트**: 시가, 고가, 저가, 종가를 시각화하여 가격 변동을 한눈에 보여줍니다.
        - 빨간색(양봉): 종가가 시가보다 높을 때
        - 파란색(음봉): 종가가 시가보다 낮을 때
        - 이동평균선: 50일(주황색), 200일(보라색) 이동평균선을 표시하여 추세를 파악합니다.
        """
        )

    with st.expander("MACD 설명"):
        st.markdown(
            """
        **MACD**: 단기와 장기 추세의 차이를 나타냅니다. 추세 전환을 예측하는 데 사용됩니다.
        - MACD 라인: 12일 지수이동평균에서 26일 지수이동평균을 뺀 값
        - Signal 라인: MACD의 9일 지수이동평균
        - MACD Histogram: MACD 라인과 Signal 라인의 차이
        """
        )

    with st.expander("RSI 설명"):
        st.markdown(
            """
        **RSI**: 과매수/과매도 상태를 나타내는 지표입니다. 70 이상은 과매수, 30 이하는 과매도로 간주됩니다.
        - 0-100 사이의 값을 가지며, 일반적으로 14일 기준으로 계산
        - 70 이상: 과매수 상태로 가격 조정 가능성 존재
        - 30 이하: 과매도 상태로 반등 가능성 존재
        """
        )

    with st.expander("거래량 설명"):
        st.markdown(
            """
        **거래량**: 주식의 거래 활성도를 나타냅니다. 가격 변동과 함께 해석하여 추세의 강도를 판단합니다.
        - 가격 상승 + 거래량 증가: 강한 상승 추세
        - 가격 하락 + 거래량 증가: 강한 하락 추세
        - 가격 변동 + 거래량 감소: 현재 추세의 약화 가능성
        """
        )


def display_agent_analysis(results):
    st.header("에이전트 상세 분석")
    for i, (agent_name, analysis) in enumerate(results.items()):
        with st.expander(f"{agent_name} 분석"):
            st.write(analysis)


def format_value(value):
    if isinstance(value, float):
        return f"{value:.2f}"
    elif isinstance(value, int):
        return f"{value:,}"
    return str(value)


def display_financial_metrics(additional_data):
    st.header("주요 재무 지표")
    for key, value in additional_data.items():
        st.metric(label=key, value=format_value(value))


if __name__ == "__main__":
    main()
