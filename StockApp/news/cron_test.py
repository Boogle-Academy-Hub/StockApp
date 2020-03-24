from django_cron import CronJobBase, Schedule
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from .models import News

class PushCronJob(CronJobBase):
    RUN_EVERY_MINS = 1 # runs every 5 mins
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "news.super_awesome_push_cron" # has to be unique

    def do(self):
        # print("test")
        html1 = requests.get('http://text.npr.org')
        print(html1)
        print(html1.content)
        soup1 = BeautifulSoup(html1, 'html.parser')
        
        new_url = soup1.find('p').find('a')['href']
        html2 = extract_html(new_url)
        soup2 = BeautifulSoup(html2, 'html.parser')

        articles = []
        
        # n = News(title="Test", created_at=datetime.now())
        # n.save()

        for article in soup2.find_all('article'):
            title = article.find('h3')
            if title is not None:
                print("test")
                n = News(title=title.text, created_at=datetime.now())
                n.save()

    def extract_html(url):
        request = requests.get(url)
        return request.content