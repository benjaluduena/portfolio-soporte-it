from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .forms import AssetForm
from .models import Asset
from .views import AssetListView


class AssetTests(TestCase):
    def setUp(self):
        users = get_user_model()
        self.user = users.objects.create_user(username="usuario")
        self.other = users.objects.create_user(username="otro")
        self.staff = users.objects.create_user(username="staff", is_staff=True)
        self.own_asset = Asset.objects.create(
            asset_tag="NB-001", name="Notebook Dell", assigned_to=self.user
        )
        self.other_asset = Asset.objects.create(
            asset_tag="NB-002", name="Notebook Lenovo", assigned_to=self.other
        )

    def queryset_for(self, user):
        view = AssetListView()
        view.request = RequestFactory().get("/activos/")
        view.request.user = user
        return view.get_queryset()

    def test_string_and_absolute_identity(self):
        self.assertEqual(str(self.own_asset), "NB-001 · Notebook Dell")
        self.assertEqual(self.own_asset.asset_tag, "NB-001")

    def test_regular_user_only_sees_assigned_assets(self):
        self.assertEqual(list(self.queryset_for(self.user)), [self.own_asset])

    def test_staff_sees_all_assets(self):
        self.assertEqual(self.queryset_for(self.staff).count(), 2)

    def test_asset_form_requires_unique_tag_and_name(self):
        form = AssetForm(data={"asset_tag": "NB-001", "name": "Duplicada", "asset_type": "laptop", "status": "active"})
        self.assertFalse(form.is_valid())
        self.assertIn("asset_tag", form.errors)
