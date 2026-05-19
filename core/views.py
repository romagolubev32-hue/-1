import json

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .constants import DEFAULT_PAGE_NUMBER, PAGE_SIZE, SKILL_SUGGEST_LIMIT
from .forms import LoginForm, ProfileEditForm, ProjectForm, RegisterForm
from .models import Project, Skill, User


guest_required = user_passes_test(lambda user: not user.is_authenticated, login_url="home")


def home(request):
    projects_qs = Project.objects.select_related("owner").prefetch_related("participants")
    paginator = Paginator(projects_qs, PAGE_SIZE)
    page_number = request.GET.get("page", DEFAULT_PAGE_NUMBER)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "projects/project_list.html",
        {
            "projects": page_obj.object_list,
            "page_obj": page_obj,
        },
    )


@guest_required
def register_view(request):
    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("login")

    return render(request, "users/register.html", {"form": form})


@guest_required
def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("home")

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")


def users_list(request):
    active_skill = request.GET.get("skill")
    participants_qs = User.objects.prefetch_related("skills")

    if active_skill:
        participants_qs = participants_qs.filter(skills__name=active_skill)

    skills = Skill.objects.all()
    paginator = Paginator(participants_qs, PAGE_SIZE)
    page_number = request.GET.get("page", DEFAULT_PAGE_NUMBER)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "users/participants.html",
        {
            "participants": page_obj.object_list,
            "skills": skills,
            "active_skill": active_skill,
            "page_obj": page_obj,
        },
    )


def user_detail(request, user_id):
    profile_user = get_object_or_404(
        User.objects.prefetch_related("skills", "owned_projects__participants"),
        id=user_id,
    )
    return render(
        request,
        "users/user-details.html",
        {
            "user": profile_user,
        },
    )


@login_required
def user_edit(request, user_id):
    if request.user.id != user_id:
        return redirect("user_detail", user_id=user_id)

    form = ProfileEditForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("user_detail", user_id=request.user.id)

    return render(
        request,
        "users/edit_profile.html",
        {
            "form": form,
            "user": request.user,
        },
    )


def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
        id=project_id,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def project_create(request):
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        return redirect("project_detail", project_id=project.id)

    return render(
        request,
        "projects/create-project.html",
        {
            "form": form,
            "is_edit": False,
        },
    )


@login_required
def project_edit(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        return redirect("project_detail", project_id=project.id)

    form = ProjectForm(request.POST or None, instance=project)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("project_detail", project_id=project.id)

    return render(
        request,
        "projects/create-project.html",
        {
            "form": form,
            "project": project,
            "is_edit": True,
        },
    )


@login_required
def password_change_view(request):
    form = PasswordChangeForm(request.user, request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect("user_detail", user_id=request.user.id)

    return render(request, "users/change_password.html", {"form": form})


@require_GET
def skill_suggest(request):
    query = request.GET.get("q", "").strip()
    queryset = Skill.objects.all()

    if query:
        queryset = queryset.filter(name__icontains=query)

    skills = list(queryset[:SKILL_SUGGEST_LIMIT].values("id", "name"))
    return JsonResponse(skills, safe=False)


@login_required
@require_POST
def user_skill_add(request, user_id):
    if request.user.id != user_id:
        return JsonResponse({"error": "Forbidden"}, status=403)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    skill_id = payload.get("skill_id")
    skill_name = (payload.get("name") or "").strip()

    if skill_id:
        skill = get_object_or_404(Skill, id=skill_id)
    elif skill_name:
        skill, _ = Skill.objects.get_or_create(name=skill_name)
    else:
        return JsonResponse({"error": "Skill is required"}, status=400)

    request.user.skills.add(skill)
    return JsonResponse({"id": skill.id, "name": skill.name})


@login_required
@require_POST
def user_skill_remove(request, user_id, skill_id):
    if request.user.id != user_id:
        return JsonResponse({"error": "Forbidden"}, status=403)

    skill = get_object_or_404(Skill, id=skill_id)
    request.user.skills.remove(skill)
    return JsonResponse({"status": "ok"})


@login_required
@require_POST
def project_participation_toggle(request, project_id):
    project = get_object_or_404(Project.objects.prefetch_related("participants"), id=project_id)

    if project.owner == request.user:
        return JsonResponse({"error": "Owner cannot join own project"}, status=400)

    if project.status == Project.STATUS_CLOSED:
        return JsonResponse({"error": "Project is closed"}, status=400)

    if request.user in project.participants.all():
        project.participants.remove(request.user)
        button_text = "Участвовать"
    else:
        project.participants.add(request.user)
        button_text = "Отказаться от участия"

    participants = [
        {
            "id": member.id,
            "name": f"{member.first_name} {member.last_name}".strip(),
            "avatar": member.avatar.url if member.avatar else "/static/images/default-avatar.png",
            "profile_url": f"/users/{member.id}/",
            "role": "Автор проекта" if member.id == project.owner.id else "Участник",
        }
        for member in project.participants.all()
    ]

    return JsonResponse(
        {
            "button_text": button_text,
            "participants_count": project.participants.count(),
            "participants": participants,
        }
    )


@login_required
@require_POST
def project_complete(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        return JsonResponse({"error": "Forbidden"}, status=403)

    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])

    return JsonResponse(
        {
            "status": project.status,
            "status_label": "Закрыт",
        }
    )