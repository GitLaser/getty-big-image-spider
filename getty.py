import os
import re
from uuid import uuid4

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

requests.packages.urllib3.disable_warnings()


class Getty:
    def __init__(self):
        self.headers = {
            'cookie': 'giu=nv=1&lv=2024-07-15T06%3A14%3A30Z; vis=vid=bd2ea9cb-8a25-4d23-8b3e-b6a9e5c3215e; __gtm_referrer=https%3A%2F%2Fwww.google.com%2F; _gcl_au=1.1.1912011962.1721024091; _gid=GA1.2.1550015919.1721024092; IR_gbd=gettyimages.com; ELOQUA=GUID=A6CCADC511E64B82B053E4F9A40341AC; csrf=t=26VhkAFrUPC3sInh9YD6enjWJpwlukWwDlj%2F1Xdi6Po%3D; cart=cid=3236604900&ac=1; uac=t=Hb3iVqAQaSyn%2BaTpVshXfXU4eNRW5ihY%2FbeJno5sjw3JM53pqRJ912W3ikkSAVumve407FlW2bSUpcbYGk6X3kcXuQ7bJrCb8DXdk81BatCosg2sbIvXZHb%2FdhHiLwmitHvTskagdnoG1%2FKePgJRzoKtfaD%2FBEo%2FPZ522aEPgwA%3D%7C77u%2FVWI5SGRnbXVDcjRpT0JqRHdYWnkKMTAwCgo4MVYyR1E9PQorMXgyR1E9PQowCgoKMAoxMDAKUmxIY0lnPT0KMTAwCjAKYmQyZWE5Y2ItOGEyNS00ZDIzLThiM2UtYjZhOWU1YzMyMTVlCgo%3D%7C3%7C2%7C1&d; gtm_ppn=image_search_results; IR_4202=1721026227458%7C0%7C1721026227458%7C%7C; _ga=GA1.2.1565494583.1721024091; sp=gsrp=0&rps=closed&mi=rf%2Crm&sgl=mosaic&es=mostpopular&ei=&ci=av%2Ct%2Crf; _ga_DMJJ3WT1SM=GS1.1.1721024091.1.1.1721026295.60.0.0; unisess=M09TaGJUSVJiQU40M3FHZkErQTd5R0U1bG1ON1E0N1prTjRLYkJvUXo1QjNFWTVjNTVEMXZJOEh4N0NYaGhtZk5iRFphUFY1eCtHQzNDRmF4VHJIaFE9PS0tNFVpREY3MlkvcGlsTkhBZWdHbmVYdz09--602e6146927b55d5511f0a7a07f5efc6ee7deadc',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }
        self.domain = 'https://www.gettyimages.com'
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.http = requests.Session()
        self.http.mount("https://", adapter)
        self.http.mount("http://", adapter)

    def page_search(self, keyword):
        for page in range(1, 1000):
            res = self.search(keyword, page)
            if res == 'stop':
                return

    def search(self, keyword, page):
        keyword = keyword.replace(' ', '%20')
        url = f'https://www.gettyimages.com/search/2/image?numberofpeople=one%2Ctwo%2Cgroup&page={page}&phrase={keyword}&sort=mostpopular&license=rf%2Crm'
        res = self.http.get(url, headers=self.headers, verify=False)
        soup = BeautifulSoup(res.text, 'html.parser')
        a_tags = soup.select('.TV1lZmIBFh_LgfiQqK1O')
        if not a_tags:
            return 'stop'

        for tag in a_tags:
            if not tag:
                continue

            detail_url = self.domain + tag.attrs['href']
            src = self.get_detail(detail_url)
            if not src:
                continue

            try:
                img_id = re.search(r'(\d{7,11})', src).group(1)
            except:
                img_id = str(uuid4())

            self.save_img(src, img_id, keyword)

    def get_detail(self, url):
        res = self.http.get(url, headers=self.headers, verify=False)
        soup = BeautifulSoup(res.text, 'html.parser')
        tag = soup.select_one('.a58rsU9bXPi2pCXFikur')
        return tag.attrs.get('src')

    def save_img(self, url, img_id, keyword):
        """
        下载图片并保存到static，图片命名用md5
        """
        dir_ = f'static/{keyword}'
        if not os.path.exists(dir_):
            os.makedirs(dir_, exist_ok=True)

        img = f'{dir_}/{img_id}.png'
        if os.path.exists(img):
            return True

        chunk_size = 1024

        # 设置重试策略
        try:
            response = self.http.get(url, stream=True, timeout=10)
            response.raise_for_status()  # 检查请求是否成功

            with open(img, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:  # 忽略保持活动的新块
                        f.write(chunk)
        except requests.exceptions.RequestException as e:
            return False
        print('save img ok', img)
        return True


if __name__ == '__main__':
    ins = Getty()
    tibetan_buddhism_terms_en = [
        "Tibetan Buddhist Monk",
        "Tibetan Lama",
        "Tulku",
        "Rinpoche",
        "Dalai Lama",
        "Panchen Lama",
        "Khenpo",
        "Geshe",
        "Vajra Master",
        "Dharma King",
        "Tibetan Monk Robes",
        "Tibetan Monastic Life",
        "Tibetan Buddhist Teacher",
        "Tibetan Buddhist Practitioner",
        "Tibetan Guru",
        "Tibetan Buddhist Ceremony",
        "Tibetan Pilgrimage",
        "Tibetan Buddhist Meditation",
        "Tibetan Buddhist Chanting",
        "Tibetan Buddhist Ritual",
        "Tibetan Nun",
        "Tibetan Monastery Life",
        "Tibetan Monks in Prayer",
        "Tibetan Buddhist Retreat",
        "Tibetan Buddhist Teachings"
    ]
    for term in tibetan_buddhism_terms_en:
        ins.page_search(term)
