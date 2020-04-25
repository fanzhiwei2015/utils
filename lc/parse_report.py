#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import os
import sys
from bs4 import BeautifulSoup as bs
import datetime
import json
from time import sleep

# use the Elasticsearch client's helpers class for _bulk API
from elasticsearch import Elasticsearch, helpers

# declare a client instance of the Python Elasticsearch library
client = Elasticsearch("localhost:9200")

# def month_to_number(m):
# 	mapping={
# 		"January":1,
# 		"February":2,
# 		"March":3,
# 		"April":4,
# 		"May":5,
# 		"June": 6,
# 		"July": 7,
# 		"August": 8,
# 		"September": 9,
# 		"Octor": 10,
# 		"November": 11,
# 		"December": 12,
# 		}
# 	if m not in mapping:
# 		import pdb;pdb.set_trace()
# 	return mapping[m]

def get_request_date(line):
	lines=line.split(" ")
	loanID=lines[2]
	rdate="%s %s %s" % (lines[6],lines[7], lines[8])
	return (loanID,rdate)
	

class Parse_report:
	def __init__(self, report):
		self.report = report
		self.loansinfo = []

	def insert_es(self):
		resp = helpers.bulk(
			client,
			self.loansinfo,
			index="lc-%s" % datetime.datetime.now().strftime("%Y-%m-%d"),
			doc_type="_doc"
		)

		# print the response returned by Elasticsearch
		print("helpers.bulk() RESPONSE:", resp)
		print("helpers.bulk() RESPONSE:", json.dumps(resp, indent=4))

	def run_parse_post(self):
		pages=[]
		cur=0
		pages.append("")
		request_date={}
		credit_report_date={}
		#import pdb;pdb.set_trace()
		infile = open(self.report, "r")
		for line in infile:
			if "<HR " in line:
				cur += 1
				pages.append("")
				continue
			elif "by a borrower with the following characteristics" in line:
				#print(line)
				loanID,rdate=get_request_date(line)
				request_date.update({loanID:rdate})
			elif "A credit bureau reported the following information" in line:
				#crdate=get_cr_date(line)
				pass
			else:
				pages[cur] += line
		loanTable_Index=1
		for page in pages:
			#import pdb;pdb.set_trace()
			soup=bs(page,'html.parser')
			tables=soup.find_all('table')

			#table 1 loan information
			rows=tables[loanTable_Index].find_all('tr')
			columns_header= rows[0].find_all('td')
			columns_data = rows[1].find_all('td')
			loaninfo={}
			cur=0
			while cur < len(columns_header):
				key=columns_header[cur].get_text().strip().replace(" ","_").replace("\n","_").replace(":","")
				value = columns_data[cur].get_text().strip()
				if value[0] == "$":
					value = int(value.replace("$","").replace(",",""))
				elif value[-1] == "%":
					value = round(float(value.replace("%",""))/100,2)
				loaninfo[key]=value
				cur += 1
			#print(loaninfo)
			if loaninfo["Member_Loan_ID"] in request_date:
				rdate = request_date[loaninfo["Member_Loan_ID"]]
			else:
				rdate = datetime.datetime.now().strftime("%B %d, %Y")
			#import pdb;pdb.set_trace()
			loaninfo.update({"request_date": datetime.datetime.strptime(rdate,"%B %d, %Y")})

			es_info={"_id": loaninfo["Member_Loan_ID"],
					 "timestamp": datetime.datetime.strptime(rdate,"%B %d, %Y"),
					 "report_type": "post"}
			loaninfo.update(es_info)

			#print(loaninfo)


			#table2 borrow information
			rows=tables[loanTable_Index+1].find_all('tr')
			for row in rows:
				columns = row.find_all('td')
				cur=0
				while cur < len(columns):
					#import pdb;pdb.set_trace()
					key = columns[cur].get_text().strip().replace(" ","_").replace("\n", "_").replace(":","")
					value = columns[cur+1].get_text().strip()
					if value[0] == "$":
						value = int(value.split("/")[0].replace("$","").replace(",",""))
					elif value[-1] == "%":
						value = round(float(value.replace("%",""))/100,2)
					elif value.isdigit():
						value=int(value)
					if "n/a" not in str(value).lower():
						loaninfo[key]=value
					cur += 2
				#print(loaninfo)

			#table3 borrow credit
			rows=tables[loanTable_Index+2].find_all('tr')
			for row in rows:
				columns = row.find_all('td')
				cur=0
				while cur < len(columns):
					#import pdb;pdb.set_trace()
					key = columns[cur].get_text().strip().replace(" ","_").replace("\n", "_").replace(":","")
					value = columns[cur+1].get_text().strip()
					if value[0] == "$":
						value = int(value.replace("$","").replace(",","").split(".")[0])
					elif value[-1] == "%":
						value = round(float(value.replace("%",""))/100,2)
					elif value.isdigit():
						value=int(value)

					if "n/a" not in str(value).lower():
						loaninfo[key]=value
					cur += 2
				#print(loaninfo)

			self.loansinfo.append(loaninfo)
			print("post", loaninfo["Member_Loan_ID"],"added")
			loanTable_Index = 0

	def run_parse_sale(self):
		pages=[]
		cur=0
		pages.append("")
		request_date={}
		credit_report_date={}
		#import pdb;pdb.set_trace()
		infile = open(self.report, "r")
		for line in infile:
			if "<HR " in line:
				cur += 1
				pages.append("")
				continue

			else:
				pages[cur] += line
		loanTable_Index=1
		for page in pages:
			#import pdb;pdb.set_trace()
			soup=bs(page,'html.parser')
			tables=soup.find_all('table')

			#table 1 loan information
			rows=tables[loanTable_Index].find_all('tr')
			columns_header= rows[0].find_all('td')
			columns_data = rows[1].find_all('td')
			loaninfo={}
			cur=0
			while cur < len(columns_header):
				key=columns_header[cur].get_text().strip().replace(" ","_").replace("\n","_").replace(":","")
				value = columns_data[cur].get_text().strip()
				if value[0] == "$":
					value = int(value.replace("$","").replace(",",""))
				elif value[-1] == "%":
					value = round(float(value.replace("%",""))/100,2)
				elif "Issue_Date" in key or "maturity" in key:
					value = datetime.datetime.strptime(value, "%B %d, %Y")
				loaninfo[key]=value
				cur += 1
			es_info={"_id": loaninfo["Series_of_Member_Payment_Dependent_Notes"],
					 "timestamp": loaninfo["Sale_and_Original_Issue_Date"],
					 "report_type": "sales"}
			loaninfo.update(es_info)

			#print(loaninfo)


			#table2 borrow information
			rows=tables[loanTable_Index+1].find_all('tr')
			for row in rows:
				columns = row.find_all('td')
				cur=0
				while cur < len(columns):
					#import pdb;pdb.set_trace()
					key = columns[cur].get_text().strip().replace(" ","_").replace("\n", "_").replace(":","")
					value = columns[cur+1].get_text().strip()
					#import pdb;pdb.set_trace()
					if key=="":
						cur +=2
						continue
					if value[0] == "$":
						value = int(value.split("/")[0].replace("$","").replace(",",""))
					elif value[-1] == "%":
						value = round(float(value.replace("%",""))/100,2)
					elif value.isdigit():
						value=int(value)
					if "n/a" not in str(value).lower():
						loaninfo[key]=value
					cur += 2
				#print(loaninfo)

			#table3 borrow credit
			rows=tables[loanTable_Index+2].find_all('tr')
			for row in rows:
				columns = row.find_all('td')
				cur=0
				while cur < len(columns):
					#import pdb;pdb.set_trace()
					key = columns[cur].get_text().strip().replace(" ","_").replace("\n", "_").replace(":","")
					value = columns[cur+1].get_text().strip()

					if key=="":
						cur +=2
						continue
					if value[0] == "$":
						value = int(value.replace("$","").replace(",","").split(".")[0])
					elif value[-1] == "%":
						value = round(float(value.replace("%",""))/100,2)
					elif value.isdigit():
						value=int(value)

					if "n/a" not in str(value).lower():
						loaninfo[key]=value
					cur += 2
				#print(loaninfo)

			self.loansinfo.append(loaninfo)
			print("sales", loaninfo["Series_of_Member_Payment_Dependent_Notes"],"added")
			loanTable_Index = 0


if __name__ == "__main__":
	filename = sys.argv[1]
	print("parsing report %s" % filename)

	report=Parse_report(filename)
	report.run_parse()