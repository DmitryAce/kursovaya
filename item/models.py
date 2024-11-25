from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=250)
    
    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Categories'
        
    def __str__(self):
        return self.name


class Item(models.Model):
    category = models.ForeignKey(Category, related_name='items', on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField()
    image = models.ImageField(upload_to='item_images', blank=True, null=True)
    is_sold = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='items', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

@receiver(post_save, sender=Item)
def track_sale(sender, instance, **kwargs):
    if instance.is_sold:
        SaleStatistic.objects.get_or_create(item=instance)



class SearchStatistics(models.Model):
    query = models.CharField(max_length=250)  # Запрос пользователя
    search_count = models.PositiveIntegerField(default=0)  # Количество поисков по запросу

    class Meta:
        ordering = ['-search_count']

    def __str__(self):
        return f"{self.query} ({self.search_count} поисков)"


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user.username}"


class SaleStatistic(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    sale_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sale_date']

    def __str__(self):
        return f"{self.item.name} - {self.sale_date.strftime('%Y-%m-%d %H:%M:%S')}"
