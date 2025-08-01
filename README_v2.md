# AI 투자 자문 시스템 v2.0

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.12](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/release/python-3120/)

## 🚀 새로운 기능 (v2.0)

### 🏗️ 완전히 재설계된 아키텍처
- **모듈화된 구조**: 2000줄 단일 파일에서 체계적인 패키지 구조로 전환
- **확장 가능한 설계**: 새로운 기능 추가가 용이한 플러그인 아키텍처
- **성능 최적화**: 캐싱 시스템과 병렬 처리로 응답 속도 향상

### ⚡ 향상된 기능들
- **스마트 캐싱**: 15분 파일 기반 캐시로 API 호출 최소화
- **동적 가격 목표**: 변동성 기반 지능형 매매 신호
- **병렬 AI 분석**: 여러 에이전트가 동시에 분석 수행
- **포괄적인 검증**: 모든 사용자 입력에 대한 철저한 검증

### 📊 새로운 분석 도구
- **고급 기술 지표**: 볼린저 밴드, 스토캐스틱, ATR 등 추가
- **섹터 성과 분석**: 시장 섹터별 성과 비교
- **리스크 메트릭스**: VaR, 최대 낙폭, 변동성 분석

## 📋 목차
- [프로젝트 개요](#프로젝트-개요)
- [주요 기능](#주요-기능)
- [시스템 아키텍처](#시스템-아키텍처)
- [설치 방법](#설치-방법)
- [사용 방법](#사용-방법)
- [프로젝트 구조](#프로젝트-구조)
- [환경 설정](#환경-설정)
- [개발자 가이드](#개발자-가이드)

## 프로젝트 개요

AI 투자 자문 시스템은 여러 전문가 AI 에이전트를 활용하여 주식 투자에 대한 종합적인 분석과 조언을 제공하는 시스템입니다. 미국 및 한국 주식 시장을 모두 지원합니다.

## 주요 기능

### 🤖 6개의 전문 AI 에이전트
1. **기업 분석가**: 재무제표, 경영 전략, 시장 포지션 분석
2. **산업 전문가**: 산업 트렌드, 기술 발전, 규제 환경 평가
3. **거시경제 전문가**: 경제 지표, 금리, 인플레이션 영향 분석
4. **기술 분석가**: 차트 패턴, 기술적 지표, 매매 신호 분석
5. **리스크 관리자**: 투자 위험 평가 및 리스크 관리 전략
6. **중재자**: 모든 분석을 종합하여 최종 투자 의견 제시

### 📈 종합적인 분석 기능
- 실시간 주가 데이터 및 과거 데이터 분석
- 50+ 기술적 지표 계산 및 시각화
- 재무 비율 분석 및 동종업계 비교
- 경제 지표와 시장 상관관계 분석
- 인터랙티브 차트 및 대시보드

### 🌍 다중 시장 지원
- **미국 시장**: NYSE, NASDAQ 상장 주식
- **한국 시장**: KOSPI, KOSDAQ 상장 주식
- 시장별 특화된 데이터 소스 및 분석

## 시스템 아키텍처

```
investment_advisor/
├── agents/          # AI 에이전트 모듈
│   ├── base.py     # 기본 에이전트 클래스
│   ├── company_analyst.py
│   ├── industry_expert.py
│   ├── macroeconomist.py
│   ├── technical_analyst.py
│   ├── risk_manager.py
│   └── mediator.py
├── data/           # 데이터 수집 모듈
│   ├── base.py    # 캐싱 시스템 포함
│   ├── korea_stock.py
│   ├── us_stock.py
│   └── economic_data.py
├── analysis/       # 분석 엔진
│   ├── technical.py
│   ├── fundamental.py
│   └── decision_system.py
├── ui/            # UI 컴포넌트
│   ├── charts.py
│   ├── metrics.py
│   └── layouts.py
└── utils/         # 유틸리티
    ├── config.py
    ├── formatters.py
    ├── validators.py
    └── logging.py
```

## 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/yourusername/ai-investment-advisor.git
cd ai-investment-advisor
```

### 2. 가상 환경 생성
```bash
conda create -n stock python=3.12
conda activate stock
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
`.env` 파일을 생성하고 다음 내용을 추가:
```env
# 필수
OPENAI_API_KEY=your_openai_api_key

# 선택 (권장)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
LANGCHAIN_TRACING_V2=false
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langchain_key

# 설정
USE_CACHE=true
CACHE_DURATION_MINUTES=15
DEFAULT_MODEL=gpt-4o-mini-2024-07-18
MODEL_TEMPERATURE=0.1
```

## 사용 방법

### 1. 애플리케이션 실행
```bash
streamlit run main.py
```

### 2. 웹 브라우저에서 접속
기본적으로 http://localhost:8501 에서 실행됩니다.

### 3. 분석 수행
1. 시장 선택 (미국/한국)
2. 티커 입력 (예: AAPL, 005930)
3. 산업 분류 선택
4. 분석 기간 설정
5. '분석 시작' 클릭

## 환경 설정

### 필수 환경 변수
- `OPENAI_API_KEY`: OpenAI API 접근 키

### 선택적 환경 변수
- `ALPHA_VANTAGE_API_KEY`: 경제 지표 데이터용
- `USE_CACHE`: 캐싱 활성화 (기본: true)
- `CACHE_DURATION_MINUTES`: 캐시 유효 시간 (기본: 15)
- `DEFAULT_MODEL`: 사용할 AI 모델 (기본: gpt-4o-mini-2024-07-18)
- `MODEL_TEMPERATURE`: 모델 온도 설정 (기본: 0.1)
- `LOG_LEVEL`: 로깅 레벨 (기본: INFO)

## 개발자 가이드

### 새로운 에이전트 추가
```python
from investment_advisor.agents.base import InvestmentAgent

class NewAgent(InvestmentAgent):
    name = "새로운 에이전트"
    description = "새로운 분석 기능"
    
    def _run(self, *args, **kwargs):
        # 분석 로직 구현
        pass
```

### 새로운 데이터 소스 추가
```python
from investment_advisor.data.base import StockDataFetcher

class NewDataFetcher(StockDataFetcher):
    def fetch_price_history(self, ticker, start_date, end_date):
        # 데이터 수집 로직 구현
        pass
```

### 테스트 실행
```bash
pytest tests/
```

## 기술 스택

### 핵심 기술
- **Python 3.12+**: 메인 프로그래밍 언어
- **Streamlit**: 웹 애플리케이션 프레임워크
- **LangChain**: AI 에이전트 오케스트레이션
- **OpenAI GPT**: AI 분석 엔진

### 데이터 & 분석
- **yfinance**: 미국 주식 데이터
- **FinanceDataReader**: 한국 주식 데이터
- **pykrx**: 한국 거래소 데이터
- **pandas/numpy**: 데이터 처리
- **ta**: 기술적 지표 계산

### 시각화
- **Plotly**: 인터랙티브 차트
- **Matplotlib**: 정적 차트

## 라이선스

이 프로젝트는 Apache License 2.0 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 기여 방법

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 문의 및 지원

- 이슈 트래커: [GitHub Issues](https://github.com/yourusername/ai-investment-advisor/issues)
- 이메일: researcherhojin@gmail.com

## 변경 이력

### v2.0.0 (2024-08-01)
- 전체 아키텍처 리팩토링
- 모듈화 및 패키지 구조 도입
- 캐싱 시스템 추가
- 병렬 처리 구현
- 동적 가격 목표 설정
- 향상된 에러 처리

### v1.0.0 (초기 버전)
- 기본 AI 에이전트 시스템
- 미국/한국 시장 지원
- 기본 기술적/기본적 분석