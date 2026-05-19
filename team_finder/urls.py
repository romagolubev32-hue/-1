from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from core import views

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", views.home, name="home"),

    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("users/list/", views.users_list, name="users_list"),
    path("users/<int:user_id>/", views.user_detail, name="user_detail"),
    path("users/<int:user_id>/edit/", views.user_edit, name="user_edit"),

    path("users/skills/", views.skill_suggest, name="skill_suggest"),
    path("users/<int:user_id>/skills/add/", views.user_skill_add, name="user_skill_add"),
    path(
        "users/<int:user_id>/skills/<int:skill_id>/remove/",
        views.user_skill_remove,
        name="user_skill_remove",
    ),

    path("projects/create/", views.project_create, name="project_create"),
    path("projects/<int:project_id>/", views.project_detail, name="project_detail"),
    path("projects/<int:project_id>/edit/", views.project_edit, name="project_edit"),
    path(
        "projects/<int:project_id>/participation-toggle/",
        views.project_participation_toggle,
        name="project_participation_toggle",
    ),
    path(
        "projects/<int:project_id>/complete/",
        views.project_complete,
        name="project_complete",
    ),

    path("password/change/", views.password_change_view, name="password_change"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)