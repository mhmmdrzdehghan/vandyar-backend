from rest_framework.permissions import BasePermission
from .models import SubProject
from account.models import Role


class IsGroupCreatorAllowed(BasePermission):

    message = "شما اجازه این عملیات را ندارید."

    def has_permission(self, request, view):
        if request.method  in ("POST", "PUT", "PATCH", "DELETE"):

            if request.user.role == Role.OWNER:
                return True

            subproject_id = request.data.get("subproject")

            if not subproject_id:
                return False

            try:
                subproject = SubProject.objects.get(id=subproject_id)
            except SubProject.DoesNotExist:
                return False

            return subproject.managers.filter(id=request.user.id).exists()

        return True
