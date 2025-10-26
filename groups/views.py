from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Group, Membership, GroupPost
from .forms import GroupForm, GroupPostForm


@login_required
def group_list(request):
    groups = Group.objects.all()
    joined_ids = Membership.objects.filter(user=request.user).values_list("group_id", flat=True)
    return render(request, "groups/group_list.html", {"groups": groups, "joined_group_ids": joined_ids})


@login_required
def group_detail(request, pk):
    group = get_object_or_404(Group, pk=pk)
    membership = Membership.objects.filter(user=request.user, group=group).first()
    is_member = membership is not None  # ✅ ця змінна для кнопок приєднання/виходу
    members = Membership.objects.filter(group=group).select_related("user")
    posts = group.posts.all().order_by("-created_at")

    return render(request, "groups/group_detail.html", {
        "group": group,
        "membership": membership,
        "is_member": is_member,
        "members": members,
        "posts": posts,
        "user": request.user,  # щоб перевірки в шаблоні працювали
    })


@login_required
def create_group(request):
    if request.method == "POST":
        form = GroupForm(request.POST)
    if form.is_valid():
        group = form.save(commit=False)
        group.creator = request.user
        group.owner = request.user
        group.save()
        Membership.objects.create(user=request.user, group=group, is_moderator=False)
        messages.success(request, "Групу створено!")
        return redirect("groups:detail", pk=group.pk)

    else:
        form = GroupForm()
    return render(request, "groups/group_form.html", {"form": form})


@login_required
def join_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    Membership.objects.get_or_create(user=request.user, group=group)
    messages.success(request, f"Ти приєднався до групи {group.name}!")
    return redirect("groups:detail", pk=pk)


@login_required
def leave_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    Membership.objects.filter(user=request.user, group=group).delete()
    messages.success(request, f"Ти покинув групу {group.name}.")
    return redirect("groups:list")


def create_post(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == "POST":
        form = GroupPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.group = group
            post.author = request.user
            post.save()
            return redirect("groups:detail", pk=group.id)
    else:
        form = GroupPostForm()
    return render(request, "groups/group_post_form.html", {"form": form, "group": group})


@login_required
def delete_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.user != group.owner:
        # можна додати повідомлення про помилку
        return redirect("groups:detail", pk=pk)
    
    if request.method == "POST":
        group.delete()
        return redirect("groups:list")
    
    # Для GET можна показати підтвердження видалення
    return render(request, "groups/group_confirm_delete.html", {"group": group})

@login_required
def delete_post(request, pk, post_id):
    group = get_object_or_404(Group, pk=pk)
    post = get_object_or_404(GroupPost, pk=post_id, group=group)
    membership = Membership.objects.filter(user=request.user, group=group).first()

    if request.user == post.author or (membership and membership.is_moderator):
        post.delete()
        messages.success(request, "Пост видалено.")
    else:
        messages.error(request, "Ти не маєш прав для видалення цього поста.")
    return redirect("groups:detail", pk=pk)


@login_required
def manage_moderators(request, pk):
    """Сторінка керування модераторами (доступна лише власнику групи)."""
    group = get_object_or_404(Group, pk=pk)

    if request.user != group.owner:  # ✅ виправлено creator → owner
        messages.error(request, "Ти не маєш прав для керування модераторами!")
        return redirect("groups:detail", pk=pk)

    members = Membership.objects.filter(group=group).select_related("user")

    return render(request, "groups/manage_moderators.html", {
        "group": group,
        "members": members
    })


@login_required
def toggle_moderator(request, pk, user_id):
    """Перемикає статус модератора для користувача."""
    group = get_object_or_404(Group, pk=pk)
    membership = get_object_or_404(Membership, group=group, user_id=user_id)

    if request.user != group.owner:  # ✅ виправлено creator → owner
        messages.error(request, "Тільки власник групи може змінювати модераторів!")
        return redirect("groups:manage_moderators", pk=pk)

    # Заборона зняти самого себе
    if membership.user == group.owner:  # ✅ виправлено creator → owner
        messages.error(request, "Ти не можеш змінювати статус власника!")
        return redirect("groups:manage_moderators", pk=pk)

    membership.is_moderator = not membership.is_moderator
    membership.save()
    status = "призначено модератором" if membership.is_moderator else "знято з модераторів"
    messages.success(request, f"{membership.user.username} {status}.")
    return redirect("groups:manage_moderators", pk=pk)
