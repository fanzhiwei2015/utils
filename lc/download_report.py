import requests
from bs4 import BeautifulSoup as bs
import re
import os
import traceback
from parse_report import Parse_report
import sys
import time

start=0
if len(sys.argv) > 0:
    start=sys.argv[1]
url="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001409970&type=424B3&dateb=&owner=exclude&start=%s&count=100" % start
print(url)
sec_base_url="https://www.sec.gov"
if not os.path.isdir("archives"):
    os.mkdir("archives")

result=requests.get(url)
soup=bs(result.text, 'html.parser')
links=soup.findAll('a', attrs={'href': re.compile("Archives/edgar/data")})
checked_links_file="checked_links.txt"
checked_links=[]
if os.path.exists(checked_links_file):
    f_checked_links=open(checked_links_file,"r")
    for line in f_checked_links:
        checked_links.append(line.strip())
    f_checked_links.close()


f_checked_links=open(checked_links_file,"a+")
for link in links:
    time.sleep(0.5)
    link_href=link.attrs["href"]
    #import pdb;pdb.set_trace()
    if link_href in checked_links:
        continue
    else:
        doc_url=sec_base_url + link_href
        print("opening document link %s " % doc_url)
        doc_result=requests.get(doc_url)
        doc_soup = bs(doc_result.text, 'html.parser')
        doc_links = doc_soup.findAll('a', attrs={'href': re.compile("/Archives/.*htm")})
        try:
            for doc_link in doc_links:
                doc_link_href=doc_link.attrs["href"]
                base_doc_link=doc_link_href.split("/")[-1]
                doc_link_url=sec_base_url + doc_link_href

                if not os.path.exists("archives/%s" % base_doc_link):
                    doc_link_result = requests.get(doc_link_url)
                    with open('archives/%s' % base_doc_link, 'wb') as f:
                        f.write(doc_link_result.content)
                #import pdb;pdb.set_trace()

                report = Parse_report("archives/%s" % base_doc_link )
                if "postsup" in base_doc_link:
                    report.run_parse_post()
                elif "salessup" in base_doc_link:
                    report.run_parse_sale()
                report.insert_es()
                f_checked_links.write(link_href + "\n")
                #import pdb;pdb.set_trace()
        except:
            traceback.print_exc()
            #print(tb)
        #import pdb;pdb.set_trace()




f_checked_links.close()
#import pdb;pdb.set_trace()