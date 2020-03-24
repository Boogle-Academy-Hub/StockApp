from django.db import models

# Create your models here.
class News(models.Model):
    title=models.CharField(max_length=64)
    created_at=models.DateTimeField(auto_now=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __repr__(self):
        return '<News {} @ {}>'.format(self.title, self.created_at)