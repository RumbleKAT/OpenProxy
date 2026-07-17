# Antigravity OpenAI Proxy (OpenProxy)

이 프로젝트는 구글의 **Gemini API Key**를 발급 및 결제 연동하지 않고도, 로컬 개발 환경에서 로그인되어 있는 `agy` CLI 인증 세션을 활용하여 OpenAI 호환 API 규격(`localhost:8000/v1`)으로 호출을 쏘아 에이전트(Antigravity Agent)와 통신할 수 있게 만들어주는 브릿지 프록시 서버입니다.

## 🚀 주요 특징
* **No Gemini API Key Required**: 번거로운 구글 API Key 입력 및 과금 정보 입력 없이 로컬 `agy` CLI 인증 터널을 그대로 활용합니다.
* **OpenAI Protocol Support**: `/v1/chat/completions` 및 `/v1/models` 규격을 준수하여, AnythingLLM 등 OpenAI 호환 클라이언트에 플러그인하듯 바로 연결할 수 있습니다.
* **Zero Dependency Blocking**: 복잡한 Python SDK 연결 블로킹이나 localharness 바이너리 결손 오류를 100% 우회합니다.
* **Dynamic CLI Routing**: 내부적으로 시스템 PATH에 있는 `agy` 바이너리를 동적으로 탐색하여 실행합니다.

## 📦 설치 및 실행 방법

### 1. 가상환경 구축 및 의존성 설치
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 프록시 서버 실행
```bash
python proxy.py
```
* 기본적으로 `http://localhost:8000` 에서 구동됩니다.

### 3. 클라이언트 연동 (예: AnythingLLM)
* **LLM Provider**: `Generic OpenAI` (또는 `Custom OpenAI`)
* **Base URL**: `http://localhost:8000/v1`
* **API Key**: 임의의 문자열 (예: `agy` 또는 `dummy`)
* **Model**: `agy-agent` (또는 `gemini-2.0-pro-exp`)
