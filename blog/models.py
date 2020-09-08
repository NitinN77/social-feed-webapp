from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

map = [""]

def valcalc(s):
    value = 0
    spl = s.split(' ')
    for x in spl:
        if x=='xbox':
            value+=1
    return value

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.IntegerField(default=0)

    def __str__(self):
        return(self.title)


