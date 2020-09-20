import bs4         
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_binary
import slackweb
import time
import argparse
import sys

# Amazonページ取得
def get_page_from_amazon(url):
    text = ""
    options = Options()
    options.add_argument('--headless')
     
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    driver.implicitly_wait(10)

    text = driver.page_source
    driver.quit()
     
    return text

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--amazon_url", default=None)
    parser.add_argument("--slack_web_hook", default=None)
    parser.add_argument("--target_price", default=None)
    parser.add_argument("--check_time", default=600, type=int)
    args = parser.parse_args()

    if args.amazon_url == None:
        print("amazon url is none.")
        sys.exit(0)

    if args.target_price == None:
        print("target price is none.")
        sys.exit(0)

    url = args.amazon_url

    slack = None
    if args.slack_web_hook != None:
        slack = slackweb.Slack(url=args.slack_web_hook)

    target_price = args.target_price
    while True:
        try:
            text = get_page_from_amazon(url)
            amazon_soup = bs4.BeautifulSoup(text, features='lxml')

            result = amazon_soup.find("span", id="priceblock_ourprice")
            price = int(result.text.replace("￥", "").replace(",", ""))

            message = f"current price is {price}"
            print(f"\n\n\t{message}\n\n")

            # notify if current price is less than target price.
            if price < target_price:
                if slack != None:
                    slack.notify(text=message)
        except:
            print("ERROR")
        finally:
            # it checks amazon 10 min every time.
            time.sleep(args.check_time)


