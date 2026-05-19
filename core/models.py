from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import FileExtensionValidator
from django.db import models

from .constants import (
    MAX_NAME_LENGTH,
    MAX_PHONE_LENGTH,
    MAX_PROJECT_NAME_LENGTH,
    MAX_SKILL_NAME_LENGTH,
)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class Skill(models.Model):
    name = models.CharField("Название", max_length=MAX_SKILL_NAME_LENGTH, unique=True)

    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"
        ordering = ("name",)

    def __str__(self):
        return self.name


class User(AbstractUser):
    username = None

    first_name = models.CharField("Имя", max_length=MAX_NAME_LENGTH)
    last_name = models.CharField("Фамилия", max_length=MAX_NAME_LENGTH)
    email = models.EmailField("Email", unique=True)
    avatar = models.ImageField(
        "Аватар",
        upload_to="avatars/",
        blank=True,
        default="",
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])],
    )
    about = models.TextField("О себе", blank=True, default="")
    phone = models.CharField("Телефон", max_length=MAX_PHONE_LENGTH, blank=True, default="")
    github_url = models.URLField("GitHub", blank=True, default="")
    skills = models.ManyToManyField(
        Skill,
        verbose_name="Навыки",
        related_name="users",
        blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("-date_joined",)

    def __str__(self):
        full_name = self.get_full_name().strip()
        return full_name or self.email


class Project(models.Model):
    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"

    STATUS_CHOICES = (
        (STATUS_OPEN, "Открытый"),
        (STATUS_CLOSED, "Закрытый"),
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="Автор",
    )
    participants = models.ManyToManyField(
        User,
        related_name="projects_participating",
        blank=True,
        verbose_name="Участники",
    )
    name = models.CharField("Название проекта", max_length=MAX_PROJECT_NAME_LENGTH)
    description = models.TextField("Описание", blank=True, default="")
    github_url = models.URLField("GitHub", blank=True, default="")
    status = models.CharField(
        "Статус",
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ("-created_at",)

    def __str__(self):
        return self.name