
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import BlogPost, Category, Comment, User
from .forms import BlogPostForm, CommentForm, UserUpdateForm
from django.contrib.auth.forms import UserCreationForm

def home(request):
    posts = BlogPost.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    
    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Category filtering
    category_filter = request.GET.get('category', '')
    if category_filter:
        posts = posts.filter(categories__name=category_filter)
    
    # Pagination
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_filter,
        'search_query': search_query,
    }
    return render(request, 'blog/home.html', context)

class PostDetailView(DetailView):
    model = BlogPost
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        return context
    
    def post(self, request):
        post = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post-detail', pk=post.pk)
        return self.render_to_response(self.get_context_data(form=form))

class PostCreateView(LoginRequiredMixin, CreateView):
    model = BlogPost
    form_class = BlogPostForm
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = BlogPost
    form_class = BlogPostForm
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = BlogPost
    success_url = '/'
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = BlogPost.objects.filter(author=user).order_by('-created_at')
    
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile', username=request.user.username)
    else:
        form = UserUpdateForm(instance=request.user)
    
    context = {
        'profile_user': user,
        'posts': posts,
        'form': form,
    }
    return render(request, 'blog/login.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login') 
    else:
        form = UserCreationForm()
    return render(request, 'blog/register.html', {'form': form})