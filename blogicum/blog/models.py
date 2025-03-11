from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

User = get_user_model()

MAX_LENGTH = 256


class PublishedCreated(models.Model):
    """
    Абстрактная модель.
    Добавляет к модели дату создания и флаг публикации.
    """

    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликовано",
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Добавлено")

    class Meta:
        abstract = True


class Category(PublishedCreated):
    """Модель для таблицы Категории"""

    title = models.CharField(max_length=MAX_LENGTH, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    slug = models.SlugField(
        unique=True,
        verbose_name="Идентификатор",
        help_text=(
            "Идентификатор страницы для URL; "
            "разрешены символы латиницы, цифры, дефис и подчёркивание."
        ),
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title


class Location(PublishedCreated):
    """Модель для таблицы Местоположение"""

    name = models.CharField(max_length=MAX_LENGTH,
                            verbose_name="Название места")

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return self.name


class Post(PublishedCreated):
    """Модель для таблицы Публикации"""

    title = models.CharField(max_length=MAX_LENGTH, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст")
    image = models.ImageField("Фото", upload_to="images", blank=True)
    pub_date = models.DateTimeField(
        verbose_name="Дата и время публикации",
        help_text=(
            "Если установить дату и время в будущем — "
            "можно делать отложенные публикации."
        ),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор публикации",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
        verbose_name="Местоположение",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="posts",
        verbose_name="Категория",
    )

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        ordering = ("-pub_date",)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"post_id": self.pk})


class Comment(PublishedCreated):
    """Модель для комментариев к публикации"""

    text = models.TextField("Текст комментария")
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comment",
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ("created_at",)

    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"post_id": self.post.pk})
