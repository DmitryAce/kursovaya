from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Count, Q
from drf_yasg import openapi

from item.models import Item, Category

PAGINATION = 2

item_list_response = openapi.Response(
    description="List of items",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'items': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                        'description': openapi.Schema(type=openapi.TYPE_STRING),
                        'price': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT),
                        'image': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI),
                        'is_sold': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'created_by': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                    }
                ),
            ),
            'categories': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                ),
            ),
        }
    )
)

def paginate_items(request, items):
    """Helper function to paginate items."""
    paginator = Paginator(items, PAGINATION)
    page = request.GET.get('page')

    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)

    return items, paginator

@swagger_auto_schema(
    method='get',
    responses={200: 'Success'},
    operation_description="Получить список элементов, созданных текущим пользователем",
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def index(request):
    items = Item.objects.filter(created_by=request.user)
    category_ids_with_items = items.values_list('category_id', flat=True).distinct()
    categories = Category.objects.filter(id__in=category_ids_with_items)

    categories = categories.annotate(
        user_item_count=Count('items', filter=Q(items__created_by=request.user))
    )
    
    items, paginator = paginate_items(request, items)

    # Определяем, HTML или JSON требуется вернуть
    if request.headers.get('accept') == 'application/json':
        items_json = [
            {
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'price': item.price,
                'image': item.image.url if item.image else None,
                'is_sold': item.is_sold,
                'created_by': item.created_by.id,
                'created_at': item.created_at,
            }
            for item in items
        ]
        categories_json = [
            {
                'id': category.id,
                'name': category.name,
                'user_item_count': category.user_item_count,
            }
            for category in categories
        ]
        return JsonResponse({'items': items_json, 'categories': categories_json})

    return render(request, 'dashboard/index.html', {
        'items': items,
        'categories': categories,
        'paginator': paginator,
    })


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('query', openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING),
        openapi.Parameter('category', openapi.IN_QUERY, description="Category ID", type=openapi.TYPE_INTEGER),
    ],
    responses={
        200: item_list_response,
        400: openapi.Response(description="Invalid input"),
    },
    operation_summary="Get a list of items of category",
    operation_description="Retrieve a list of items that match category ID. Returns a list of items with their details.",
    tags=['Items']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def category(request, pk):
    categoryName = get_object_or_404(Category, pk=pk)
    categoryname = "Мои товары в категории " + str(categoryName).lower()
    items = Item.objects.filter(is_sold=False, category=pk, created_by=request.user)
    
    items, paginator = paginate_items(request, items)

    # Определяем, HTML или JSON требуется вернуть
    if request.headers.get('accept') == 'application/json':
        items_json = [
            {
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'price': item.price,
                'image': item.image.url if item.image else None,
                'is_sold': item.is_sold,
                'created_by': item.created_by.id,
                'created_at': item.created_at,
            }
            for item in items
        ]
        return JsonResponse({'items': items_json, 'category': {'id': categoryName.id, 'name': categoryName.name}})

    return render(request, 'item/category.html', {
        'items': items,
        'categoryName': categoryName,
        'categoryname': categoryname,
        'paginator': paginator,
    })
