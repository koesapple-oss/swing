# Project: Swing
# Agent 2: The Scanner & Analyzer
# Path: scraper/kis_client.py

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

class KISClient:
    def __init__(self):
        self.base_url = os.getenv("KIS_BASE_URL", "https://openapi.koreainvestment.com:9443")
        self.app_key = os.getenv("KIS_APP_KEY")
        self.app_secret = os.getenv("KIS_APP_SECRET")
        self.access_token = None

    def get_access_token(self):
        """접근 토큰 발급"""
        path = "/oauth2/tokenP"
        url = self.base_url + path
        payload = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        res = requests.post(url, data=json.dumps(payload))
        if res.status_code == 200:
            self.access_token = res.json()["access_token"]
            return self.access_token
        return None

    def get_market_rankings(self, market_code="0001"):
        """거래대금 상위 종목 수집 (market_code: 0001=코스피, 1001=코스닥)"""
        if not self.access_token:
            self.get_access_token()

        path = "/uapi/domestic-stock/v1/quotations/volume-rank"
        url = self.base_url + path
        headers = {
            "Content-Type": "application/json",
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "FHPST01710000"
        }
        
        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_cond_scr_div_code": "20171",
            "fid_input_iscd": market_code, 
            "fid_div_cls_code": "0",
            "fid_sort_cntg_id": "1", # 거래대금 순
            "fid_trgt_cls_code": "0",
            "fid_trgt_exls_cls_code": "0",
            "fid_input_price_1": "",
            "fid_input_price_2": "",
            "fid_vol_cnt": "",
            "fid_input_date_1": ""
        }
        
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            return res.json()["output"]
        return []
