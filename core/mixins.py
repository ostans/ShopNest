from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404


class SellerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    raise_exception = False

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and getattr(user, "seller_profile")

    def handle_no_permission(self):
        if not hasattr(self.request.user, "seller_profile"):
            raise PermissionDenied("You need a seller account to access this page.")
        return super().handle_no_permission()


class StoreOwnerRequiredMixin(SellerRequiredMixin):
    store_slug_url_kwarg = "store_slug"

    def dispatch(self, request, *args, **kwargs):

        from stores.models import Store

        self.store = get_object_or_404(
            Store,
            slug=self.kwargs.get(self.store_slug_url_kwarg),
        )
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        if not super().test_func():
            return False
        return self.store.owner_id == self.request.user.id
