from django.db import models

class Clothes(models.Model):
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    size = models.CharField(max_length=50) # e.g., 'S', 'M', 'L', 'XL'
    color = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    stock = models.IntegerField()
    category_id = models.IntegerField(null=True, blank=True)
    image_url = models.URLField(max_length=1000, null=True, blank=True)