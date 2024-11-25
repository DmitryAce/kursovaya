from django.contrib import admin
from .models import Category, Item, SearchStatistics, SaleStatistic


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_sold', 'created_by', 'created_at')
    list_filter = ('category', 'is_sold', 'created_at')
    search_fields = ('name', 'description')


@admin.register(SearchStatistics)
class SearchStatisticsAdmin(admin.ModelAdmin):
    list_display = ('query', 'search_count')
    search_fields = ('query',)


from django.db.models import Count
from django.utils.timezone import now, timedelta

class ItemAdmin(admin.ModelAdmin):
    # Добавляем анализ популярных товаров
    def get_popular_items(self, request):
        one_month_ago = now() - timedelta(days=30)
        popular_items = Item.objects.filter(is_sold=True, created_at__gte=one_month_ago).values('name').annotate(sold_count=Count('id')).order_by('-sold_count')
        return popular_items


@admin.register(SaleStatistic)
class SaleStatisticAdmin(admin.ModelAdmin):
    list_display = ('item', 'sale_date')  # Поля для отображения в списке
    list_filter = ('sale_date', 'item__category')  # Фильтрация по дате и категории
    search_fields = ('item__name',)  # Поиск по названию товара
