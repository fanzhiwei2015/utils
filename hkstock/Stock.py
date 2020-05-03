#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import requests
import re
import os
import traceback
import sys
import time
import datetime
import pinyin
import json

# use the Elasticsearch client's helpers class for _bulk API
from elasticsearch import Elasticsearch, helpers

# declare a client instance of the Python Elasticsearch library
client = Elasticsearch("localhost:9200")


base_url="http://emweb.securities.eastmoney.com/PC_HKF10/NewFinancialAnalysis/GetZCFZB?code={}&startdate=&ctype=4&rtype=0"
class Stock:
    def __init__(self, stock_id, stock_name):
        self.url = base_url.format(stock_id)
        self.stock_id = stock_id
        self.stock_name = stock_name

    def get_asset_debt(self):
        page = requests.get(self.url)
        assert page.status_code==200, "fail to get url %s" % self.url

        page_json=page.json()
        assert page_json['status'] == 1, "status not return 1"
        all_data = page_json['data']
        headers_cn= all_data[0]
        headers_en=[]

        for header in headers_cn:
            header = header.replace("|", "_").replace("(", "").replace(")", "").replace(":","")
            headers_en.append(pinyin.get(header, format="strip", delimiter="_"))
        #import pdb;pdb.set_trace()
        assert len(headers_cn) == len(headers_en), "headers not equal after translate to english"
        header_len=len(headers_en)

        results=[]
        for data in all_data[1:]:
            item={}
            timestamp = datetime.datetime.strptime(data[0], "%y-%m-%d")
            cur=1
            while cur < header_len:
                #import pdb;pdb.set_trace()
                if "--" in data[cur]:
                    item[headers_en[cur]] = 0.0
                else:
                    value = data[cur].replace("亿", "")
                    if "万" in value:
                        value=float(value.replace("万","")) * 10000
                    item[headers_en[cur]]=float(value)
                cur += 1
            item["timestamp"] = timestamp
            item["stock_id"] = self.stock_id
            item["stock_name"] = self.stock_name
            item["table"] = "asset_debt"
            results.append(item)

        resp = helpers.bulk(
            client,
            results,
            index="stocks-info",
            doc_type="_doc"
        )

        # print the response returned by Elasticsearch
        print("helpers.bulk() RESPONSE:", resp, flush=True)
        print("helpers.bulk() RESPONSE:", json.dumps(resp, indent=4), flush=True)



if __name__ == "__main__":
    istock=Stock("00001", "长和")
    istock.get_asset_debt()