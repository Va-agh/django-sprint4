from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse_lazy, reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.db.models import Count

from blog.models import Category, Post, Comment
from blog.forms import PostForm, CommentForm


User = get_user_model()

class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

class UserCreateView(CreateView):
    template_name='registration/registration_form.html'
    form_class=UserCreationForm
    #success_url=reverse_lazy('pages:homepage')

class ProfileView(ListView):
    model = User
    template_name = 'blog/profile.html'
    ordering = 'id'
    paginate_by = 10
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        queryset_all = Post.objects.select_related('author').filter(author__username=self.kwargs['username'])
        if self.request.user == user:
            return queryset_all
        return queryset_all.filter(is_published=True, category__is_published=True, pub_date__lte=timezone.now())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = User.objects.get(username=self.kwargs['username'])
        return context

    
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name='blog/create.html'

    def form_valid(self, form):
        # Присвоить полю author объект пользователя из запроса.
        form.instance.author = self.request.user
        # Продолжить валидацию, описанную в форме.
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('blog:profile',args=[self.request.user])


class PostEditView(OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name='blog/create.html'
    pk_url_kwarg = 'post_id'

   
class PostDetailView(UserPassesTestMixin, DetailView):
    model = Post
    template_name='blog/detail.html'
    pk_url_kwarg = 'post_id'
   

    def test_func(self):
        approved_query = Post.objects.filter(is_published=True, category__is_published=True, pub_date__lte=timezone.now())
        obj = self.get_object()
        if obj in approved_query:
            return True
        return obj.author == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['post'] = Post.objects.get(id=self.kwargs['post_id'])
        context['comments'] = Comment.objects.filter(post__id=self.kwargs['post_id'])
        return context


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name ='blog/create.html'
    success_url = reverse_lazy('blog:index')
   

class CommentAddView(LoginRequiredMixin, CreateView):
    obj = None
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        self.obj = get_object_or_404(Post, id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    # Переопределяем form_valid()
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.obj
        return super().form_valid(form)


class CommentEditView(OnlyAuthorMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name='blog/create.html'
    


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name='blog/create.html'
    success_url = reverse_lazy('blog:index')
    
    

class IndexView(ListView):
    template_name = 'blog/index.html'
    model = Post
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True, category__is_published=True, pub_date__lte=timezone.now()
            ).annotate(comment_count=Count('comment')
            ).order_by('-pub_date')


class CategoryView(ListView):
    template_name = 'blog/category.html'
    model = Post
    paginate_by = 10


    def get_queryset(self):
        get_object_or_404(Category, is_published=True, slug=self.kwargs['category_slug'])
        return Post.objects.filter(
            category__slug=self.kwargs['category_slug'],
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
            ).annotate(
            comment_count=Count('comment')
            ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.get(slug=self.kwargs['category_slug'])
        return context
    



