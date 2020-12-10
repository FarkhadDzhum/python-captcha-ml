#!/app/Python-3.7.9/bin/python3.7
# python3


import time
import csv
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from twocaptcha import TwoCaptcha, ValidationException, NetworkException, ApiException, TimeoutException as TimeoutExceptionCaptcha

CHROMEDRIVER_PATH = "/app/jars/workplace_parser_selenium/drivers/chromedriver"


def parse_court_acts(base_url):
    acts = []
    page_count = 0
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    try:
        browser = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
        browser.get(base_url)
        timeout = 60

        try:
            element_clickable = EC.element_to_be_clickable((By.XPATH, '//div[@class="g-recaptcha"]'))
            WebDriverWait(browser, timeout).until(element_clickable)
        except TimeoutException as e:
            print("Timed out waiting for page to load")
            raise e

        soup = bs(browser.page_source, "lxml")
        captcha_div = soup.find("div", attrs={"class": "g-recaptcha"})
        sitekey = captcha_div["data-sitekey"]

        result = {}

        try:
            config = {
                "apiKey": "d3f80ad21283b9e6045586e677fe51b8",
                "softId": 123,
                "defaultTimeout": 120,
                "recaptchaTimeout": 600,
                "pollingInterval": 10,
            }
            solver = TwoCaptcha(**config)
            result = solver.recaptcha(sitekey=sitekey, url=base_url)
            time.sleep(18)
        except ValidationException as e:
            # invalid parameters passed
            print(e)
        except NetworkException as e:
            # network error occurred
            print(e)
        except ApiException as e:
            # api respond with error
            print(e)
        except TimeoutExceptionCaptcha as e:
            # captcha is not solved so far
            print(e)
            time.sleep(5)
            result = solver.recaptcha(sitekey=sitekey, url=base_url)

        captcha_token = result["code"]

        browser.execute_script("document.getElementById('g-recaptcha-response').style.display = 'block';")
        browser.find_element_by_id("g-recaptcha-response").clear()
        browser.find_element_by_id("g-recaptcha-response").send_keys(captcha_token)
        browser.find_element_by_xpath("//input[@type='submit']").click()

        try:
            element_present = EC.presence_of_element_located((By.LINK_TEXT, '►'))
            WebDriverWait(browser, timeout).until(element_present)
        except TimeoutException as e:
            print("Timed out waiting for page to load")
            raise e

        while True:
            soup = bs(browser.page_source, "lxml")
            trs = soup.find_all("tr", attrs={'style': 'cursor: pointer;'})
            for tr in trs:
                tds = tr.find_all("td")
                try:
                    litigants = tds[1].text
                    judicial_authority = tds[2].text
                    consideration_result = tds[3].text
                    case_category = tds[4].text
                    acts.append({
                        'litigants': litigants.replace('\\n', '').strip(),
                        'judicial_authority': judicial_authority.replace('\\n', '').strip(),
                        'consideration_result': consideration_result.replace('\\n', '').strip(),
                        'case_category': case_category.replace('\\n', '').strip()
                    })
                except:
                    pass
            try:
                ignored_exceptions = (StaleElementReferenceException,)
                element_present = EC.presence_of_element_located((By.LINK_TEXT, '►'))
                WebDriverWait(browser, timeout, ignored_exceptions=ignored_exceptions).until(element_present)
                browser.find_element_by_link_text('►').click()
            except TimeoutException:
                break
            except ElementClickInterceptedException:
                break
            except NoSuchElementException:
                break
            except StaleElementReferenceException:
                pass
            time.sleep(4)
            page_count += 1
    finally:
        browser.quit()

    print("Pages parsed:", page_count)

    return acts


def write_to_csv(acts):
    with open("/app/prod/government_sources/parsing_gov_court_acts/data/gov_court_acts_parsed_file.csv", "w+", encoding="utf-8", newline="") as file:
        a_pen = csv.writer(file, delimiter="|")
        a_pen.writerow(("litigants", "judicial_authority", "consideration_result", "case_category"))
        for act in acts:
            a_pen.writerow((act["litigants"], act["judicial_authority"], act["consideration_result"], act["case_category"]))

    return 0


if __name__ == "__main__":
    base_url = f"https://office.sud.kz/courtActs/site/index.xhtml"
    acts = parse_court_acts(base_url)
    assert write_to_csv(acts) == 0
