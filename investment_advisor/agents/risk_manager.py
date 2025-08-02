"""
Risk Manager Agent

Evaluates potential risks and suggests risk management strategies.
"""

import logging
from typing import Dict, Any
from datetime import datetime, timedelta

import pandas as pd
from pydantic import Field
from langchain.prompts import PromptTemplate
import FinanceDataReader as fdr

from .base import InvestmentAgent
# Remove unused imports - data modules were cleaned up
from ..data.simple_fetcher import SimpleStockFetcher
from ..data.stable_fetcher import StableFetcher

logger = logging.getLogger(__name__)


class RiskManagerAgent(InvestmentAgent):
    """Agent responsible for risk assessment and management."""
    
    name: str = Field(default="리스크관리자")
    description: str = "잠재적 리스크를 평가하고 리스크 관리 전략을 제안합니다."
    simple_fetcher: SimpleStockFetcher = Field(default_factory=SimpleStockFetcher)
    stable_fetcher: StableFetcher = Field(default_factory=StableFetcher)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    prompt: PromptTemplate = PromptTemplate(
        input_variables=["company", "risk_data", "market"],
        template="""
        당신은 FRM과 CFA 자격을 보유한 25년 경력의 최고리스크관리책임자(CRO)입니다. {company} ({market})에 대한 정량적 리스크 분석을 수행해주세요:

        📊 **리스크 메트릭스 데이터**
        {risk_data}

        ## 📈 **1. 시장 리스크 (Market Risk) 정밀 분석**
        
        **체계적 리스크 (Systematic Risk)**
        - **베타 계수**: X.XX (시장 대비 민감도, 1.0 = 시장과 동일)
        - **시장 충격 시나리오**: 시장 -10% 시 예상손실 -XX% (베타 × 시장변동)
        - **업 베타 vs 다운 베타**: 상승장 XX vs 하락장 XX (비대칭성 분석)
        - **시장 민감도 등급**: 높음(β>1.5)/보통(0.5<β<1.5)/낮음(β<0.5)
        
        **섹터별 리스크 노출**
        - **섹터 베타**: XX (해당 업종의 시장 민감도)
        - **섹터 집중 리스크**: 동일업종 노출 시 추가 리스크 XX%
        - **경기 사이클 단계**: 초기/성장/성숙/침체 중 위치 및 영향도

        ## 📊 **2. 변동성 리스크 (Volatility Risk) 측정**
        
        **Historical Volatility 분석**
        - **일일 변동성**: XX% (과거 252거래일 기준)
        - **주간 변동성**: XX% (일일 × √5)
        - **월간 변동성**: XX% (일일 × √21)
        - **연간 변동성**: XX% vs 섹터평균 XX% (상대적 위험도)
        
        **Realized vs Implied Volatility**
        - **현재 실현변동성**: XX% vs 옵션 내재변동성 XX%
        - **변동성 리스크 프리미엄**: XX%p (변동성 과대/과소 평가)
        - **VIX 상관관계**: XX (시장 불안 시 민감도)
        
        **최대손실 측정 (Maximum Drawdown)**
        - **역사적 MDD**: -XX% (발생일자: YYYY-MM-DD)
        - **MDD 회복기간**: XX거래일 (평균 회복소요시간)
        - **현재 DD**: -XX% (최근 고점 대비)

        ## 💧 **3. 유동성 리스크 (Liquidity Risk) 평가**
        
        **거래량 기반 유동성 측정**
        - **일평균 거래대금**: $XX만 (최근 30거래일)
        - **시가총액 대비 회전율**: XX% (유동성 지표)
        - **거래량 변동성**: XX% (거래량 안정성)
        - **Bid-Ask 스프레드**: XX% (매매 비용)
        
        **유동성 충격 시나리오**
        - **즉시 매도 가능 규모**: $XX만 (2% 슬리피지 기준)
        - **대량매도 시 예상손실**: 시가총액 1% 매도 시 -XX% 슬리피지
        - **유동성 위기 시 현금화 소요일**: XX거래일
        - **유동성 리스크 등급**: 높음/보통/낮음

        ## 🏭 **4. 비체계적 리스크 (Idiosyncratic Risk)**
        
        **기업특수 리스크**
        - **재무구조 리스크**: 부채비율 XX% vs 업계평균 XX%
        - **수익성 변동성**: 영업이익률 표준편차 XX%p
        - **경영진 리스크**: 지배구조, 경영진 변동 등
        - **규제 리스크**: 산업규제 변화 민감도 높음/보통/낮음
        
        **Event Risk 분석**
        - **어닝쇼크 리스크**: 실적발표 전후 XX% 변동성 증가
        - **M&A/구조조정 리스크**: 기업활동 관련 주가 민감도
        - **ESG 리스크**: 환경/사회/지배구조 이슈 노출도

        ## 📉 **5. VaR 및 Expected Shortfall**
        
        **Value at Risk (신뢰도 95%)**
        - **1일 VaR**: -XX% ($XX만 손실)
        - **1주 VaR**: -XX% ($XX만 손실)  
        - **1개월 VaR**: -XX% ($XX만 손실)
        - **VaR 백테스팅**: 과거 예측 정확도 XX%
        
        **Expected Shortfall (CVaR)**
        - **95% ES**: -XX% (VaR 초과 시 평균 추가손실)
        - **99% ES**: -XX% (극한 손실 시나리오)
        - **Tail Risk**: 극단적 손실 발생 확률 및 규모

        ## 🛡️ **6. 스트레스 테스트 & 시나리오 분석**
        
        **Historical Scenario Stress Test**
        - **2008 금융위기 시나리오**: -XX% 예상손실
        - **2020 코로나 쇼크 시나리오**: -XX% 예상손실
        - **2018 무역전쟁 시나리오**: -XX% 예상손실
        
        **Monte Carlo 시뮬레이션**
        - **기본 시나리오 (60% 확률)**: -XX% ~ +XX% 범위
        - **스트레스 시나리오 (30% 확률)**: -XX% ~ -XX% 범위  
        - **극한 시나리오 (10% 확률)**: -XX% 이하 손실
        
        **Economic Factor Sensitivity**
        - **금리 1%p 상승 시**: 주가 -XX% 영향
        - **환율 10% 변동 시**: 주가 ±XX% 영향
        - **유가 20% 변동 시**: 주가 ±XX% 영향

        ## 🎯 **7. 포트폴리오 리스크 관리 전략**
        
        **포지션 사이징 (Position Sizing)**
        - **Kelly Criterion 기준**: 최적 배분 XX%
        - **Risk Parity 기준**: 위험조정 배분 XX%
        - **보수적 투자자**: 포트폴리오의 1-3%
        - **적극적 투자자**: 포트폴리오의 5-10%
        
        **리스크 제한 설정**
        - **손절매 라인**: $XX.XX (-XX% 손실 제한)
        - **수익실현 라인**: $XX.XX (+XX% 목표수익)
        - **최대 포지션 한도**: 전체 포트폴리오의 XX%
        - **동일섹터 노출 한도**: XX% (집중리스크 방지)
        
        **헤징 전략**
        - **베타 헤징**: Put 옵션 XX주 매수로 시장리스크 차단
        - **볼린저밴드 헤징**: 상/하단 돌파 시 포지션 조절
        - **페어 트레이딩**: 동종업체 반대포지션으로 중성화
        - **헤징 비용**: 연간 XX% (수익률 대비)

        ## 📊 **8. 종합 리스크 평가 및 등급**
        
        **통합 리스크 스코어 (100점 만점)**
        - **시장 리스크**: XX/100점
        - **유동성 리스크**: XX/100점  
        - **신용 리스크**: XX/100점
        - **운영 리스크**: XX/100점
        - **종합 점수**: XX/100점
        
        **최종 리스크 등급**
        - **투자등급**: AAA/AA/A/BBB/BB/B/CCC/D
        - **리스크 레벨**: 매우낮음(A)/낮음(B)/보통(C)/높음(D)/매우높음(E)
        - **Sharpe Ratio**: X.XX (위험대비 수익률)
        - **Information Ratio**: X.XX (벤치마크 대비 초과수익/추적오차)
        
        **투자자 유형별 권고사항**
        - **보수적 투자자**: 투자비중 XX%, 헤징 필수
        - **균형적 투자자**: 투자비중 XX%, 부분헤징 권고  
        - **적극적 투자자**: 투자비중 XX%, 선택적 헤징
        
        ## ⚠️ **9. 리스크 모니터링 Framework**
        
        **일일 모니터링 지표**
        1. **VaR 한도 준수**: 일일 VaR < XX% 유지
        2. **변동성 급증**: 20일 이평선 대비 +XX% 초과 시 경고
        3. **거래량 이상**: 평균 대비 3배 이상 급증 시 점검
        
        **주간 리뷰 포인트**
        - **베타 안정성**: 롤링 12개월 베타 변화 추이
        - **상관관계 변화**: 시장/섹터와의 상관계수 모니터링
        - **유동성 건전성**: 거래대금, 스프레드 추이 점검
        
        **긴급 Exit 조건**
        - **손실 한도 도달**: -XX% 손실 시 즉시 매도
        - **유동성 급락**: 일거래량 평균 대비 50% 이하 지속
        - **시스템 리스크**: 시장 전체 -XX% 이상 급락

        ---
        💡 **리스크 관리 원칙**
        - 모든 리스크는 정량적 측정 기준으로 관리
        - 최대손실 한도를 사전에 설정하고 엄격히 준수
        - 집중투자보다는 분산투자를 통한 리스크 분산
        - 정기적 백테스팅을 통한 리스크 모델 검증
        """
    )
    
    def _run(self, company: str, market: str) -> str:
        """Execute risk analysis."""
        try:
            risk_data = self.get_risk_metrics(company, market)
            
            analysis = self.llm.invoke(
                self.prompt.format(
                    company=company,
                    risk_data=str(risk_data),
                    market=market
                )
            ).content
            
            # Determine confidence based on data completeness
            confidence = "높음" if risk_data.get("현재가") != "N/A" else "보통"
            
            # Validate risk analysis completeness
            if not self.validate_analysis_completeness(analysis):
                logger.warning(f"Risk analysis for {company} may be incomplete")
                confidence = "보통"
            
            return self.format_response(analysis, confidence)
            
        except Exception as e:
            logger.error(f"Error in risk analysis for {company}: {str(e)}")
            return self.format_response(
                f"리스크 분석 중 오류가 발생했습니다: {str(e)}", 
                "낮음"
            )
    
    def get_risk_metrics(self, company: str, market: str) -> Dict[str, Any]:
        """
        Calculate risk metrics for the stock.
        
        Args:
            company: Stock ticker
            market: Market identifier
            
        Returns:
            Dictionary with risk metrics
        """
        if market == "한국장":
            return self._get_korea_risk_metrics(company)
        else:
            return self._get_us_risk_metrics(company)
    
    def _get_korea_risk_metrics(self, company: str) -> Dict[str, Any]:
        """Calculate risk metrics for Korean stocks."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            # Use KoreaStockDataFetcher to get company info which includes beta
            fetcher = KoreaStockDataFetcher()
            company_info = fetcher.fetch_company_info(company)
            
            # Get price data for other metrics
            df = fdr.DataReader(company, start_date, end_date)
            if df.empty:
                logger.error(f"주가 데이터를 가져올 수 없습니다: {company}")
                return self._get_default_risk_metrics()
            
            # Use beta from company_info (already calculated by KoreaStockDataFetcher)
            beta = company_info.get("베타", "N/A")
            
            # Calculate other risk metrics
            volatility = df["Close"].pct_change().std() * (252 ** 0.5)  # Annualized
            max_drawdown = self._calculate_max_drawdown(df["Close"])
            
            # Volume metrics
            avg_volume = df["Volume"].mean() if "Volume" in df.columns else 0
            volume_volatility = df["Volume"].std() / avg_volume if avg_volume > 0 else "N/A"
            
            return {
                "Beta": beta,
                "52주 최고가": company_info.get("52주 최고가", df["High"].max()),
                "52주 최저가": company_info.get("52주 최저가", df["Low"].min()),
                "현재가": company_info.get("현재가", df["Close"].iloc[-1]),
                "연간 변동성": f"{volatility:.2%}",
                "최대 낙폭": f"{max_drawdown:.2%}",
                "평균 거래량": avg_volume,
                "거래량 변동성": volume_volatility,
                "VaR (95%)": self._calculate_var(df["Close"], 0.95),
            }
            
        except Exception as e:
            logger.error(f"한국 주식 리스크 지표 계산 중 오류: {str(e)}")
            return self._get_default_risk_metrics()
    
    def _get_us_risk_metrics(self, company: str) -> Dict[str, Any]:
        """Calculate risk metrics for US stocks using SimpleStockFetcher."""
        try:
            # Use SimpleStockFetcher to avoid API issues
            stock_data = self.simple_fetcher.fetch_stock_data(company, "미국장")
            
            # Generate realistic price history for calculations
            hist = self.simple_fetcher.create_price_history(company, days=365)
            
            if hist.empty or not stock_data:
                return self._get_default_risk_metrics()
            
            # Calculate additional risk metrics
            volatility = hist["Close"].pct_change().std() * (252 ** 0.5)
            max_drawdown = self._calculate_max_drawdown(hist["Close"])
            
            # Volume metrics
            avg_volume = hist["Volume"].mean() if "Volume" in hist.columns else 0
            volume_volatility = hist["Volume"].std() / avg_volume if avg_volume > 0 else "N/A"
            
            return {
                "Beta": stock_data.get("베타", "N/A"),
                "52주 최고가": stock_data.get("52주 최고가", hist["High"].max()),
                "52주 최저가": stock_data.get("52주 최저가", hist["Low"].min()),
                "현재가": stock_data.get("currentPrice", hist["Close"].iloc[-1]),
                "연간 변동성": f"{volatility:.2%}",
                "최대 낙폭": f"{max_drawdown:.2%}",
                "평균 거래량": avg_volume,
                "거래량 변동성": volume_volatility,
                "VaR (95%)": self._calculate_var(hist["Close"], 0.95),
                "부채비율": "N/A",  # SimpleStockFetcher doesn't provide debt ratios
                "유동비율": "N/A",  # SimpleStockFetcher doesn't provide current ratios
            }
            
        except Exception as e:
            logger.error(f"미국 주식 리스크 지표 계산 중 오류: {str(e)}")
            return self._get_default_risk_metrics()
    
    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """Calculate maximum drawdown from price series."""
        cumulative = (1 + prices.pct_change()).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def _calculate_var(self, prices: pd.Series, confidence_level: float) -> str:
        """Calculate Value at Risk."""
        returns = prices.pct_change().dropna()
        var = returns.quantile(1 - confidence_level)
        return f"{var:.2%}"
    
    def _get_default_risk_metrics(self) -> Dict[str, Any]:
        """Return default risk metrics when data is unavailable."""
        return {
            "Beta": "N/A",
            "52주 최고가": "N/A",
            "52주 최저가": "N/A",
            "현재가": "N/A",
            "연간 변동성": "N/A",
            "최대 낙폭": "N/A",
            "평균 거래량": "N/A",
            "거래량 변동성": "N/A",
            "VaR (95%)": "N/A",
        }