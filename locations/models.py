from django.db import models

from shared.models import BaseModel


class Country(BaseModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=2, unique=True)

    class Meta:
        ordering = ("-name", )

    def __str__(self):
        return self.name


class City(BaseModel):
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="cities"
    )
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ("country", "name")

    def __str__(self):
        return f"{self.name}, {self.country.code}"
