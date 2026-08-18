from django.conf import settings
from django.db import models
from django.urls import reverse


class KnowledgeArticleQuerySet(models.QuerySet):
    def visible_to(self, user):
        if user.is_authenticated and user.is_staff:
            return self
        return self.filter(status=KnowledgeArticle.Status.PUBLISHED)


class KnowledgeArticle(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        PUBLISHED = "published", "Publicado"

    title = models.CharField("título", max_length=180)
    slug = models.SlugField("slug", max_length=200, unique=True)
    category = models.ForeignKey(
        "tickets.Category",
        verbose_name="categoría",
        related_name="knowledge_articles",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    summary = models.TextField("resumen")
    content = models.TextField("contenido")
    status = models.CharField(
        "estado", max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="autor",
        related_name="knowledge_articles",
        on_delete=models.PROTECT,
    )
    related_tickets = models.ManyToManyField(
        "tickets.Ticket", verbose_name="tickets relacionados", related_name="knowledge_articles", blank=True
    )
    created_at = models.DateTimeField("creado", auto_now_add=True)
    updated_at = models.DateTimeField("actualizado", auto_now=True)

    objects = KnowledgeArticleQuerySet.as_manager()

    class Meta:
        ordering = ("title",)
        verbose_name = "artículo de conocimiento"
        verbose_name_plural = "artículos de conocimiento"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("knowledge:detail", kwargs={"pk": self.pk})

    @property
    def procedure(self):
        return self.content

    @property
    def objective(self):
        return self.summary

    @property
    def is_featured(self):
        return False
