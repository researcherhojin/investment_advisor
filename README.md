# AI 투자 자문 시스템

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.12](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/release/python-3120/)

## 🚀 프로젝트 개요

다양한 AI 에이전트를 활용하여 미국 및 한국 주식 시장에 대한 종합적인 투자 분석과 자문을 제공하는 전문 시스템입니다.

### 🏗️ 모듈화된 아키텍처 (v2.0)
- **단일 파일 → 패키지 구조**: 2000줄 모놀리스에서 체계적인 모듈화로 전환
- **확장 가능한 설계**: 플러그인 아키텍처로 새로운 기능 추가 용이
- **성능 최적화**: 지능형 캐싱과 병렬 처리로 응답 속도 향상

## ⚡ 주요 기능

### 🤖 AI 에이전트 시스템
- **기업분석가**: 재무제표, 성장성, 수익성 분석
- **산업전문가**: 섹터 동향, 경쟁사 비교, 산업 전망
- **거시경제전문가**: 경제 지표, 통화정책, 시장 환경 분석
- **기술분석가**: 차트 패턴, 기술 지표, 매매 타이밍
- **리스크관리자**: 위험 요소, 포트폴리오 리스크 평가
- **중재자**: 종합 의견 조율 및 최종 투자 결정

### 📊 분석 도구
- **기술적 분석**: 볼린저 밴드, 스토캐스틱, ATR, RSI, MACD
- **기본적 분석**: P/E, P/B, ROE, 성장률, 재무건전성
- **섹터 분석**: 시장 섹터별 성과 비교
- **리스크 메트릭**: VaR, 최대 낙폭, 변동성 분석

### ⚙️ 시스템 안정성
- **다중 데이터 소스**: Yahoo Finance, Alpha Vantage, 모의 데이터
- **스마트 캐싱**: 15분 파일 기반 캐시로 API 호출 최소화
- **Rate Limiting 대응**: 지능형 요청 지연 및 재시도 로직
- **로깅 최적화**: 중복 메시지 필터링, 써드파티 로그 억제

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# Python 환경 생성
conda create -n stock python=3.12
conda activate stock

# 의존성 설치
pip install -r requirements.txt
```

### 2. API 키 설정

`.env` 파일을 생성하고 필수 API 키를 설정하세요:

```bash
# OpenAI API 키 (필수)
OPENAI_API_KEY=your_openai_api_key_here

# Alpha Vantage API 키 (선택사항, 백업 데이터 소스)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here

# 캐시 설정
USE_CACHE=true
CACHE_DURATION_MINUTES=15
```

### 3. 애플리케이션 실행

```bash
# Streamlit 앱 실행
streamlit run main.py

# 또는 빠른 시작 스크립트 사용
chmod +x quick_start.sh
./quick_start.sh
```

## 📁 프로젝트 구조

```
investment_advisor/
├── agents/              # AI 에이전트 모듈
│   ├── base.py         # 에이전트 기본 클래스
│   ├── company_analyst.py
│   ├── industry_expert.py
│   ├── macroeconomist.py
│   ├── technical_analyst.py
│   ├── risk_manager.py
│   └── mediator.py
├── analysis/            # 분석 엔진
│   ├── decision_system.py  # 의사결정 시스템
│   ├── fundamental.py      # 기본적 분석
│   └── technical.py        # 기술적 분석
├── data/                # 데이터 fetcher
│   ├── base.py         # 기본 데이터 fetcher
│   ├── korea_stock.py  # 한국 주식 데이터
│   ├── us_stock.py     # 미국 주식 데이터
│   └── economic_data.py # 경제 데이터
├── ui/                  # UI 컴포넌트
│   ├── styles.py       # 전문적인 테마
│   ├── charts.py       # 차트 컴포넌트
│   ├── metrics.py      # 메트릭 표시
│   └── layouts.py      # 레이아웃 관리
└── utils/               # 유틸리티
    ├── config.py       # 설정 관리
    ├── advanced_cache.py # 캐싱 시스템
    └── json_encoder.py  # JSON 직렬화
```

## 🛠️ 주요 명령어

```bash
# 테스트 실행
python -m pytest investment_advisor/tests/

# 린트 체크
ruff check .

# 타입 체크
mypy investment_advisor/

# 캐시 초기화
rm -rf .cache/
```

## 🔧 문제 해결

### Yahoo Finance Rate Limiting (429 오류)

**증상**: `429 Client Error: Too Many Requests`

**해결 방법**:
1. **캐시 활성화 확인**: `.env`에서 `USE_CACHE=true` 설정
2. **캐시 초기화**: `rm -rf .cache/` 실행
3. **API 키 설정**: Alpha Vantage API 키를 백업으로 설정

### OpenAI API 키 오류

**증상**: OpenAI API 키 관련 오류

**해결 방법**:
1. [OpenAI 플랫폼](https://platform.openai.com/api-keys)에서 API 키 생성
2. `.env` 파일에 `OPENAI_API_KEY=your_key_here` 추가
3. 애플리케이션 재시작

### 데이터 로딩 실패

**증상**: 주식 데이터를 가져올 수 없음

**해결 방법**:
1. **네트워크 연결** 확인
2. **티커 심볼** 정확성 확인 (미국장: AAPL, 한국장: 005930.KS)
3. **모의 데이터 모드** 활성화: `.env`에서 `USE_MOCK_DATA=true` 설정

## 🚧 개발 계획

### Phase 1: 현대화 기반 작업 (완료)
- ✅ 모놀리스 → 모듈화 아키텍처 전환
- ✅ 전문적인 UI/UX 개선
- ✅ 성능 최적화 및 캐싱 시스템

### Phase 2: React + FastAPI 마이그레이션 (진행 중)
- 🔄 Docker 기반 개발 환경 구축
- 🔄 React TypeScript + Vite 프론트엔드
- 🔄 FastAPI 백엔드 개발
- 🔄 PWA 기능 구현

### Phase 3: 고급 기능 추가 (계획)
- 📋 실시간 데이터 스트리밍
- 📋 포트폴리오 백테스팅
- 📋 알림 시스템
- 📋 모바일 최적화

## 📄 라이센스

Apache License 2.0

## 🤝 기여

프로젝트 개선에 기여하고 싶으시다면 Pull Request를 보내주세요.

## 📞 지원

문제가 발생하면 GitHub Issues를 통해 문의해주세요.