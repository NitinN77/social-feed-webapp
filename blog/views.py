from django.shortcuts import render
from queue import PriorityQueue
from django.views.generic import ListView,CreateView
from .models import Post,valcalc
from django.contrib.auth.models import User
from textblob import TextBlob
import pandas as pd
import io,urllib,base64
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup


def home(request):
    pq=PriorityQueue()
    posts2 = []
    posts2deq = []

    for post in Post.objects.all():
        posts2.append([-valcalc(post.content),post.title,post.content,post.author,post.date_posted])

    for x in posts2:
        pq.put(x)
    
    while not pq.empty():
        posts2deq.append(pq.get())
    context = {
        'posts':Post.objects.all(),
        'posts2deq':posts2deq,
    }
    return render(request, 'blog/home.html', context)

def home1(request):
    pq=PriorityQueue()
    posts2r = []
    posts2rdeq = []

    for post in Post.objects.all():
        posts2r.append([valcalc(post.content),post.title,post.content,post.author,post.date_posted])

    for x in posts2r:
        pq.put(x)
    
    while not pq.empty():
        get = pq.get()
        get[0]=-get[0]
        posts2rdeq.append(get)

    context = {
        'posts':Post.objects.all(),
        'posts2deq':posts2rdeq,
    }
    return render(request, 'blog/home.html', context)

class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'


class PostCreateView(CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)




def about(request):
    context = {
        'title':'About',
    }
    return render(request, 'blog/about.html',context)

#analysis

def analysis(request):
    l = []
    t1 = [1, 2, 3, 4, 5]
    t2 = [0, 0, 0, 0, 0]
    hs = []
    for post in Post.objects.all():
        temp = -valcalc(post.content)
        if temp < -0.6:
            t2[4]+=1
        elif temp >= -0.6 and temp < -0.2:
            t2[3]+=1
        elif temp >= -0.2 and temp < 0.2:
            t2[2]+=1
        elif temp >= 0.2 and temp < 0.6:
            t2[1]+=1
        elif temp > 0.6:
            t2[0]+=1
        l.append(post.content)
    d1 = {}
    for post in l:
        post = post.split(' ')
        for x in post:
            x1 = x.lower().strip()
            if x1 in d1.keys() and list(TextBlob(x1).sentiment)[0]:
                d1[x1]+=1
            else:
                d1[x1]=1
                cx = x1
                anf = filter(str.isalnum, cx)
                anf = "".join(anf)
                if list(TextBlob(anf).sentiment)[0]:
                    hs.append((anf,list(TextBlob(anf).sentiment)[0]))
    
    panels = list(d1.items())
    panels.sort(key = lambda x: x[1],reverse=True)    
    hs.sort(key = lambda x:x[1],reverse=True)
    df = pd.DataFrame(panels, columns=['Word', 'Occurences'])
    df1 = pd.DataFrame(hs, columns=['Word','Polarity'])
    hs.sort(key = lambda x:x[1])
    df2 = pd.DataFrame(hs, columns=['Word','Polarity'])
    plt.bar(t1,t2,color=['maroon', 'darkorange', 'gold', 'greenyellow', 'green'])
    plt.xlabel("Review Tone")
    plt.ylabel("Count")
    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf,format='png')
    plt.close()
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    context = {
        'df':df.head(5),
        'data':uri,
        'df1':df1.head(10),
        'df2':df2.head(10),
    }
    
    return render(request, 'blog/analysis.html',context)

def scrape(request):
    url = request.POST.get('url')
    user = User.objects.filter(username='Nitin').first()
    r = []
    if url:
        uClient = uReq(url)
        page_html = uClient.read()
        uClient.close()
        page_soup = soup(page_html, "html.parser")

        reviews = page_soup.findAll("div", {"class": "a-row a-spacing-small review-data"})
        
        for review in reviews:
            res1 = review.text.strip()
            r.append(res1)
            ScrapedReview = Post(title='Scraped Review',content=res1,author=user,value=valcalc(res1))
            ScrapedReview.save()
        
        
    context = {
        'title':'About',
        'r':r
    }
    return render(request, 'blog/scrape.html',context)