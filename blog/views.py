from django.shortcuts import render
from queue import PriorityQueue
from django.views.generic import ListView,CreateView
from .models import Post,valcalc
from django.contrib.auth.models import User
from textblob import TextBlob
import pandas as pd
import io,urllib,base64
import matplotlib
import statistics
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import spacy

nlp = spacy.load("en_core_web_sm")

def nlpf(s):
    ret = []
    rets = ''
    doc = nlp(s)
    str1 = ', '
    str2 = ', '
    rets += 'Nouns: ' + str1.join([chunk.text for chunk in doc.noun_chunks]) + '\n\n'
    rets += 'Verbs: ' + str2.join([token.lemma_ for token in doc if token.pos_ == "VERB"]) + '\n\n'
    text = []
    pos = []
    dep = []
    for token in doc:
        if token.dep_ != 'punct':
            text.append(token.text)
            pos.append(token.pos_)
            dep.append(token.dep_)
    df = pd.DataFrame(list(zip(text, pos, dep)), columns=['Word', 'Pos', 'Dep'])
    ret = [rets, df]

    return ret


def clean(s):
    cx = s
    anf = filter(str.isalnum, cx)
    anf = "".join(anf)
    return anf


def home(request):
    pq=PriorityQueue()
    posts2 = []
    posts2deq = []

    for post in Post.objects.all():
        posts2.append([-valcalc(post.content)-valcalc(post.title),post.title,post.content,post.author,post.date_posted,clean(post.title)])

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
        posts2r.append([valcalc(post.content)+valcalc(post.title),post.title,post.content,post.author,post.date_posted,clean(post.title)])
        
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
    dfw = []
    dfo = []
    pvalues = []
    svalues = []
    for post in Post.objects.all():
        temp1 = list(TextBlob(post.content).sentiment)[0]+list(TextBlob(post.title).sentiment)[0]
        temp = -temp1
        temp2 = list(TextBlob(post.content).sentiment)[1]+list(TextBlob(post.title).sentiment)[1]
        pvalues.append(temp1)
        svalues.append(temp2)
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
    print(t2)
    d1 = {}
    pl = list(range(1,len(pvalues)+1))
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
                if  list(TextBlob(anf).sentiment)[0]:
                    hs.append((anf,list(TextBlob(anf).sentiment)[0]))
    
    panels = list(d1.items())
    panels.sort(key = lambda x: x[1],reverse=True)    
    hs.sort(key = lambda x:x[1],reverse=True)
    df = pd.DataFrame(panels, columns=['Word', 'Occurences'])
    df1 = pd.DataFrame(hs, columns=['Word','Polarity'])
    hs.sort(key = lambda x:x[1])
    df2 = pd.DataFrame(hs, columns=['Word','Polarity'])
    pmean,pvar,smean,svar=0,0,0,0
    if len(pvalues):
        pmean=round(statistics.mean(pvalues),3)
        pvar=round(statistics.variance(pvalues),3)
        smean=round(statistics.mean(svalues),3)
        svar=round(statistics.variance(svalues),3)
    context = {
        'df':df.head(10),
        'df1':df1.head(10),
        'df2':df2.head(10),
        't1':t1,
        't2':t2,
        'pvalues':pvalues,
        'svalues':svalues,
        'pl':pl,
        'pmean':pmean,
        'pvar':pvar,
        'smean':smean,
        'svar':svar,
    }
    
    return render(request, 'blog/analysis.html',context)

def scrape(request):
    url = request.POST.get('url')
    r = []
    r1 = []
    if url:
        uClient = uReq(url)
        page_html = uClient.read()
        uClient.close()
        page_soup = soup(page_html, "html.parser")

        reviews = page_soup.findAll("div", {"class": "a-row a-spacing-small review-data"})
        review_titles = page_soup.findAll("a", {"class": "a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold"})

        for i in range(len(reviews)):
            res1 = reviews[i].text.strip()
            res2 = review_titles[i].text.strip()
            r.append(res1)
            r1.append(res2)
            ScrapedReview = Post(title=res2,content=res1,author=request.user,value=valcalc(res1)+valcalc(res2))
            ScrapedReview.save()
    
    context = {
        'title':'About',
        'r':r,
    }
    return render(request, 'blog/scrape.html',context)


def lp(request):
    posts2 = []
    for post in Post.objects.all():
        posts2.append([-valcalc(post.content)-valcalc(post.title),post.title,post.content,post.author,post.date_posted,clean(post.title),nlpf(post.content)[0],nlpf(post.content)[1]])
    context = {
        'posts':posts2,

    }
    return render(request, 'blog/nlp.html', context)
    