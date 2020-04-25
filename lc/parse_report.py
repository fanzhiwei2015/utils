import os
import sys
from bs4 import BeautifulSoup as bs
import datetime
# to form the output as below data
# results=[{"loadID","168822424","loanAmount":1000,"interestRate":0.1033,"ServiceCharge":0.01,"initialMaturity","Five years after issurance","Finalmaturity":"Five years after inssurance"..]
#
#
filename=sys.argv[1]
print("parsing report %s" % filename)
def month_to_number(m):
	mapping={
		"January":1,
		"February":2,
		"March":3,
		"April":4,
		"May":5,
		"June": 6,
		"July": 7,
		"August": 8,
		"September": 9,
		"Octor": 10,
		"November": 11,
		"December": 12,
		}
	return mapping[m]

def get_request_date(line):
	lines=line.split(" ")
	loanID=lines[2]
	rdate_y=str(lines[8])
	rdate_m=lines[6]
	rdate_m=str(month_to_number(rdate_m))
	rdate_d=str(lines[7].replace(",",""))
	rdate="-".join([rdate_y,rdate_m,rdate_d])
	return (loanID,rdate)
	
infile=open(filename,"r")
pages=[]
cur=0
pages.append("")
request_date={}
credit_report_date={}

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
	soup=bs(page,'html.parser')
	tables=soup.find_all('table')

	#table 1 loan information
	rows=tables[loanTable_Index].find_all('tr')
	loanTable_Index=0

	columns_header= rows[0].find_all('td')
	columns_data = rows[1].find_all('td')
	loaninfo={}
	cur=0
	while cur < len(columns_header):
		key=columns_header[cur].get_text().strip().replace(" ","_")
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
		rdate = datetime.datetime.now().strftime("%Y-%m-%d")
	loaninfo.update({"request_date": rdate})
	print(loaninfo)
	#import pdb;pdb.set_trace()

