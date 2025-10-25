from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Group, Membership

@login_required
def group_list(request):
    groups = Group.objects.all()
    user_memberships = Membership.objects.filter(user=request.user)
    joined_group_ids = user_memberships.values_list("group_id", flat=True)
    return render(request, "groups/group_list.html", {
        "groups": groups,
        "joined_group_ids": joined_group_ids,
    })


@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    members = Membership.objects.filter(group=group)
    is_member = Membership.objects.filter(group=group, user=request.user).exists()
    return render(request, "groups/group_detail.html", {
        "group": group,
        "members": members,
        "is_member": is_member,
    })


@login_required
def group_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description", "")
        if Group.objects.filter(name=name).exists():
            messages.error(request, "Група з такою назвою вже існує.")
        else:
            group = Group.objects.create(
                name=name,
                description=description,
                owner=request.user
            )
            Membership.objects.create(user=request.user, group=group)
            messages.success(request, "Групу створено!")
            # Перехід на сторінку групи після створення
            return redirect("groups:detail", group_id=group.id)
    return render(request, "groups/group_form.html")



@login_required
def join_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    membership, created = Membership.objects.get_or_create(user=request.user, group=group)
    if created:
        messages.success(request, f"Ти приєднався до групи {group.name}!")
    else:
        messages.info(request, "Ти вже в цій групі.")
    
    # Тут змінити ім’я URL на правильне з namespace
    return redirect("groups:detail", group_id=group.id)


@login_required
def leave_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    membership = Membership.objects.filter(user=request.user, group=group)
    if membership.exists():
        membership.delete()
        messages.info(request, f"Ти вийшов з групи {group.name}.")
    else:
        messages.warning(request, "Ти не є учасником цієї групи.")
    return redirect("groups:detail", group_id=group.id)  # якщо хочеш після виходу залишати на сторінці групи




@login_required
def group_delete(request, group_id):
    group = get_object_or_404(Group, id=group_id, owner=request.user)
    if request.method == "POST":
        group.delete()
        messages.success(request, "Групу видалено.")
        return redirect("groups:list")

    return render(request, "groups/group_confirm_delete.html", {"group": group})
