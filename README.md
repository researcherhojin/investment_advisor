# AI 투자 자문 시스템

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.12](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/release/python-3120/)

<br/>

## 프로젝트 개요

이 프로젝트는 다양한 AI 에이전트를 활용하여 주식 투자에 대한 종합적인 분석과 자문을 제공하는 시스템입니다. 미국 및 한국 주식 시장에 대한 분석을 지원합니다.

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

1. Streamlit 앱을 실행합니다.

    ```
    streamlit run investment_advisor.py
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
├── investment_advisor.py
├── requirements.txt
├── README.md
├── LICENSE
├── .env
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

<br/>

## 감사의 글

이 프로젝트는 다음 오픈 소스 프로젝트들의 도움을 받았습니다:

-   [Streamlit](https://streamlit.io/)
-   [yfinance](https://github.com/ranaroussi/yfinance)
-   [FinanceDataReader](https://github.com/FinanceData/FinanceDataReader)
-   [LangChain](https://github.com/hwchase17/langchain)
