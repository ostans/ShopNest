from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class SellerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    raise_exception = False

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and getattr(user, "seller_profile")

    def handle_no_permission(self):
        if not hasattr(self.request.user, "seller_profile"):
            raise PermissionDenied("You need a seller account to access this page.")
        return super().handle_no_permission()
