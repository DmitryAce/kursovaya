from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from item.models import Item, Category
from django.urls import reverse
from rest_framework.test import APITestCase


class DashboardViewsTests(TestCase):
    def setUp(self):
        # Создаем пользователя
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Создаем категории и элементы
        self.category1 = Category.objects.create(name='Category 1')
        self.category2 = Category.objects.create(name='Category 2')
        
        self.item1 = Item.objects.create(
            name='Item 1', description='Description 1', price=10.0,
            image='http://example.com/image1.jpg', is_sold=False,
            created_by=self.user, category=self.category1
        )
        self.item2 = Item.objects.create(
            name='Item 2', description='Description 2', price=20.0,
            image='http://example.com/image2.jpg', is_sold=False,
            created_by=self.user, category=self.category2
        )
    
    def test_index_view(self):
        """Тест для проверки index представления"""
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/index.html')
        self.assertContains(response, 'Category 1')
        self.assertContains(response, 'Item 1')
    
    def test_index_view_pagination(self):
        """Тест для проверки пагинации в index"""
        for i in range(10):
            Item.objects.create(
                name=f'Item {i+3}', description='Description', price=5.0,
                image=f'http://example.com/image{i+3}.jpg', is_sold=False,
                created_by=self.user, category=self.category1
            )
        
        response = self.client.get(reverse('dashboard:index') + '?page=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['items']), 2)  # Проверяем пагинацию (PAGINATION = 2)
    
    def test_category_view(self):
        """Тест для проверки category представления"""
        response = self.client.get(reverse('dashboard:category', args=[self.category1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'item/category.html')
        self.assertContains(response, 'Мои товары в категории category 1')
        self.assertContains(response, 'Item 1')
    

    def test_category_view_invalid_category(self):
        response = self.client.get(reverse('dashboard:category', args=[999]))
        self.assertEqual(response.status_code, 404)
        self.assertIn("No Category matches the given query", response.data['detail'])

    def test_category_view_pagination(self):
        """Тест для проверки пагинации в category"""
        for i in range(10):
            Item.objects.create(
                name=f'Item {i+3}', description='Description', price=5.0,
                image=f'http://example.com/image{i+3}.jpg', is_sold=False,
                created_by=self.user, category=self.category1
            )
        
        response = self.client.get(reverse('dashboard:category', args=[self.category1.id]) + '?page=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['items']), 2)  # Проверяем пагинацию (PAGINATION = 2)
