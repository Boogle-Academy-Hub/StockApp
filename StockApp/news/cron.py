from django_cron import CronJobBase, Schedule
from datetime import datetime
from .models import News

class PushCronJob(CronJobBase):
    RUN_EVERY_MINS = 1
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "news.super_awesome_push_cron"

    def do(self):
        print("test")
        n = News(title="Jeffrey Testing", created_at=datetime.now(), updated_at=datetime.now())
        n.save()