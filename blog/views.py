from django.shortcuts import render
from queue import PriorityQueue
from django.views.generic import ListView,CreateView
from .models import Post,valcalc
from django.contrib.auth.models import User

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
    return render(request, 'blog/about.html',{'title':'About'})