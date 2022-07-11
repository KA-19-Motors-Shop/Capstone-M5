from django.db import models


class Convenio(models.Model):
    id   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    tipo = models.CharField(max_length=127)