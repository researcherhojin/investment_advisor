# AI 투자 자문 시스템 v0.2 (Beta)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.12](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.47.0-FF4B4B?logo=streamlit)](https://streamlit.io)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991?logo=openai)](https://openai.com)

## 🚀 프로젝트 개요

6개의 전문 AI 에이전트를 활용하여 미국 및 한국 주식 시장에 대한 종합적인 투자 분석과 자문을 제공하는 시스템입니다.

### 주요 특징

- **🤖 6개 전문 AI 에이전트**: 기업분석가, 기술분석가, 리스크관리자, 산업전문가, 거시경제학자, 중재자
- **📊 실시간 데이터**: Yahoo Finance API를 통한 정확한 실시간 주가 및 재무 데이터 (PER, PBR 등 정확한 지표)
- **🌍 글로벌 시장 지원**: 미국 및 한국 주식 시장 동시 지원
- **⚡ 고성능 아키텍처**: ThreadPoolExecutor 병렬 처리, 스마트 캐싱, Rate Limiting 대응
- **🎨 미니멀 UI**: 탭 기반의 깔끔하고 직관적인 사용자 인터페이스
- **📈 시각화**: Plotly 기반 인터랙티브 차트 (가격, 이동평균선, 기술적 지표)

## 📦 설치 방법

### 사전 요구사항

- Python 3.12 이상
- OpenAI API 키 (GPT-4 접근 권한 필요)

### 설치 단계

```bash
# 1. 저장소 클론
git clone https://github.com/yourusername/ai-investment-advisor.git
cd ai-investment-advisor

# 2. 빠른 설치 (권장)
bash scripts/quick_start.sh

# 또는 수동 설치:
# 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정 (.env 파일 생성)
cp .env.example .env
# .env 파일에 OPENAI_API_KEY 입력
```

## 🔑 환경 설정

`.env` 파일을 생성하고 API 키를 설정하세요:

```bash
# 필수 설정
OPENAI_API_KEY=sk-...  # OpenAI API 키

# 선택적 설정
DEFAULT_MODEL=gpt-4o-mini       # 기본 AI 모델 (gpt-4o-mini 권장)
MODEL_TEMPERATURE=0.1           # 모델 온도 (0.0-2.0, 낮을수록 일관성 높음)
MAX_TOKENS=800                  # 최대 토큰 수
USE_CACHE=true                  # 캐싱 활성화 (권장)
CACHE_DURATION_MINUTES=15       # 캐시 유효 시간
DEBUG_MODE=false                # 디버그 모드
LOG_LEVEL=INFO                  # 로그 레벨 (DEBUG, INFO, WARNING, ERROR)
```

## 🎮 사용 방법

### 애플리케이션 실행

```bash
# 빠른 실행 (스크립트 사용)
bash scripts/run.sh

# 또는 직접 실행
streamlit run main.py

# 또는 활성화된 가상환경에서
source .venv/bin/activate && streamlit run main.py
```

브라우저에서 http://localhost:8501 접속

### 사용 예시

1. **종목 코드 입력**

   - 미국: AAPL, GOOGL, TSLA, MSFT, NVDA
   - 한국: 005930 (삼성전자), 000660 (SK하이닉스), 035720 (카카오)

2. **시장 선택**: 미국장 또는 한국장

3. **분석 시작 클릭**: 약 30-45초 후 AI 분석 결과 확인

4. **결과 확인**:
   - 핵심 지표: 현재가, PER, PBR, 거래량
   - AI 투자 의견: BUY/SELL/HOLD 및 신뢰도
   - 상세 분석: 4개 탭에서 각 에이전트별 분석 확인

## 🏗 프로젝트 구조

```
ai-investment-advisor/
├── investment_advisor/             # 핵심 모듈
│   ├── agents/                     # AI 에이전트 모듈
│   │   ├── base.py                 # 에이전트 기본 클래스
│   │   ├── company_analyst.py      # 기업 재무 분석
│   │   ├── technical_analyst.py    # 기술적 차트 분석
│   │   ├── risk_manager.py         # 리스크 평가
│   │   ├── industry_expert.py      # 산업 동향 분석
│   │   ├── macroeconomist.py       # 거시경제 분석
│   │   └── mediator.py             # 종합 의사결정
│   ├── analysis/                   # 분석 엔진
│   │   └── decision_system.py      # 의사결정 시스템
│   ├── data/                       # 데이터 수집
│   │   ├── yahoo_fetcher.py        # Yahoo Finance 실시간 데이터
│   │   ├── stable_fetcher.py       # 안정적 백업 데이터
│   │   └── simple_fetcher.py       # 간단한 백업 데이터
│   ├── ui/                         # UI 컴포넌트
│   │   └── minimal_ui.py           # 미니멀 UI 컴포넌트
│   └── utils/                      # 유틸리티
│       ├── config.py               # 설정 관리
│       └── logging_config.py       # 로깅 설정
├── scripts/                        # 유틸리티 스크립트
│   ├── quick_start.sh              # 빠른 설치 스크립트
│   ├── run.sh                      # 실행 스크립트
│   └── setup_uv.sh                 # UV 설치 스크립트
├── tests/                          # 테스트 파일
├── main.py                         # 메인 애플리케이션
├── requirements.txt                # Python 패키지 목록
└── .env.example                    # 환경 변수 예제
```

## 🚀 주요 기능

### 1. 실시간 데이터 분석

- **Yahoo Finance API**: 실시간 주가 데이터 수집
- **정확한 재무 지표**: PER, PBR, ROE 등 실시간 계산 (예: TSLA PER 256.67)
- **52주 최고/최저가**: 현재 위치 파악
- **거래량 분석**: 평균 대비 현재 거래량 비교

### 2. AI 에이전트 분석 (GPT-4 기반)

#### 기업분석가

- 재무제표 분석 (수익성, 성장성, 안정성)
- 밸류에이션 평가 (PER, PBR, EV/EBITDA)
- 경쟁우위 분석 (Porter's 5 Forces)
- 목표주가 산정

#### 기술분석가

- 차트 패턴 인식 (상승/하락 추세)
- 이동평균선 분석 (20일, 50일, 200일)
- 모멘텀 지표 (RSI, MACD)
- 지지/저항선 계산

#### 리스크관리자

- 시장 리스크 평가 (Beta 계수)
- 변동성 측정 (일간/주간/연간)
- 최대손실 계산 (VaR, Maximum Drawdown)
- 유동성 리스크 평가

#### 산업전문가

- 산업 사이클 분석
- 경쟁 구조 평가
- 기술 혁신 동향
- 규제 환경 변화

#### 거시경제학자

- 경제 지표 영향 분석
- 금리 정책 영향
- 환율 동향
- 글로벌 경제 전망

#### 중재자

- 모든 분석 종합
- 최종 투자 의견 도출 (BUY/SELL/HOLD)
- 신뢰도 평가
- 핵심 투자 포인트 정리

### 3. 시각화

- **가격 차트**: 1년 일봉 차트 with Plotly
- **이동평균선**: 20일, 50일 이동평균
- **기술적 지표**: RSI, MACD 시각화
- **핵심 지표 대시보드**: 실시간 업데이트

## 🛠 개발자 가이드

### 새로운 AI 에이전트 추가

1. `investment_advisor/agents/` 디렉토리에 새 파일 생성
2. `InvestmentAgent` 기본 클래스 상속
3. `_run()` 메소드 구현
4. `decision_system.py`에 에이전트 등록

```python
# investment_advisor/agents/new_agent.py
from .base import InvestmentAgent

class NewAgent(InvestmentAgent):
    def _run(self, company: str, market: str, stock_data: Dict[str, Any] = None) -> str:
        # 분석 로직 구현
        return analysis_result
```

### 데이터 소스 우선순위

1. Yahoo Finance (실시간 데이터)
2. StableFetcher (백업 데이터)
3. SimpleFetcher (하드코딩된 백업)

## 🔧 문제 해결

### Yahoo Finance Rate Limiting

- 캐싱 활성화: `USE_CACHE=true`
- 캐시 초기화: `rm -rf .cache/`

### OpenAI API 오류

- API 키 유효성 확인
- GPT-4 모델 액세스 권한 확인
- 기본 모델을 gpt-4o-mini로 설정

### 메모리 부족

- 캐시 정리: `rm -rf .cache/`
- 로그 파일 정리: `rm logs/*.log`

## 📊 기술 스택

- **Backend**: Python 3.12, Streamlit 1.47.0
- **AI/ML**: OpenAI GPT-4 (gpt-4o-mini), LangChain
- **Data**: Yahoo Finance (yfinance 0.2.31)
- **Analysis**: pandas, numpy
- **Visualization**: Plotly
- **Cache**: File-based caching with TTL
- **Parallel Processing**: ThreadPoolExecutor

## 📊 성능 지표

- **분석 시간**: 30-45초 (6개 에이전트 병렬 처리)
- **데이터 정확도**: Yahoo Finance 실시간 데이터
- **캐시 효율**: 15분 TTL로 API 호출 최소화
- **동시 처리**: ThreadPoolExecutor로 병렬 분석

## 🗺 로드맵

### Phase 1: 현재 버전 (v0.2 Beta) ✅

- [x] 6개 AI 에이전트 통합
- [x] Yahoo Finance 실시간 데이터
- [x] 미니멀 UI/UX
- [x] 스마트 캐싱 시스템

### Phase 2: 향후 개선 사항 📋

- [ ] 포트폴리오 관리 기능
- [ ] 사용자 계정 시스템
- [ ] 실시간 알림 기능
- [ ] 백테스팅 기능
- [ ] React + FastAPI 마이그레이션

## ⚠️ 주의사항

- 이 시스템은 투자 참고용입니다
- 실제 투자는 본인의 판단과 책임하에 결정하세요
- AI 분석 결과는 100% 정확하지 않을 수 있습니다

## 📄 라이센스

Apache License 2.0

## 🤝 기여

프로젝트 개선에 기여하고 싶으시다면 Pull Request를 보내주세요.

## 📞 지원

문제가 발생하면 GitHub Issues를 통해 문의해주세요.

---

**현재 버전**: 0.2 (Beta)
**최종 업데이트**: 2025-09-21
