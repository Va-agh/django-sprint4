from django.urls import include, path

from . import views

app_name = "blog"

post_urls = [
    path("create/", views.PostCreateView.as_view(), name="create_post"),
    path(
        "<int:post_id>/",
        views.PostDetailView.as_view(),
        name="post_detail"),
    path(
        "<int:post_id>/edit/",
        views.PostEditView.as_view(),
        name="edit_post"
    ),
    path(
        "<int:post_id>/delete/",
        views.PostDeleteView.as_view(),
        name="delete_post",
    ),
    path(
        "<int:post_id>/comment/",
        views.CommentAddView.as_view(),
        name="add_comment",
    ),
    path(
        "<int:post_id>/edit_comment/<comment_id>/",
        views.CommentEditView.as_view(),
        name="edit_comment",
    ),
    path(
        "<int:post_id>/delete_comment/<comment_id>/",
        views.CommentDeleteView.as_view(),
        name="delete_comment",
    ),

]

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path('posts/', include(post_urls)),
    path(
        "profile_edit/",
        views.ProfileEditView.as_view(),
        name="edit_profile"
    ),
    path(
        "profile/<str:username>/",
        views.ProfileView.as_view(),
        name="profile"
    ),
    path(
        "category/<slug:category_slug>/",
        views.CategoryView.as_view(),
        name="category_posts",
    ),
]
