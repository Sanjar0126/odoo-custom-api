import requests

import json

MERCHANT_ID = "61a8bbcdf6071daf8dacfb5b"
MERCHANT_KEY = "XuvqmN1&cHxAjZH9KPTpF2zHM5xQX84tk0wO"

URL = 'https://checkout.paycom.uz/api'

def add_card(data):
    payload = {
        "id": 123,
        "method": "cards.create",
        "params": {
            "card": {
                "number": data['card_number'],
                "expire": data['card_expire']
            },
            "save": True
        }
    }
    headers = {"X-Auth": MERCHANT_ID}
    r = requests.post(URL, data=json.dumps(payload), headers=headers)
    return r.json()

def send_code(token):
    payload = {
        "id": 123,
        "method": "cards.get_verify_code",
        "params": {
            "token": token
        }
    }
    headers = {"X-Auth": MERCHANT_ID}
    return requests.post(URL, data=json.dumps(payload), headers=headers).json()

def verify_code(code, token):
    payload = {
        "id": 123,
        "method": "cards.verify",
        "params": {
            "token": token,
            "code": code
        }
    }
    headers = {"X-Auth": MERCHANT_ID}
    return requests.post(URL, data=json.dumps(payload), headers=headers).json()

def create_receipt(amount):
    payload = {
        "id": 123,
        "method": "receipts.create",
        "params": {
            "amount": amount
        }
    }
    headers = {"X-Auth": MERCHANT_ID+":"+MERCHANT_KEY}
    return requests.post(URL, json=payload, headers=headers).json()

def pay_receipt(receipt_id, token):
    payload = {
        "id": 123,
        "method": "receipts.pay",
        "params": {
            "id": receipt_id,
            "token": token
        }
    }
    headers = {"X-Auth": MERCHANT_ID+":"+MERCHANT_KEY}
    return requests.post(URL, json=payload, headers=headers).json()

def cancel_receipt(receipt_id):
    payload = {
                "id": 123,
                "method": "receipts.check",
                "params": {
                    "id": receipt_id
                }
              }
    
    headers = {"X-Auth": MERCHANT_ID+":"+MERCHANT_KEY}
    return requests.post(URL, json=payload, headers=headers).json()

def check_receipt(receipt_id):
    payload = {
        "id": 123,
        "method": "receipts.check",
        "params": {
            "id": receipt_id
        }
    }
    
    headers = {"X-Auth": MERCHANT_ID+":"+MERCHANT_KEY}
    return requests.post(URL, json=payload, headers=headers).json()
