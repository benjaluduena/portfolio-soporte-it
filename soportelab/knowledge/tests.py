from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from tickets.models import Category, Ticket

from .forms import KnowledgeArticleForm
from .models import KnowledgeArticle


class KnowledgeArticleTests(TestCase):
    def setUp(self):
        users = get_user_model()
        self.staff = users.objects.create_user(username="autor", is_staff=True)
        self.user = users.objects.create_user(username="lector")
        self.category = Category.objects.create(name="Software")
        self.published = KnowledgeArticle.objects.create(
            title="Limpiar espacio en Windows",
            slug="limpiar-espacio-windows",
            category=self.category,
            summary="Procedimiento seguro",
            content="Pasos del procedimiento",
            status=KnowledgeArticle.Status.PUBLISHED,
            author=self.staff,
        )
        self.draft = KnowledgeArticle.objects.create(
            title="Borrador",
            slug="borrador",
            summary="No publicado",
            content="Pendiente de revisión",
            author=self.staff,
        )

    def test_public_and_regular_users_only_see_published_articles(self):
        self.assertEqual(
            list(KnowledgeArticle.objects.visible_to(AnonymousUser())), [self.published]
        )
        self.assertEqual(list(KnowledgeArticle.objects.visible_to(self.user)), [self.published])

    def test_staff_sees_drafts(self):
        self.assertEqual(KnowledgeArticle.objects.visible_to(self.staff).count(), 2)

    def test_article_can_reference_source_ticket(self):
        ticket = Ticket.objects.create(
            title="Falta espacio",
            description="Disco al 99%",
            category=self.category,
            requester=self.user,
        )
        self.published.related_tickets.add(ticket)
        self.assertEqual(list(self.published.related_tickets.all()), [ticket])

    def test_article_form_rejects_duplicate_slug(self):
        form = KnowledgeArticleForm(
            data={
                "title": "Otro artículo",
                "slug": self.published.slug,
                "summary": "Resumen",
                "content": "Contenido",
                "status": KnowledgeArticle.Status.PUBLISHED,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("slug", form.errors)
