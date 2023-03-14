from django.core.validators import MinLengthValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=10, validators=[MinLengthValidator(5)], unique=True)


class Ad(models.Model):
    name = models.CharField(max_length=250, validators=[MinLengthValidator(10)])
    author_id = models.ForeignKey('users.User', on_delete=models.CASCADE)
    price = models.PositiveIntegerField()
    description = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=300)
    is_published = models.BooleanField(default=False)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='ads/', null=True, blank=True)


class Selection(models.Model):
    name = models.CharField(max_length=250)
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE)
    items = models.ManyToManyField(Ad)

    class Meta:
        verbose_name = 'Подборка'
        verbose_name_plural = 'Подборки'

    def __str__(self):
        return self.name

