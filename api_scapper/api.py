import requests
import xlwt
from xlwt import Workbook
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate


Base_url = "https://remoteok.com/api"
User_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
Request_header = {
    "user_agent" : User_agent,
    "accept_language" : "en-US, en;q=0.5" 
}

def get_job_info():
    res = requests.get(url = Base_url,headers=Request_header )
    return res.json()

def output_to_excel(data):
    wb = Workbook()
    job_sheet = wb.add_sheet("Jobs")
    header = list(data[0].keys())
    for i in range(len(header)):
        job_sheet.write(0,i,header[i]) #row, column, value
    for i in range(len(data)):
        job = data[i]
        values = list(job.values())
        for j in range(len(values)):
            job_sheet.write(i+1,j,values[j])
    wb.save("new_jobs.csv")

if __name__ == "__main__" :
    json = get_job_info()[1:]
    output_to_excel(json)