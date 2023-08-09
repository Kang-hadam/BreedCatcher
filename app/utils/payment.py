"""
iamport 기반 payment 모듈
"""

from pydantic import BaseModel, Field


class CardInfo(BaseModel):
    """
    iamport base card info
    """
    card_number: str = Field(regex=r'^\d{4}-\d{4}-\d{4}-\d{4}$')
    expiry: str = Field(regex=r'^\d{4}-(0[1-9]|1[0-2])$')
    birth: str = Field(regex=r'^\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])$')
    pwd_2digit: str = Field(regex=r'^\d{2}')


class PayInfo(CardInfo):
    """
    iamport base pay info
    """
    name: str
    buyer_name: str
    buyer_tel: str
    buyer_email: str


class Payment:
    """
    Payment
    """
    __auth_header = {}

    # pylint: disable=import-outside-toplevel
    def __init__(self, api_key: str, api_secret_key: str):
        """
        iamport access token 발급
        """
        import requests
        url = 'https://api.iamport.kr/users/getToken'
        body = {"imp_key": api_key, "imp_secret": api_secret_key}
        self.__auth_header["Authorization"] = requests.post(url, data=body, timeout=30).json()['response']['access_token']

        def set_billing_key(self, customer_uid: str, card_info: CardInfo):
            """
            빌링키 세팅
            """
            url = f'https://api.iamport.kr/subscribe/customers/{customer_uid}'
            body = {"card_number": card_info.card_number, "expiry": card_info.expiry, "birth": card_info.birth,
                    "pwd_2digit": card_info.pwd_2digit}
            response = requests.post(url, headers=self.__auth_header, data=body, timeout=30)
            if response.status_code != 200:
                raise ConnectionError('iamport server error')
            if response.json()['code'] != 0:
                raise ValueError('invalid card info')

        self.set_billing_key = set_billing_key

        def pay_once(self, merchant_uid: str, amount: int, pay_info: PayInfo):
            """
            일회성 결제
            """
            url = "https://api.iamport.kr/subscribe/payments/onetime"
            body = {"merchant_uid": merchant_uid, "card_number": pay_info.card_number, "expiry": pay_info.expiry,
                    "birth": pay_info.birth, "amount": amount, "name": pay_info.name, "buyer_name": pay_info.buyer_name,
                    "buyer_tel": pay_info.buyer_tel,
                    "buyer_email": pay_info.buyer_tel, "pwd_2digit": pay_info.pwd_2digit}
            response = requests.post(url, headers=self.__auth_header, data=body, timeout=30)
            if response.status_code != 200:
                raise ConnectionError('iamport server error')
            if response.json()['code'] != 0:
                raise ValueError('invalid card info')

        self.pay_once = pay_once

        def pay_again(self, customer_uid: str, merchant_uid: str, amount: int):
            """
            빌링키를 이용해 결제
            """
            url = 'https://api.iamport.kr/subscribe/payments/again'
            body = {"customer_uid": customer_uid, "merchant_uid": merchant_uid, "amount": amount,
                    "name": "월간 이용권 정기결제"}
            requests.post(url, headers=self.__auth_header, data=body, timeout=30)

        self.pay_again = pay_again
