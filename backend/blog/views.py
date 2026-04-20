from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Post, Comment, Like
from .forms import PostForm, CommentForm, UserRegisterForm

def post_list(request):
    query = request.GET.get('q')
    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).order_by('-created_at')
    else:
        posts = Post.objects.all().order_by('-created_at')
    return render(request, 'blog/post_list.html', {'posts': posts, 'query': query})

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    # Increment view count
    post.views += 1
    post.save(update_fields=['views'])
    
    comments = post.comments.all().order_by('-created_at')
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('post_detail', slug=post.slug)
    else:
        form = CommentForm()
        
    user_has_liked = False
    if request.user.is_authenticated:
        user_has_liked = Like.objects.filter(post=post, user=request.user).exists()
        
    return render(request, 'blog/post_detail.html', {
        'post': post, 
        'comments': comments, 
        'form': form,
        'user_has_liked': user_has_liked,
        'like_count': Like.objects.filter(post=post).count()
    })

@login_required
def post_like(request, slug):
    if request.method == 'POST':
        post = get_object_or_404(Post, slug=slug)
        like, created = Like.objects.get_or_create(post=post, user=request.user)
        
        if not created:
            # If the like already exists, the user is unliking it
            like.delete()
            is_liked = False
        else:
            is_liked = True
            
        like_count = Like.objects.filter(post=post).count()
        return JsonResponse({'is_liked': is_liked, 'like_count': like_count})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Create Post'})

@login_required
def post_update(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if post.author != request.user:
        messages.error(request, 'You are not authorized to edit this post.')
        return redirect('post_detail', slug=slug)
        
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Edit Post'})

@login_required
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if post.author != request.user:
        messages.error(request, 'You are not authorized to delete this post.')
        return redirect('post_detail', slug=slug)
        
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('post_list')
    return render(request, 'blog/post_confirm_delete.html', {'post': post})

from django.contrib.auth import login

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Your account has been created and you are now logged in!')
            return redirect('post_list')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})
