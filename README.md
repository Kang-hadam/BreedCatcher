# 데브파이브 서버 시스템

---

## Install

**python 3.10** poetry 설치

    pip install poetry

가상 환경 접속

    poetry shell

라이브러리 설치

    poetry install

.env 파일을 직접 작성

    STAGE=local, prod, dev
    DB_URL=localhost
    DB_PORT=5432
    DB_ID=postgres
    DB_PW=pw
    DB_DB=postgres
    DB_SCHEMA=public

서버 시작

    devfive dev

Lint 문법 검사 시작

    devfive lint

## Update database models

    devfive commit "message"

## FCM 적용

firebase admin account json을 app 폴더 안에 아래 파일명으로 추가

    google-account.json