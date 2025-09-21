#!/bin/bash

# AI Investment Advisory System - Quick Start Script

echo "🚀 AI 투자 자문 시스템 빠른 시작"
echo "================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env 파일이 없습니다."

    # Check if .env.example exists
    if [ -f .env.example ]; then
        echo "📝 .env.example을 .env로 복사합니다..."
        cp .env.example .env
        echo "✅ .env 파일이 생성되었습니다."
        echo ""
        echo "⚠️  중요: .env 파일을 열어서 OPENAI_API_KEY를 설정해주세요!"
        echo "   명령어: nano .env 또는 vi .env"
        echo ""
        read -p "API 키를 설정하셨나요? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "❌ .env 파일에서 API 키를 설정한 후 다시 실행해주세요."
            exit 1
        fi
    else
        echo "❌ .env.example 파일도 없습니다. 설정 파일을 확인해주세요."
        exit 1
    fi
fi

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python이 설치되어 있지 않습니다."
    exit 1
fi

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✅ Python 버전: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d "../../../miniforge/envs/stock" ]; then
    echo "📦 가상 환경을 생성합니다..."
    python -m venv venv
    source venv/bin/activate

    echo "📥 필요한 패키지를 설치합니다..."
    pip install -r requirements.txt
else
    echo "✅ 가상 환경이 이미 존재합니다."
fi

# Create cache directory if it doesn't exist
if [ ! -d ".cache" ]; then
    mkdir .cache
    echo "✅ 캐시 디렉토리가 생성되었습니다."
fi

echo ""
echo "🎉 준비가 완료되었습니다!"
echo ""
echo "다음 명령어로 애플리케이션을 실행하세요:"
echo "  streamlit run main.py"
echo ""
echo "또는 이 스크립트에 'run' 인자를 추가하여 바로 실행할 수 있습니다:"
echo "  ./quick_start.sh run"

# Run the app if 'run' argument is provided
if [ "$1" == "run" ]; then
    echo ""
    echo "🚀 애플리케이션을 시작합니다..."
    streamlit run main.py
fi
