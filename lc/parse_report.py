import os
import sys
from bs4 import BeautifulSoup as bs
# to form the output as below data
# results=[{"loadID","168822424","loanAmount":1000,"interestRate":0.1033,"ServiceCharge":0.01,"initialMaturity","Five years after issurance","Finalmaturity":"Five years after inssurance"..]
#
#
filename=sys.argv[1]
print("parsing report %s" % filename)
def month_to_number(m):
	mapping={
		"January":1,
		"April": 4,
		}
	return mapping[m]

def get_request_date(line):
	lines=line.split("\s+")
	loanID=lines[2]
	rdate_y=lines[8]
	rdate_m=lines[6]
	rdate_m=month_to_number(rdate_m)
	rdate_d=lines[7].replace(",","")
	rdate="-".join(rdate_y,rdate_m,rdate_d)
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
		loanID,rdate=get_request_date(line)
		request_date.update({loanID:rdate})	
	elif "A credit bureau reported the following information" in line:
		#crdate=get_cr_date(line)
		pass
	else
		pages[cur] += line

for page in pages:
	soup=bs(page,'html.parser')
	tables=soup.find_all('table')
	import pdb;pdb.set_trace()
