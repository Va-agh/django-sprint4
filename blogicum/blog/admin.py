from django.contrib import admin

from blog.models import Category, Location, Post

admin.site.empty_value_display = 'Не задано'


class CategoryAdmin(admin.ModelAdmin):
    """Интерфейс для управления категориями"""

    list_display = (
        'title',
        'description',
        'is_published',
    )

    list_editable = (
        'is_published',
    )

    search_fields = ('title',)
    list_display_links = ('title',)


class PostAdmin(admin.ModelAdmin):
    """Интерфейс для управления постами"""

    list_display = (
        'title',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
    )
    list_editable = (
        'is_published',
        'location',
        'category'
    )
    search_fields = ('title',)
    list_filter = ('category',)
    list_display_links = ('title',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Location)
