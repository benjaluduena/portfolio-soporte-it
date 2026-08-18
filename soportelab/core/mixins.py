from django.contrib.auth.mixins import UserPassesTestMixin


class StaffRequiredMixin(UserPassesTestMixin):
    """Restricts mutating views to help-desk staff."""

    raise_exception = True

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff
