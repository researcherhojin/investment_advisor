# AI 투자 자문 시스템

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.12](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/release/python-3120/)

<br/>

## 프로젝트 개요

이 프로젝트는 다양한 AI 에이전트를 활용하여 주식 투자에 대한 종합적인 분석과 자문을 제공하는 시스템입니다. 미국 및 한국 주식 시장에 대한 분석을 지원합니다.

<br/>

## ⚠️ API Rate Limiting 및 안정성 개선

시스템 안정성과 Yahoo Finance API rate limiting (429 오류) 대응을 위한 다중 방어 시스템:

### 1. 캐싱 및 성능 최적화
- **고급 JSON 직렬화**: Pandas Timestamp, numpy 타입 등 완전 지원
- **15분 캐시**: 동일 요청 시 캐시된 데이터 사용으로 API 호출 최소화
- **스마트 요청 지연**: 1.5초 + 랜덤 지연으로 rate limiting 회피

### 2. 다중 데이터 소스 지원
- **Yahoo Finance**: 메인 데이터 소스
- **Alpha Vantage API**: 백업 데이터 소스 (API 키 설정 시)
- **모의 데이터**: 개발/테스트용 안전한 대체 데이터

### 3. 로깅 시스템 최적화
- **반복 메시지 필터링**: 동일 오류 메시지 최대 3회만 출력
- **써드파티 라이브러리 로그 억제**: yfinance, langsmith 등 노이즈 로그 제거
- **LangChain 비활성화**: API 키 없을 시 자동으로 tracing 비활성화

### Alpha Vantage API 설정 (선택사항)
```bash
# .env 파일에 추가
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

무료 API 키 받기: https://www.alphavantage.co/support/#api-key

<br/>

## 주요 기능

-   기업 분석가, 산업 전문가, 거시경제 전문가, 기술 분석가, 리스크 관리자의 다각도 분석
-   실시간 주가 데이터 및 기술적 지표 시각화
-   종합적인 투자 의견 제시
-   한국 및 미국 주식 시장 지원

<br/>

## 선행 조건

-   Python 3.12 이상
-   OpenAI API Key
-   Alpha Vantage API Key (경제 지표 데이터용)

<br/>

## 설치 방법

1. 저장소를 클론합니다:

    ```
    git clone https://github.com/yourusername/ai-investment-advisor.git
    cd ai-investment-advisor
    ```

2. 가상 환경을 생성하고 활성화합니다:

    ```
     conda create -n stock python=3.12
     conda activate stock
    ```

3. 필요한 패키지를 설치합니다:

    ```
    pip install -r requirements.txt
    ```

4. `.env` 파일을 생성하고 필요한 API 키를 설정합니다:

    ```
    OPENAI_API_KEY=your_openai_api_key_here
    ```

<br/>

## 사용 방법

1. Streamlit 앱을 실행합니다:

    ```
    streamlit run main.py
    ```
    
    또는 빠른 시작 스크립트 사용:
    
    ```
    ./quick_start.sh run
    ```

2. 웹 브라우저에서 표시된 로컬 URL로 접속합니다.
3. 사이드바에서 분석하고자 하는 주식의 티커, 시장, 산업 등을 선택합니다.
4. "분석 시작" 버튼을 클릭하여 결과를 확인합니다.

<br/>

## 기술 스택

-   Python
-   Streamlit
-   Pandas, NumPy
-   Plotly
-   yfinance, FinanceDataReader
-   OpenAI GPT
-   LangChain

<br/>

## 프로젝트 구조

```
ai-investment-advisor/
│
├── main.py                            # 메인 애플리케이션 진입점
├── investment_advisor/                # 리팩토링된 모듈 패키지
│   ├── agents/                        # AI 에이전트들
│   │   ├── base.py                    # 기본 에이전트 클래스
│   │   ├── company_analyst.py         # 기업 분석가
│   │   ├── industry_expert.py         # 산업 전문가
│   │   ├── macroeconomist.py         # 거시경제 전문가
│   │   ├── technical_analyst.py      # 기술 분석가
│   │   └── risk_manager.py           # 리스크 관리자
│   ├── data/                          # 데이터 수집 모듈
│   │   ├── base.py                    # 기본 데이터 페처
│   │   ├── korea_stock.py             # 한국 주식 데이터
│   │   ├── us_stock.py                # 미국 주식 데이터
│   │   └── yahoo_finance_alternative.py # 대체 데이터 소스
│   ├── analysis/                      # 분석 로직
│   │   ├── technical.py               # 기술적 분석
│   │   └── fundamental.py             # 기본적 분석
│   ├── ui/                            # UI 컴포넌트
│   │   ├── components.py              # UI 컴포넌트
│   │   └── layout.py                  # 레이아웃 관리
│   └── utils/                         # 유틸리티 함수
│       ├── config.py                  # 설정 관리
│       ├── logging.py                 # 로깅 시스템
│       └── json_encoder.py            # JSON 직렬화
├── quick_start.sh                     # 빠른 시작 스크립트
├── requirements.txt                   # 파이썬 패키지 목록
├── README.md                          # 프로젝트 문서
├── SETUP_GUIDE.md                     # 상세 설정 가이드
├── TROUBLESHOOTING.md                 # 문제 해결 가이드
├── LICENSE                            # 라이센스
├── .env.example                       # 환경 변수 템플릿
├── .env                               # 실제 환경 변수 (gitignore)
├── .cache/                            # 데이터 캐시 디렉토리
└── .gitignore
```

<br/>

## 라이선스

이 프로젝트는 Apache 라이선스 2.0 하에 있습니다. 자세한 내용은 [LICENSE](https://www.apache.org/licenses/LICENSE-2.0) 파일을 참조하세요.

<br/>

## 기여

프로젝트에 기여하고 싶으시다면 다음 절차를 따라주세요:

1. 이 저장소를 포크합니다.
2. 새 브랜치를 만듭니다 (`git checkout -b feature/AmazingFeature`).
3. 변경 사항을 커밋합니다 (`git commit -m 'Add some AmazingFeature'`).
4. 브랜치에 푸시합니다 (`git push origin feature/AmazingFeature`).
5. 풀 리퀘스트를 열어주세요.

<br/>

## 연락처

프로젝트에 대한 질문이나 피드백이 있으시면 researcherhojin@gmail.com으로 연락주세요.

## 감사의 글

이 프로젝트는 다음 오픈 소스 프로젝트들의 도움을 받았습니다:

-   [Streamlit](https://streamlit.io/)
-   [yfinance](https://github.com/ranaroussi/yfinance)
-   [FinanceDataReader](https://github.com/FinanceData/FinanceDataReader)
-   [LangChain](https://github.com/hwchase17/langchain)
-   [Alpha Vantage](https://www.alphavantage.co/)
