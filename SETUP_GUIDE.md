# AI 투자 자문 시스템 설정 가이드

## 🚀 빠른 시작

### 1. 환경 변수 설정

먼저 `.env` 파일을 생성해야 합니다:

```bash
# .env.example을 복사하여 .env 파일 생성
cp .env.example .env
```

### 2. OpenAI API 키 설정

`.env` 파일을 열어서 OpenAI API 키를 설정하세요:

```bash
# 텍스트 에디터로 .env 파일 열기
nano .env
# 또는
vi .env
```

다음 라인을 찾아서 수정하세요:
```
OPENAI_API_KEY=your_openai_api_key_here
```

여기서 `your_openai_api_key_here`를 실제 OpenAI API 키로 교체하세요.

**OpenAI API 키 받는 방법:**
1. https://platform.openai.com/api-keys 방문
2. 로그인 또는 회원가입
3. "Create new secret key" 클릭
4. 생성된 키를 복사하여 `.env` 파일에 붙여넣기

### 3. 의존성 설치

```bash
# 가상 환경 생성 (선택사항이지만 권장)
python -m venv venv

# 가상 환경 활성화
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 4. 애플리케이션 실행

```bash
streamlit run main.py
```

또는 빠른 시작 스크립트 사용:

```bash
# 실행 권한 부여 (첫 실행 시에만)
chmod +x quick_start.sh

# 설정 및 실행
./quick_start.sh run
```

## 📋 선택적 설정

### Alpha Vantage API 키 (선택사항)

미국 주식의 추가 데이터를 위해 Alpha Vantage API 키를 설정할 수 있습니다:

1. https://www.alphavantage.co/support/#api-key 방문
2. 무료 API 키 신청
3. `.env` 파일에 추가:
   ```
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
   ```

### 고급 설정 옵션

`.env` 파일에서 다음 설정들을 커스터마이즈할 수 있습니다:

- `DEFAULT_MODEL`: OpenAI 모델 선택 (기본값: gpt-4o-mini-2024-07-18)
- `MODEL_TEMPERATURE`: 모델 창의성 조절 (0.0-2.0, 기본값: 0.1)
- `DEFAULT_MARKET`: 기본 시장 선택 (미국장/한국장)
- `CACHE_DURATION_MINUTES`: 캐시 유지 시간 (기본값: 15분)

## 🔧 문제 해결

### "OPENAI_API_KEY가 필요합니다!" 오류

1. `.env` 파일이 올바른 위치에 있는지 확인
2. API 키가 올바르게 입력되었는지 확인
3. API 키 앞뒤에 공백이나 따옴표가 없는지 확인

### 패키지 설치 오류

```bash
# pip 업그레이드
pip install --upgrade pip

# 개별 패키지 설치 시도
pip install streamlit langchain openai yfinance
```

### Streamlit 실행 오류

```bash
# Streamlit 캐시 초기화
streamlit cache clear

# 포트 변경하여 실행
streamlit run main.py --server.port 8502
```

## 📱 사용 방법

1. **시장 선택**: 사이드바에서 미국장 또는 한국장 선택
2. **티커 입력**: 
   - 미국장: AAPL, MSFT, GOOGL 등
   - 한국장: 005930, 000660, 035720 등
3. **산업 선택**: 해당 기업의 산업 분류 선택
4. **분석 기간**: 슬라이더로 분석 기간 조정
5. **분석 시작**: 버튼 클릭하여 AI 분석 실행

## 🎯 주요 기능

- **종합 AI 분석**: 5개의 전문가 AI가 다각도로 분석
- **기술적 분석**: 차트, 지표, 패턴 분석
- **기본적 분석**: 재무제표, 가치평가
- **리스크 평가**: 투자 위험 요소 분석
- **추천 종목**: 유사 종목 및 섹터 분석
- **캐싱 시스템**: 빠른 재분석을 위한 데이터 캐싱

## 📞 지원

문제가 있거나 도움이 필요하시면:
- GitHub Issues: [프로젝트 저장소]/issues
- 이메일: support@example.com

---

마지막 업데이트: 2025년 8월