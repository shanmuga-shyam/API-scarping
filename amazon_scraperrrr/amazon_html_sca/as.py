from datetime import datetime
import requests
import csv
import bs4 #check for lxml is installed
import concurrent.futures
from tqdm import tqdm 

Base_url = "https://remoteok.com/api"
# Use a realistic User-Agent and correct header names
User_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
Request_header = {
    "User-Agent": User_agent,
    "Accept-Language": "en-US,en;q=0.9",
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
    # Fetch the given URL using the configured headers. Return text for BS4.
    try:
        res = requests.get(url, headers=Request_header, timeout=15)
    except Exception as e:
        print(f"request error for {url}: {e}")
        return None
    if res.status_code != 200:
        print(f"non-200 response for {url}: {res.status_code}")
        return None
    return res.text
    
def get_product_price(soup):
    if not soup:
        return None

    # Try multiple common Amazon price selectors in order of likelihood.
    selectors = [
        '#priceblock_ourprice',
        '#priceblock_dealprice',
        'span.a-price > span.a-offscreen',
        'span.a-price-whole',
        'span#priceblock_saleprice',
    ]
    

    for sel in selectors:
        el = soup.select_one(sel)
        if el and el.get_text(strip=True):
            # Some selectors return currency symbol inside text
            text = el.get_text(strip=True)
            # Normalize common formats: remove currency symbols and commas
            value =  text.replace('₹', '').replace('Rs.', '').replace(',', '').strip()
            try:
                return float(value)
            except ValueError:
                print("value error")
                exit()
    # Fallback: look for meta property
    # meta = soup.find('meta', {'property': 'product:price:amount'})
    # return meta['content'] if meta and meta.get('content') else None
def get_product_title(soup):
    product_title = soup.find("span", id="productTitle")
    return product_title.get_text(strip=True) if product_title else None
    

def get_product_rating(soup):

    if not soup:
        return None

    # Try to find rating element, falling back to any visible rating span
    el = soup.select_one('#averageCustomerReviews .a-icon-alt') or soup.select_one('span.a-icon-alt')
    return el.get_text(strip=True) if el else None

def get_product_information(soup):
    """
    Return a dict of product detail key/value pairs found in common Amazon
    product-details tables or the detail bullets section.
    """
    specs = {}
    if not soup:
        return specs

    table = soup.select_one(
        '#productDetails_techSpec_section_1, table.prodDetTable, table.a-keyvalue.prodDetTable, table#productDetails_detailBullets_sections1'
    )

    if not table:
        # Fallback: parse the detail bullets list
        if (bullets := soup.select_one('#detailBullets_feature_div')):
            for li in bullets.select('li'):
                text = li.get_text(' ', strip=True)
                if ':' in text:
                    k, v = text.split(':', 1)
                    specs[k.strip()] = v.strip()
                else:
                    parts = text.split('\n', 1)
                    if len(parts) == 2:
                        specs[parts[0].strip()] = parts[1].strip()
        return specs

    # Iterate table rows and extract th->td pairs; handle alternate structures
    for tr in table.find_all('tr'):
        th = tr.find('th')
        td = tr.find('td')
        if not th:
            th = tr.find('td', class_='prodDetSectionEntry')
        if not td:
            td = tr.find('td', class_='prodDetAttrValue')

        if not th and td:
            tds = tr.find_all('td')
            if len(tds) >= 2:
                key = tds[0].get_text(' ', strip=True)
                val = tds[1].get_text(' ', strip=True)
                if key:
                    specs[key] = val
            continue

        key = th.get_text(' ', strip=True) if th else None
        val = td.get_text(' ', strip=True) if td else None
        if key:
            specs[key] = val

    return specs
def extract_product_info(url):
    print(f"scraped_url: {url}")
    html = get_page_html(url=url)
    if not html:
        return {"price": None}
    soup = bs4.BeautifulSoup(html, "lxml")
    price = get_product_price(soup)
    title = get_product_title(soup)
    rating = get_product_rating(soup)
    information = get_product_information(soup)
    return {"price": price, "title": title, "rating": rating, "information": information}
    
if __name__ == "__main__":
    # file_creator("amazon_products_urs.csv")
    # Open using UTF-8 to avoid Windows cp1252 decode errors. If the file contains
    # bytes that aren't valid UTF-8, you can change errors='replace' or fall back
    # to latin-1 as needed.
    # Open file with utf-8 and replace errors to avoid decode crashes from mixed encodings.
    product_data = []
    with open("amazon_products_urs.csv", newline="", encoding='utf-8', errors='replace') as csvfile:
        readers = csv.reader(csvfile, delimiter=",")
        for row in readers:
            url = row[0]
            print(url)
            product_data.append(extract_product_info(url))
    output_filename = f'output-{datetime.now().strftime("%m-%d-%y")}.csv'
    with open(output_filename, "w") as outputfile:
        writer = csv.writer(outputfile)
        writer.writerow(product_data[0].keys())
        for i in product_data:
            writer.writerow(i.values())