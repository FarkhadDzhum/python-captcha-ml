import shutil
import requests
from predict import predict
from pathlib import Path
from bs4 import BeautifulSoup as bs


def parse_missing(url_post, url_get, iin, doc_number):
    req_setting = {
        "headers": {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
        },
        "timeout": 5,
    }
    captcha_value = ""

    with requests.Session() as s:
        res = s.get(url_post, verify=False)
        soup = bs(res.content, "html.parser")

        for img in soup.find_all("img"):
            link = img.get("src")
            if "captcha" in link:
                link = "http://qamqor.gov.kz" + link
                path = str(
                    Path(__file__).parent.absolute()
                ) + "/captchas/{}.jpg".format(link.split("=")[1])
                res_img = s.get(
                    link,
                    headers=req_setting.get("headers"),
                    timeout=req_setting.get("timeout"),
                    stream=True,
                )
                if res_img.status_code == 200:
                    with open(path, "wb") as f:
                        res_img.raw.decode_content = True
                        shutil.copyfileobj(res_img.raw, f)
                    captcha_value = predict(path)

    return captcha_value


def retrieve_data_penalties(iin, doc_number):
    url_post = "https://qamqor.gov.kz/portal/page/portal/POPageGroup/Services/Su1ap"
    url_get = f"https://qamqor.gov.kz/portal/page/portal/POPageGroup/Services/Su1ap?_piref36_258203_36_246080_246080.__ora_navigState=eventSubmit_doSearch%3DPENALTY&_piref36_258203_36_246080_246080.__ora_navigValues="
    penalties = parse_missing(url_post, url_get, iin, doc_number)
    return penalties
