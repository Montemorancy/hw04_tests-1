from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from yatube.utils import pagination

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    template = 'posts/index.html'
    posts = pagination(request, Post.objects.all())
    context = {
        'page_obj': posts
    }
    return render(request, template, context)


def group_posts(request, slug):
    group_template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = pagination(request, posts)
    context = {
        'group': group,
        'page_obj': paginator,
    }
    return render(request, group_template, context)


def profile(request, username):
    profile_template = 'posts/profile.html'
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    paginator = pagination(request, posts)
    count = user.posts.count()
    context = {
        'page_obj': paginator,
        'author': user,
        'count': count
    }
    return render(request, profile_template, context)


def post_detail(request, post_id):
    post_detail_template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    post_count = post.author.posts.count()
    context = {
        'post': post,
        'author': post.author,
        'post_count': post_count,
    }
    return render(request, post_detail_template, context)


@ login_required
def post_create(request):
    create_post_template = 'posts/create_post.html'
    group = Group.objects.all()
    form = PostForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('posts:profile', username=request.user.username)

    context = {
        'form': form,
        'group': group
    }
    return render(request, create_post_template, context)


def post_edit(request, post_id):
    post_edit_template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.id)
    context = {
        'form': form,
        'post': post,
        'is_edit': True
    }
    return render(request, post_edit_template, context)
