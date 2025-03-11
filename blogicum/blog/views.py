from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from blog.forms import PostForm, CommentForm
from blog.models import Category, Post, Comment


User = get_user_model()


class OnlyAuthorMixin(UserPassesTestMixin):
    """Позволяет удалять и редактировать записи только авторам."""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class UserCreateView(CreateView):
    """Регистрация нового пользователя."""

    template_name = "registration/registration_form.html"
    form_class = UserCreationForm


class ProfileView(ListView):
    """Выводит список публикаций."""

    model = User
    template_name = "blog/profile.html"
    ordering = "id"
    paginate_by = 10

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        queryset_all = (
            Post.objects.select_related("author")
            .filter(author__username=self.kwargs["username"])
            .annotate(comment_count=Count("comment"))
            .order_by("-pub_date")
        )
        if self.request.user == user:
            return queryset_all
        return queryset_all.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = User.objects.get(username=self.kwargs["username"])
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля."""

    model = User
    form_class = UserChangeForm
    template_name = "blog/user.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            "blog:profile", kwargs={"username": self.request.user.username}
        )


class PostDetailView(UserPassesTestMixin, DetailView):
    """Отображение поста."""

    model = Post
    template_name = "blog/detail.html"
    pk_url_kwarg = "post_id"
    paginate_by = 10

    def test_func(self):
        approved_query = Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
        obj = self.get_object()
        if obj in approved_query:
            return True
        return obj.author == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["post"] = Post.objects.get(id=self.kwargs["post_id"])
        context["comments"] = Comment.objects.filter(
            post__id=self.kwargs["post_id"])
        return context

    def handle_no_permission(self):
        return HttpResponseNotFound()


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание нового поста."""''

    model = Post
    form_class = PostForm
    template_name = "blog/create.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "blog:profile", kwargs={"username": self.request.user.username}
        )


class PostEditView(OnlyAuthorMixin, UpdateView):
    """Редактирование поста."""

    model = Post
    form_class = PostForm
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"

    def handle_no_permission(self):
        return HttpResponseRedirect(
            reverse_lazy("blog:post_detail", kwargs={
                         "post_id": self.kwargs["post_id"]})
        )


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    """Удаление поста."""

    model = Post
    pk_url_kwarg = "post_id"
    template_name = "blog/create.html"
    success_url = reverse_lazy("blog:index")


class CommentAddView(LoginRequiredMixin, CreateView):
    """Добавление комментария."""

    obj = None
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = "post_id"

    def dispatch(self, request, *args, **kwargs):
        self.obj = get_object_or_404(Post, id=kwargs["post_id"])
        return super().dispatch(request, *args, **kwargs)

    # Переопределяем form_valid()
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.obj
        return super().form_valid(form)


class CommentEditView(OnlyAuthorMixin, UpdateView):
    """Редактирование комментария."""

    model = Comment
    form_class = CommentForm
    pk_url_kwarg = "comment_id"
    template_name = "blog/create.html"


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    """Удаление комментария."""

    model = Comment
    pk_url_kwarg = "comment_id"
    template_name = "blog/create.html"
    success_url = reverse_lazy("blog:index")


class IndexView(ListView):
    """Выводит список публикаций на главную."""

    template_name = "blog/index.html"
    model = Post
    paginate_by = 10

    def get_queryset(self):
        return (
            Post.objects.filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now(),
            )
            .annotate(comment_count=Count("comment"))
            .order_by("-pub_date")
        )


class CategoryView(ListView):
    """Выводит на страницу список публикаций по категориям."""

    template_name = "blog/category.html"
    model = Post
    paginate_by = 10

    def get_queryset(self):
        get_object_or_404(
            Category, is_published=True, slug=self.kwargs["category_slug"]
        )
        return (
            Post.objects.filter(
                category__slug=self.kwargs["category_slug"],
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now(),
            )
            .annotate(comment_count=Count("comment"))
            .order_by("-pub_date")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = Category.objects.get(
            slug=self.kwargs["category_slug"])
        return context
