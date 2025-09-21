"""
Investment Decision System

Orchestrates all agents and analysis components to make investment decisions.
"""

import logging
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import streamlit as st

from ..agents import (
    CompanyAnalystAgent,
    IndustryExpertAgent,
    MacroeconomistAgent,
    TechnicalAnalystAgent,
    RiskManagerAgent,
    MediatorAgent
)
from ..data.stable_fetcher import StableFetcher
from ..data.simple_fetcher import SimpleStockFetcher
from ..data.yahoo_fetcher import YahooFetcher
from ..utils import get_config

logger = logging.getLogger(__name__)


class InvestmentDecisionSystem:
    """Main system that orchestrates all investment analysis components."""

    def __init__(self):
        self.config = get_config()

        # Initialize data fetchers - Yahoo as primary, Stable as fallback
        try:
            self.yahoo_fetcher = YahooFetcher(cache_ttl=60)
            logger.info("Using Yahoo Finance as primary data source")
        except Exception as e:
            self.yahoo_fetcher = None
            logger.warning(f"Yahoo Finance unavailable: {e}")

        self.stable_fetcher = StableFetcher(use_cache=self.config.use_cache)
        self.simple_fetcher = SimpleStockFetcher()

        # Set primary fetcher
        self.primary_fetcher = self.yahoo_fetcher if self.yahoo_fetcher else self.stable_fetcher

        # Initialize agents
        self._initialize_agents()

        logger.info("Investment Decision System initialized")

    def _initialize_agents(self):
        """Initialize all AI agents."""
        model_config = self.config.get_model_config()

        # Create agent instances for each market
        self.agents = {
            "미국장": {
                "기업분석가": CompanyAnalystAgent(**model_config),
                "산업전문가": IndustryExpertAgent(**model_config),
                "거시경제전문가": MacroeconomistAgent(
                    alpha_vantage_api_key=self.config.alpha_vantage_api_key,
                    **model_config
                ),
                "기술분석가": TechnicalAnalystAgent(**model_config),
                "리스크관리자": RiskManagerAgent(**model_config),
                "중재자": MediatorAgent(**model_config),
            },
            "한국장": {
                "기업분석가": CompanyAnalystAgent(**model_config),
                "산업전문가": IndustryExpertAgent(**model_config),
                "거시경제전문가": MacroeconomistAgent(
                    alpha_vantage_api_key=self.config.alpha_vantage_api_key,
                    **model_config
                ),
                "기술분석가": TechnicalAnalystAgent(**model_config),
                "리스크관리자": RiskManagerAgent(**model_config),
                "중재자": MediatorAgent(**model_config),
            }
        }

    def make_decision(
        self,
        ticker: str,
        industry: str,
        market: str,
        analysis_period: int = 12,
        progress_callback: Optional[callable] = None
    ) -> Tuple[str, Dict[str, str], Dict[str, Any], pd.DataFrame]:
        """
        Make comprehensive investment decision.

        Args:
            ticker: Stock ticker symbol
            industry: Industry category
            market: Market identifier
            analysis_period: Analysis period in months
            progress_callback: Optional callback for progress updates

        Returns:
            Tuple of (final_decision, agent_results, analysis_data, price_history)
        """
        logger.info(f"Starting analysis for {ticker} in {market}")

        try:
            # Fetch stock data
            stock_data, price_history = self._fetch_stock_data(
                ticker, market, analysis_period
            )

            if stock_data is None or price_history.empty:
                error_msg = f"Unable to fetch data for {ticker}"
                logger.error(error_msg)
                return None, None, {"error": error_msg}, pd.DataFrame()

            # Run technical and fundamental analysis
            analysis_results = self._run_analyses(
                ticker, market, stock_data, price_history
            )

            # Run agent analysis
            agent_results = self._run_agent_analysis(
                ticker, industry, market, stock_data,
                analysis_results, progress_callback
            )

            if agent_results is None:
                return None, None, {"error": "Analysis interrupted"}, price_history

            # Get final decision from mediator
            final_decision = self._get_final_decision(agent_results, market)

            # Compile all analysis data
            analysis_data = self._compile_analysis_data(
                stock_data, analysis_results, agent_results
            )

            logger.info(f"Analysis completed for {ticker}")

            return final_decision, agent_results, analysis_data, price_history

        except Exception as e:
            logger.error(f"Error in make_decision: {str(e)}", exc_info=True)
            return None, None, {"error": str(e)}, pd.DataFrame()

    def fetch_stock_data(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime
    ) -> Tuple[Dict[str, Any], pd.DataFrame]:
        """Public method to fetch stock data."""
        return self._fetch_stock_data_internal(ticker, start_date, end_date)
    
    def _fetch_stock_data_internal(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime
    ) -> Tuple[Dict[str, Any], pd.DataFrame]:
        """Internal method to fetch stock data from Yahoo Finance with fallback."""
        try:
            # Try Yahoo Finance first (real data)
            if self.yahoo_fetcher:
                try:
                    logger.info(f"Fetching real data for {ticker} using Yahoo Finance")
                    
                    # Get quote data
                    quote_data = self.yahoo_fetcher.fetch_quote(ticker)
                    
                    # Get price history
                    price_history = self.yahoo_fetcher.fetch_price_history(ticker, start_date, end_date)
                    
                    # Get financial data
                    financial_data = self.yahoo_fetcher.fetch_financial_data(ticker)
                    
                    if quote_data and not price_history.empty:
                        company_info = self.yahoo_fetcher.fetch_company_info(ticker)
                        
                        stock_data = {
                            **quote_data,
                            **company_info,
                            **financial_data,
                            'fetcher': 'yahoo'
                        }
                        
                        logger.info(f"Successfully fetched real data for {ticker} from Yahoo Finance")
                        return stock_data, price_history
                        
                except Exception as e:
                    logger.debug(f"Yahoo Finance failed for {ticker}: {e}")
            
            # Fallback to StableFetcher
            logger.info(f"Using StableFetcher as fallback for {ticker}")
            
            quote_data = self.stable_fetcher.fetch_quote(ticker)
            price_history = self.stable_fetcher.fetch_price_history(ticker, start_date, end_date)
            financial_data = self.stable_fetcher.fetch_financial_data(ticker)
            company_info = self.stable_fetcher.fetch_company_info(ticker)
            
            stock_data = {
                **quote_data,
                **financial_data,
                **company_info,
                'fetcher': 'stable'
            }
            
            return stock_data, price_history
            
        except Exception as e:
            logger.error(f"Failed to fetch stock data for {ticker}: {e}")
            raise Exception(f"데이터 수집 실패: {str(e)}")
    
    def _fetch_stock_data(
        self,
        ticker: str,
        market: str,
        analysis_period: int
    ) -> Tuple[Dict[str, Any], pd.DataFrame]:
        """Old method for compatibility - redirects to new method."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=analysis_period * 30)
        return self._fetch_stock_data_internal(ticker, start_date, end_date)

    def _run_analyses(
        self,
        ticker: str,
        market: str,
        stock_data: Dict[str, Any],
        price_history: pd.DataFrame
    ) -> Dict[str, Any]:
        """Run technical and fundamental analyses."""
        results = {}

        try:
            # Technical analysis is now handled by TechnicalAnalystAgent
            # Store price data for visualization
            results["technical_viz_data"] = {
                'price_history': price_history,
                'ticker': ticker
            }

            # Analysis is now handled by agents - no separate analyzer needed
            # Store basic data for agents to use
            results["stock_info"] = stock_data

        except Exception as e:
            logger.error(f"Error in analyses: {str(e)}")

        return results

    def _run_agent_analysis(
        self,
        ticker: str,
        industry: str,
        market: str,
        stock_data: Dict[str, Any],
        analysis_results: Dict[str, Any],
        progress_callback: Optional[callable] = None
    ) -> Optional[Dict[str, str]]:
        """Run all agent analyses in parallel where possible."""
        results = {}
        agents = self.agents[market]

        # Update progress
        if progress_callback:
            progress_callback("Starting agent analysis...", 0)

        try:
            # Run analyses in parallel using ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=4) as executor:
                # Submit agent tasks
                futures = {}

                # Company Analyst - pass stock_data for accurate financials
                futures[executor.submit(
                    agents["기업분석가"]._run, ticker, market, stock_data
                )] = "기업분석가"

                # Industry Expert
                futures[executor.submit(
                    agents["산업전문가"]._run, industry, market
                )] = "산업전문가"

                # Macroeconomist
                futures[executor.submit(
                    agents["거시경제전문가"]._run, market, market
                )] = "거시경제전문가"

                # Technical Analyst
                futures[executor.submit(
                    agents["기술분석가"]._run, ticker, market
                )] = "기술분석가"

                # Risk Manager
                futures[executor.submit(
                    agents["리스크관리자"]._run, ticker, market
                )] = "리스크관리자"

                # Process completed futures
                completed = 0
                total = len(futures)

                for future in as_completed(futures):
                    agent_name = futures[future]

                    try:
                        result = future.result(timeout=30)
                        results[agent_name] = result
                        completed += 1

                        if progress_callback:
                            progress = int((completed / total) * 100)
                            progress_callback(
                                f"{agent_name} 분석 완료 ({completed}/{total})",
                                progress
                            )

                    except Exception as e:
                        logger.error(f"Error in {agent_name}: {str(e)}")
                        results[agent_name] = f"분석 실패: {str(e)}"

            return results

        except Exception as e:
            logger.error(f"Error in agent analysis: {str(e)}")
            return None

    def _get_final_decision(
        self,
        agent_results: Dict[str, str],
        market: str
    ) -> str:
        """Get final decision from mediator agent."""
        try:
            mediator = self.agents[market]["중재자"]

            # Prepare inputs for mediator
            mediator_inputs = {
                "company_analysis": agent_results.get("기업분석가", "분석 없음"),
                "industry_analysis": agent_results.get("산업전문가", "분석 없음"),
                "macro_analysis": agent_results.get("거시경제전문가", "분석 없음"),
                "technical_analysis": agent_results.get("기술분석가", "분석 없음"),
                "risk_analysis": agent_results.get("리스크관리자", "분석 없음"),
                "market": market
            }

            final_decision = mediator._run(mediator_inputs)

            return final_decision

        except Exception as e:
            logger.error(f"Error getting final decision: {str(e)}")
            return "최종 투자 의견을 생성할 수 없습니다."

    def _compile_analysis_data(
        self,
        stock_data: Dict[str, Any],
        analysis_results: Dict[str, Any],
        agent_results: Dict[str, str]
    ) -> Dict[str, Any]:
        """Compile all analysis data into a single dictionary."""
        return {
            "stock_info": stock_data,
            "technical_analysis": analysis_results.get("technical", {}),
            "fundamental_analysis": analysis_results.get("fundamental", {}),
            "price_targets": analysis_results.get("price_targets", {}),
            "economic_indicators": analysis_results.get("economic", {}),
            "agent_analyses": agent_results,
            "timestamp": datetime.now().isoformat()
        }

    def get_recommendations(
        self,
        ticker: str,
        market: str,
        recommendation_type: str = "similar"
    ) -> pd.DataFrame:
        """
        Get stock recommendations.

        Args:
            ticker: Current stock ticker
            market: Market identifier
            recommendation_type: Type of recommendations

        Returns:
            DataFrame with recommendations
        """
        try:
            if market == "한국장":
                # For Korean market, use stable fetcher
                try:
                    data = self.korea_fetcher.get_market_trading_data(datetime.now().strftime("%Y%m%d"))
                    if not data.empty:
                        recommendations = data[
                            (data.get("PER", 0) < 20) &
                            (data.get("거래량", 0) > 1000000)
                        ].head(5)
                        return recommendations
                except:
                    # Fallback to mock Korean recommendations
                    korean_stocks = ['005930', '000660', '207940', '006400', '051910']
                    recommendations = pd.DataFrame({
                        'Code': korean_stocks,
                        'Name': ['삼성전자', 'SK하이닉스', '삼성바이오로직스', '삼성SDI', 'LG화학'],
                        'Performance': ['2.1%', '1.8%', '3.2%', '0.9%', '1.5%'],
                        'Trend': ['상승', '상승', '상승', '상승', '상승']
                    })
                    return recommendations
            else:
                # For US market, use stable fetcher sector performance
                sector_data = self.stable_fetcher.get_sector_performance()

                # Convert to DataFrame
                if sector_data:
                    recommendations = pd.DataFrame.from_dict(
                        sector_data, orient='index'
                    ).reset_index()
                    recommendations.columns = ['Sector', 'Performance', 'Trend']
                    return recommendations

            return pd.DataFrame()

        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return pd.DataFrame()

    def update_agent_weights(self, performance_scores: Dict[str, float]):
        """
        Update agent weights based on performance.

        Args:
            performance_scores: Dictionary of agent -> performance score
        """
        for market_agents in self.agents.values():
            for agent_name, agent in market_agents.items():
                if agent_name in performance_scores and agent_name != "중재자":
                    agent.weight = performance_scores[agent_name]
                    logger.info(
                        f"Updated {agent_name} weight to {performance_scores[agent_name]}"
                    )
