from django.db import models
from django.utils.text import gettext_lazy as _
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_all_lexers, get_lexer_by_name
from pygments.styles import get_all_styles
from django.contrib.auth import get_user_model

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])

User = get_user_model()


class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Snippet(TimeStampModel):
    title = models.CharField(verbose_name=_("Snippet Title"), max_length=50)
    code = models.TextField(verbose_name=_("Snippet Code"))
    linenos = models.BooleanField(default=False)
    language = models.CharField(
        verbose_name=_("Snippet Language"),
        choices=LANGUAGE_CHOICES,
        default="python",
        max_length=100,
    )
    style = models.CharField(
        verbose_name=_("Snippet Style"), choices=STYLE_CHOICES, max_length=100
    )
    owner = models.ForeignKey(User, related_name="snippets", on_delete=models.CASCADE)
    highlighted = models.TextField()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["created_at"]

    def save(self, *args, **kwargs):
        """
        Use the `pygments` library to create a highlighted HTML
         representation of the code snippet.
        """
        lexer = get_lexer_by_name(self.language)
        linenos = "table" if self.linenos else False
        options = {"title": self.title} if self.title else {}
        formatter = HtmlFormatter(
            style=self.style, linenos=linenos, full=True, **options
        )
        self.highlighted = highlight(self.code, lexer, formatter)
        super(Snippet, self).save(*args, **kwargs)
