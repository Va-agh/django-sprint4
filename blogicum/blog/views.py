from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http import Http404, HttpResponseRedirect
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

NUMBER_OF_OBJECTS_ON_PAGE = 10
User = get_user_model()


def organize_queryset(filter=False, order=False):
    """Получает посты с учетом фильтрации и сортировки."""
    queryset = Post.objects.select_related("category", "author", "location")
    if filter:
        queryset = queryset.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )
    if order:
        queryset = queryset.annotate(comment_count=Count("comments")).order_by(
            "-pub_date"
        )
    return queryset


class OnlyAuthorMixin(UserPassesTestMixin):
    """Позволяет удалять и редактировать записи только авторам."""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        return HttpResponseRedirect(
            reverse_lazy("blog:post_detail", kwargs={
                         "post_id": self.kwargs["post_id"]})
        )

    def get_success_url(self, queryset=None):
        return reverse_lazy(
            "blog:post_detail", kwargs={"post_id": self.kwargs["post_id"]}
        )


class UserCreateView(CreateView):
    """Регистрация нового пользователя."""

    template_name = "registration/registration_form.html"
    form_class = UserCreationForm


class ProfileView(ListView):
    """Выводит список публикаций."""

    model = User
    template_name = "blog/profile.html"
    paginate_by = NUMBER_OF_OBJECTS_ON_PAGE

    def get_user(self):
        return get_object_or_404(User, username=self.kwargs["username"])

    def get_queryset(self):
        user = self.get_user()
        if self.request.user == user:
            queryset = organize_queryset(order=True)
        else:
            queryset = organize_queryset(filter=True, order=True)
        return queryset.filter(author=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.get_user()
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


class PostDetailView(DetailView):
    """Отображение поста."""

    queryset = organize_queryset()
    template_name = "blog/detail.html"
    pk_url_kwarg = "post_id"

    def get_object(self, queryset=None):
        post = super().get_object()
        author = post.author
        if author != self.request.user and (
            post.is_published is False
            or post.category.is_published is False
            or post.pub_date > timezone.now()
        ):
            raise Http404
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["comments"] = Comment.objects.select_related("author").filter(
            post__id=self.kwargs["post_id"]
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание нового поста.""" ""

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


class PostEditView(OnlyAuthorMixin, LoginRequiredMixin, UpdateView):
    """Редактирование поста."""

    model = Post
    form_class = PostForm
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"


class PostDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    """Удаление поста."""

    model = Post
    pk_url_kwarg = "post_id"
    template_name = "blog/create.html"

    def get_success_url(self):
        return reverse_lazy(
            "blog:profile", kwargs={"username": self.request.user.username}
        )


class CommentAddView(LoginRequiredMixin, CreateView):
    """Добавление комментария."""

    model = Comment
    form_class = CommentForm
    pk_url_kwarg = "post_id"

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, id=self.kwargs["post_id"])
        return super().form_valid(form)


class CommentEditView(OnlyAuthorMixin, UpdateView):
    """Редактирование комментария."""

    model = Comment
    form_class = CommentForm
    pk_url_kwarg = "comment_id"
    template_name = "blog/create.html"

    def get_object(self):
        return get_object_or_404(Comment, id=self.kwargs["comment_id"])


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    """Удаление комментария."""

    model = Comment
    pk_url_kwarg = "comment_id"
    template_name = "blog/create.html"

    def get_object(self):
        return get_object_or_404(Comment, id=self.kwargs["comment_id"])


class IndexView(ListView):
    """Выводит список публикаций на главную."""

    queryset = organize_queryset(filter=True, order=True)
    template_name = "blog/index.html"
    paginate_by = NUMBER_OF_OBJECTS_ON_PAGE


class CategoryView(ListView):
    """Выводит на страницу список публикаций по категориям."""

    template_name = "blog/category.html"
    model = Post
    paginate_by = NUMBER_OF_OBJECTS_ON_PAGE

    def get_category(self):
        return get_object_or_404(
            Category, is_published=True, slug=self.kwargs["category_slug"]
        )

    def get_queryset(self):
        category = self.get_category()  # выбрасывает 404?
        return organize_queryset(
            filter=True, order=True
        ).filter(
            category=category
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.get_category()
        return context
