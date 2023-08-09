"""유저 관련 api 모음"""
import base64
import json
import os
from typing import Optional, Literal

import requests
from fastapi import APIRouter, HTTPException, Form
from fastapi import Request
from server_modules.route import FilterSQLAlchemyCRUDRouter
from starlette.responses import RedirectResponse

from models.user import UserModel

SNS_REDIRECT_URL = os.getenv('SNS_REDIRECT_URL')
KAKAO_CLIENT_ID = os.getenv('KAKAO_CLIENT_ID')
NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
NAVER_SECRET_KEY = os.getenv('NAVER_SECRET_KEY')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_SECRET_KEY = os.getenv('GOOGLE_SECRET_KEY')

user_router = APIRouter(tags=["Users"])


def get_all_after_callback(_: Request, __: list[UserModel], ___=None):
    """
    get all 추가 코드
    """
    print('Complete get Before')


def complete_after(_: Request, __: UserModel, ___=None):
    """
    get all 추가 코드
    """
    print('Complete get After')


user_router.include_router(
    FilterSQLAlchemyCRUDRouter(db_model=UserModel,
                               prefix='/users',
                               create_route_before_callback=get_all_after_callback,
                               create_route_after_callback=complete_after,
                               update_route_before_callback=get_all_after_callback,
                               update_route_after_callback=complete_after,
                               delete_one_route_before_callback=get_all_after_callback,
                               delete_one_route_after_callback=complete_after,
                               # dependencies=[Depends(get_user)],
                               delete_all_route=False))

user_router.include_router(
    FilterSQLAlchemyCRUDRouter(db_model=UserModel,
                               prefix='/test/{id}',
                               tags=['Users'],
                               # id 경로 매개 변수를 id 칼럼에 필터링
                               # get_all 이 완료 되었을 때 호출
                               get_all_route_after_callback=get_all_after_callback,
                               delete_all_route=False))


@user_router.get('/sns/{platform}/')
def sns_signup(platform: Literal['kakao', 'naver', 'google'], code: str, state: Optional[str]):
    """
    sns 회원가입 / login api

    [error code]\n
    - kakao \n
    1 : code에 문제가 있음\n
    2 : sns 서버에 문제가 있음\n
    3 : 잘못된 platform
    """
    if platform == 'kakao':
        params = {'client_id': KAKAO_CLIENT_ID, 'code': code, 'state': state, 'grant_type': 'authorization_code'}
        auth_info = requests.post(url='https://kauth.kakao.com/oauth/token', params=params, timeout=30)

        if auth_info.status_code != 200:
            raise HTTPException(status_code=400, detail={'code': 1, 'msg': 'invalid code'})
        headers = {'Authorization': f'Bearer {auth_info.json()["access_token"]}'}

        client_info = requests.get(url='https://kapi.kakao.com/v2/user/me', headers=headers, timeout=30)
        if client_info.status_code != 200:
            raise HTTPException(status_code=400, detail={'code': 2, 'msg': 'kakao server has problem'})

        sns_id = str(client_info.json()['id'])
        sns_email = client_info.json()['kakao_account']['email']

    elif platform == 'naver':
        params = {'client_id': NAVER_CLIENT_ID, 'client_secret': NAVER_SECRET_KEY, 'code': code, 'state': state,
                  'grant_type': 'authorization_code'}
        auth_info = requests.post(url='https://nid.naver.com/oauth2.0/token', params=params, timeout=30)
        if auth_info.status_code != 200:
            raise HTTPException(status_code=400, detail={'code': 1, 'msg': 'invalid code'})
        headers = {'Authorization': f'Bearer {auth_info.json()["access_token"]}'}

        client_info = requests.get(url='https://openapi.naver.com/v1/nid/me', headers=headers, timeout=30)
        if client_info.status_code != 200:
            raise HTTPException(status_code=400, detail={'code': 2, 'msg': 'naver server has problem'})
        sns_id = str(client_info.json()['response']['id'])
        sns_email = client_info.json()['response']['email']

    elif platform == 'google':
        data = {'client_id': GOOGLE_CLIENT_ID, 'client_secret': GOOGLE_SECRET_KEY, 'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': SNS_REDIRECT_URL}
        auth_info = requests.post(url='https://oauth2.googleapis.com/token', data=data, timeout=30)
        if auth_info.status_code != 200:
            raise HTTPException(status_code=400, detail={'code': 1, 'msg': 'invalid code'})
        params = {'access_token': auth_info.json()["access_token"]}
        client_info = requests.get(url='https://www.googleapis.com/oauth2/v2/userinfo', params=params, timeout=30)
        if client_info.status_code != 200:
            raise HTTPException(status_code=400, detail={'code': 2, 'msg': 'google server has problem'})
        sns_id = str(client_info.json()['id'])
        sns_email = client_info.json()['email']
    else:
        raise HTTPException(status_code=400, detail={'code': 3, 'msg': 'wrong platform'})

    username = platform + sns_email
    password = sns_id

    return RedirectResponse(url=f'{SNS_REDIRECT_URL}?pw={password}&username={username}&snsType={platform}',
                            status_code=302)


@user_router.post('/sns/apple/')
def sns_apple_signup(id_token: str = Form(...)):
    """
    apple 로그인
    """
    token_payload = id_token.split('.')[1]
    token_payload = token_payload + '=' * (4 - len(token_payload) % 4)  # set string's format to base64 length
    decoded_payload = json.loads(base64.b64decode(token_payload))

    username = 'apple' + decoded_payload['email']
    password = decoded_payload['sub']

    return RedirectResponse(url=f'{SNS_REDIRECT_URL}?pw={password}&username={username}&snsType=apple', status_code=302)
