from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Item, Category, SearchStatistics
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO


class ItemTests(TestCase):
    
    def setUp(self):
        # Создаем пользователя
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        image = SimpleUploadedFile(name='test_image.jpg', content=b'file_content', content_type='image/jpeg')
        # Создаем категорию
        self.category = Category.objects.create(name='Test Category')
        
        # Создаем элемент
        self.item = Item.objects.create(
            name='Test Item',
            description='Test Description',
            price=100.0,
            category=self.category,
            created_by=self.user,
            is_sold=False,
            image=image,
        )
        
        self.client = APIClient()

    def test_items_list(self):
        """
        Проверка GET-запроса к списку товаров
        """
        url = reverse('item:items')  # Примените правильное имя URL
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.item.name)
        self.assertContains(response, self.category.name)
        
    def test_item_search(self):
        """
        Проверка поиска товаров по запросу
        """
        url = reverse('item:items') + '?query=Test'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.item.name)
        
    def test_category_filter(self):
        """
        Проверка фильтрации товаров по категории
        """
        url = reverse('item:category', args=[self.category.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.item.name)
    
    def test_item_detail(self):
        """
        Проверка GET-запроса для подробной информации о товаре
        """
        url = reverse('item:detail', args=[self.item.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.item.name)
        self.assertContains(response, self.item.description)
    
    def test_item_create(self):
        """
        Проверка создания нового товара
        """
        self.client.login(username='testuser', password='testpassword')
        url = reverse('item:new')
        data = {
            'name': 'New Item',
            'description': 'New Description',
            'price': 150.0,
            'category': self.category.pk,
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Переадресация на страницу товара
        self.assertTrue(Item.objects.filter(name='New Item').exists())
    
    def test_item_edit(self):
        """
        Проверка редактирования товара
        """
        self.client.login(username='testuser', password='testpassword')
        url = reverse('item:edit', args=[self.item.pk])
        data = {
            'name': 'Updated Item',
            'description': 'Updated Description',
            'price': 200.0,
            'category': self.category.pk,
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Переадресация на страницу товара
        self.item.refresh_from_db()
        self.assertEqual(self.item.name, 'Updated Item')
    
    def test_item_delete(self):
        """
        Проверка удаления товара
        """
        self.client.login(username='testuser', password='testpassword')
        url = reverse('item:delete', args=[self.item.pk, self.user.pk])
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Переадресация на страницу
        self.assertFalse(Item.objects.filter(pk=self.item.pk).exists())
    
    def test_feedback(self):
        """
        Проверка отправки отзыва
        """
        self.client.login(username='testuser', password='testpassword')
        url = reverse('item:feedback')
        data = {'message': 'Great product!'}
        
        response = self.client.post(url, data)
        
        # Assert the response is JSON
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['message'], 'Спасибо за отзыв!')

    
    def test_search_statistics(self):
        """
        Проверка статистики поиска
        """
        url = reverse('item:items') + '?query=Test'
        response = self.client.get(url)
        
        # Проверяем, что статистика поиска была увеличена
        stat = SearchStatistics.objects.get(query='Test')
        self.assertEqual(stat.search_count, 1)  # Предположим, что был один запрос


    def test_pagination(self):
        """
        Проверка пагинации
        """
        # Создадим больше товаров для проверки пагинации
        for i in range(10):
            image = SimpleUploadedFile(
                name=f'image{i}.jpg',
                content=BytesIO(b"dummy image content").getvalue(),
                content_type='image/jpeg'
            )
            Item.objects.create(
                name=f'Item {i}',
                description=f'Description {i}',
                price=50.0,
                category=self.category,
                created_by=self.user,
                image=image  # Include the image field
            )
        
        url = reverse('item:items')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'page')
        self.assertContains(response, 'Item 0')
        response = self.client.get(url, {'page': 2})
        self.assertContains(response, 'Item 9')
