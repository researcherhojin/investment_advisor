# 문제 해결 가이드

## Yahoo Finance API Rate Limiting (429 오류)

### 증상
```
429 Client Error: Too Many Requests for url: https://query2.finance.yahoo.com/...
```

### 해결 방법

#### 1. 캐시 사용 확인
`.env` 파일에서 캐시가 활성화되어 있는지 확인:
```
USE_CACHE=true
CACHE_DURATION_MINUTES=15
```

#### 2. 캐시 초기화
캐시가 손상되었거나 오래된 경우:
```bash
rm -rf .cache
```

#### 3. VPN 또는 프록시 사용
Yahoo Finance가 IP 기반으로 rate limiting을 하는 경우:
- VPN을 사용하여 IP 변경
- 프록시 서버 설정

#### 4. 대체 데이터 소스 사용
`.env` 파일에 Alpha Vantage API 키 추가:
```
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

Alpha Vantage에서 무료 API 키 받기: https://www.alphavantage.co/support/#api-key

#### 5. 요청 간격 조정
현재 설정은 요청 간 1.5초 + 랜덤 지연이 추가됩니다.
필요시 `/investment_advisor/data/us_stock.py`에서 `self.request_delay` 값을 더 크게 조정할 수 있습니다.

## 한국 주식 데이터 오류

### 증상
```
Error fetching Korean stock data
```

### 해결 방법

#### 1. 티커 형식 확인
한국 주식은 6자리 숫자여야 합니다:
- 올바른 예: 005930 (삼성전자)
- 잘못된 예: 5930, A005930

#### 2. 거래 시간 확인
한국 증시 거래 시간: 평일 09:00-15:30 (KST)
장 마감 후에는 일부 실시간 데이터가 제공되지 않을 수 있습니다.

## OpenAI API 오류

### 증상
```
OpenAI API key is required
```

### 해결 방법

#### 1. API 키 설정 확인
`.env` 파일:
```
OPENAI_API_KEY=sk-...
```

#### 2. API 키 유효성 확인
- https://platform.openai.com/api-keys 에서 키 상태 확인
- 사용량 한도 확인
- 결제 정보 확인

## Streamlit 실행 오류

### 증상
```
ModuleNotFoundError: No module named 'streamlit'
```

### 해결 방법

#### 1. 가상 환경 활성화
```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 2. 패키지 재설치
```bash
pip install -r requirements.txt
```

## 메모리 부족 오류

### 증상
- 애플리케이션이 느려지거나 멈춤
- "Memory limit exceeded" 오류

### 해결 방법

#### 1. 캐시 크기 제한
정기적으로 캐시 정리:
```bash
# 30일 이상 된 캐시 파일 삭제
find .cache -type f -mtime +30 -delete
```

#### 2. 분석 기간 단축
더 짧은 기간의 데이터로 분석

## 네트워크 연결 오류

### 증상
```
ConnectionError: Unable to connect to the internet
```

### 해결 방법

#### 1. 인터넷 연결 확인
```bash
ping google.com
```

#### 2. 방화벽/프록시 설정
회사 네트워크의 경우 프록시 설정이 필요할 수 있습니다:
```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
```

#### 3. DNS 설정
DNS 문제인 경우:
```bash
# macOS
sudo dscacheutil -flushcache

# Linux
sudo systemctl restart systemd-resolved
```

## 추가 지원

문제가 지속되는 경우:
1. 로그 파일 확인 (LOG_FILE 설정 시)
2. GitHub Issues에 문제 보고
3. 상세한 오류 메시지와 환경 정보 포함