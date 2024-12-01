from django.shortcuts import render, redirect
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema

from item.models import Category, Item
from .forms import SignupForm

@swagger_auto_schema(method='get', responses={200: 'Success'})
@api_view(['GET'])
@permission_classes([AllowAny])
def index(request):
    items = Item.objects.filter(is_sold=False).order_by('-created_at')[0:6]
    categories = Category.objects.all()
    
    # Определяем, требуется ли JSON-ответ
    if request.headers.get('accept') == 'application/json':
        items_json = [
            {
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'price': item.price,
                'image': item.image.url if item.image else None,
                'created_at': item.created_at,
                'is_sold': item.is_sold,
            }
            for item in items
        ]
        categories_json = [
            {
                'id': category.id,
                'name': category.name,
            }
            for category in categories
        ]
        return JsonResponse({'categories': categories_json, 'items': items_json})
    
    return render(request, 'core/index.html', {
        'categories': categories,
        'items': items,
    })

@swagger_auto_schema(method='get', responses={200: 'Success'})
@api_view(['GET'])
@permission_classes([AllowAny])
def contact(request):
    # Возвращаем JSON или HTML в зависимости от заголовка Accept
    if request.headers.get('accept') == 'application/json':
        return JsonResponse({'message': 'Contact page content.'})
    
    return render(request, 'core/contact.html')

@swagger_auto_schema(methods=['GET', 'POST'], responses={200: 'Success'})
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get('accept') == 'application/json':
                return JsonResponse({'message': 'Signup successful.'}, status=201)
            return redirect('/login/')
        else:
            if request.headers.get('accept') == 'application/json':
                return JsonResponse({'errors': form.errors}, status=400)
    else:
        form = SignupForm()

    # Возвращаем HTML форму или JSON данные
    if request.headers.get('accept') == 'application/json':
        return JsonResponse({'form_fields': list(form.fields.keys())})
    
    return render(request, 'core/signup.html', {
        'form': form
    })
