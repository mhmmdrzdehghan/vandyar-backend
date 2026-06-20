from rest_framework.permissions import BasePermission
from account.models import Role


class IsProjectOwner(BasePermission):
    message = "فقط مدیر سیستم اجازه ایجاد یا ویرایش پروژه را دارد."
    

    def has_permission(self, request, view):
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            return request.user.role == Role.OWNER

        return True
    


class IsSubProjectManagerOrOwner(BasePermission):

    message = "شما اجازه انجام این عملیات را ندارید."

    def has_permission(self, request, view):
        if request.method == "POST":
            return request.user.role == Role.OWNER

        return True

    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        if request.user.role == Role.OWNER:
            return True

        if obj.managers.filter(id=request.user.id).exists():
            return True

        return False

