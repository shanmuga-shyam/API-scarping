from datetime import datetime
import requests
import csv
import bs4 #check for lxml is installed


Base_url = "https://remoteok.com/api"
User_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
Request_header = {
    "user_agent" : User_agent,
    "accept_language" : "en-US, en;q=0.5" 
}

def file_creator(filename):
    if not filename.endswith(".csv"):
        filename += ".csv"
    # Create a real text CSV file (not an Excel workbook saved with .csv extension).
    # Previously this used xlwt.Workbook which writes a binary Excel file even when
    # the filename ends with .csv. Reading that file with the csv module caused
    # UnicodeDecodeError on Windows. Create an empty UTF-8 CSV instead.
    with open(filename, mode='w', encoding='utf-8', newline='') as f:
        # Optionally write a header row here. Keep file empty for now.
        pass




def get_page_html(url):
    res = requests.get(url = Base_url,headers=Request_header )
    return res.content   
    
def extract_product_info(url):
    product_info = {}
    print(f"scraped_url: {url}")
    html =  get_page_html(url=url)
    print(html)
    
    
if __name__ == "__main__":
    # file_creator("amazon_products_urs.csv")
    # Open using UTF-8 to avoid Windows cp1252 decode errors. If the file contains
    # bytes that aren't valid UTF-8, you can change errors='replace' or fall back
    # to latin-1 as needed.
    with open("amazon_products_urs.csv", newline="") as csvfile:
        readers = csv.reader(csvfile, delimiter=",")
        for row in readers:
            url = row[0]
            print(url)
            print(extract_product_info(url))