import base64
import json
import time
from datetime import datetime

import scrapy
import requests


class ProxySubmissionSpider(scrapy.Spider):
    name = "proxy_submission"
    start_urls = ['http://free-proxy.cz/en/']

    personal_token = "t_d222c9ef"
    final_proxies={}
    custom_settings = {
        "DOWNLOAD_DELAY": 5
    }

    def start_requests(self):
        self.start_time = datetime.now()
        urls = [
            'http://free-proxy.cz/en/proxylist/main/1',
            'http://free-proxy.cz/en/proxylist/main/2',
            'http://free-proxy.cz/en/proxylist/main/3',
            'http://free-proxy.cz/en/proxylist/main/4',
            'http://free-proxy.cz/en/proxylist/main/5'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        proxies = []
        for row in response.xpath('//table[@id="proxy_list"]/tbody/tr'):
            ip_script = row.xpath('.//script/text()').re_first(r'Base64\.decode\("(.+?)"\)')
            if ip_script:
                proxy_ip = base64.b64decode(ip_script).decode('utf-8')
            else:
                proxy_ip = row.xpath('.//td[1]/span/text()').get()
            proxy_port = row.xpath('.//td[2]/span/text()').get()
            if proxy_ip and proxy_port:
                proxies.append(f"{proxy_ip}:{proxy_port}")
        print(proxies)
        # Once proxies are scraped, submit the form
        proxy_chunks = [proxies[i:i+10] for i in range(0, len(proxies), 10)]
        for ten_proxies_arr in proxy_chunks:
            form_data = {'user_id': 't_d222c9ef',
                         'len': len(ten_proxies_arr),
                         'proxies': ', '.join(ten_proxies_arr)
                         }
            resp1 = requests.get('https://test-rg8.ddns.net/api/get_token')
            time.sleep(2)
            print(resp1.cookies.get('form_token'))
            resp2 = requests.post(url='https://test-rg8.ddns.net/api/post_proxies',
                                  json=form_data,
                                  headers={'cookie':f"user_id={self.personal_token};form_token={resp1.cookies.get('form_token')}"})
            saved_id = resp2.json()['save_id']
            self.final_proxies[saved_id] = proxies

    def closed(self, reason):
        end_time = datetime.now()
        elapsed_time = end_time - self.start_time
        hours, remainder = divmod(elapsed_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        with open('time.txt', 'w') as f:
            f.write(f"{hours:02}:{minutes:02}:{seconds:02}")
        with open('proxies.json', 'w') as f:
            json.dump(self.final_proxies, f)