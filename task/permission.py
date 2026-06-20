from rest_framework.permissions import BasePermission


from rest_framework.permissions import BasePermission
from .models import Group
from account.models import Role



class IsTaskManagerOrOwner(BasePermission):

    message = "شما اجازه انجام این عملیات را ندارید."

    def has_permission(self, request, view):

        if request.method == "POST":

            if request.user.role == Role.OWNER:
                return True

            group_id = request.data.get("group")
            if not group_id:
                return False

            try:
                group = Group.objects.select_related("subproject").get(id=group_id)
            except Group.DoesNotExist:
                return False

            return group.subproject.managers.filter(
                id=request.user.id
            ).exists()

        return True


    def has_object_permission(self, request, view, obj):

        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        # owner اصلی سیستم
        if request.user.role == Role.OWNER:
            return True

        # manager ساب پروژه
        if obj.group.subproject.managers.filter(id=request.user.id).exists():
            return True

        # صاحب تسک
        if obj.assigned_to_id == request.user.id:
            return True

        return False

    
