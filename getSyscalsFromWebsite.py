from bs4 import BeautifulSoup
import requests

page_source = requests.get("https://filippo.io/linux-syscall-table/").content
soup = BeautifulSoup(page_source, 'html.parser')

table=soup.select_one("table.tbls-table")
entries =table.find_all("tr", class_="tbls-entry-collapsed")

outputCsv=open("syscalls.csv","w+")
outputCsv.write("name,".ljust(22,' ')+"sys_number,".ljust(21,' ')+"arg_len"+"\n")

for entry in entries:
    nextSibling=entry.find_next_sibling()
    if(nextSibling['class'][0] =='tbls-arguments-collapsed' ):
        argLen = len(nextSibling.select('td > strong'))
        out=f"{entry.findChildren()[1].text},".ljust(25,' ')+f"{entry.findChildren()[0].text},".ljust(21,' ')+f"{argLen}"+"\n"
        outputCsv.write(out)
        outputCsv.flush()

outputCsv.close()