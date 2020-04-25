import requests
from bs4 import BeautifulSoup as bs
import re
import os
url="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001409970&type=424B3&dateb=&owner=exclude&count=40"
sec_base_url="https://www.sec.gov"

result=requests.get(url)
soup=bs(result.text, 'html.parser')
links=soup.findAll('a', attrs={'href': re.compile("Archives/edgar/data")})
checked_links_file="checked_links.txt"
if os.path.exists(checked_links_file):
    f_checked_links=open(checked_links_file,"r")
    checked_links = f_checked_links.readlines()
    f_checked_links.close()
else:
    checked_links=[]

f_checked_links=open(checked_links_file,"a+")
for link in links:
    link_href=link.attrs["href"]
    import pdb;pdb.set_trace()
    if link_href in checked_links:
        continue
    else:
        doc_url=sec_base_url + link_href
        f_checked_links.write(link_href + "\n")
        print(doc_url)

f_checked_links.close()
import pdb;pdb.set_trace()