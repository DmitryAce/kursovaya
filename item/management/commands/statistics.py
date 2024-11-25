from django.core.management.base import BaseCommand
from item.models import SaleStatistic, SearchStatistics
from django.db.models import Count
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Displays sales statistics and search query statistics for the current month'

    def handle(self, *args, **kwargs):
        # Даты для фильтрации
        start_date = datetime.now().replace(day=1)
        end_date = (start_date + timedelta(days=31)).replace(day=1)

        # Популярные товары
        statistics = SaleStatistic.objects.filter(
            sale_date__range=(start_date, end_date)
        ).values(
            'item__name', 'item__category__name'
        ).annotate(
            total_sales=Count('item')
        ).order_by('-total_sales')

        # Вывод статистики по продажам
        if not statistics:
            self.stdout.write("No sales data available for the current month.")
        else:
            self.stdout.write("Sales statistics for the current month:\n")
            for stat in statistics:
                self.stdout.write(
                    f"Item: {stat['item__name']}, Category: {stat['item__category__name']}, Total Sales: {stat['total_sales']}"
                )

        # Топ запросов
        search_stats = SearchStatistics.objects.all().order_by('-search_count')[:10]

        if not search_stats:
            self.stdout.write("\nNo search data available.")
        else:
            self.stdout.write("\nTop search queries for the current month:\n")
            for stat in search_stats:
                self.stdout.write(
                    f"Query: '{stat.query}', Searches: {stat.search_count}"
                )
