from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Item, Category

class ItemViewsTestCase(TestCase):
    def setUp(self):
        # Создаём пользователя для тестов
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name='Category 1')
        self.item = Item.objects.create(
            name='Test Item',
            description='This is a test item',
            price=10.99,
            category=self.category,
            created_by=self.user,
        )
        # URL, который будет тестироваться
        self.url = reverse('item:items')

    def test_items_view_get(self):
        """Тестируем представление, которое отображает список товаров"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Item')

    def test_item_detail_view(self):
        """Тестируем представление страницы товара"""
        url = reverse('item:detail', kwargs={'pk': self.item.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.item.name)

    def test_create_item(self):
        """Тестируем создание нового товара"""
        self.client.login(username='testuser', password='password')
        url = reverse('item:new')
        data = {
            'name': 'New Item',
            'description': 'A new test item',
            'price': 20.99,
            'category': self.category.pk,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # редирект на страницу товара
        self.assertEqual(Item.objects.count(), 2)  # Товар должен быть создан

    def test_edit_item(self):
        """Тестируем редактирование товара"""
        self.client.login(username='testuser', password='password')
        url = reverse('item:edit', kwargs={'pk': self.item.pk})
        data = {
            'name': 'Updated Item',
            'description': 'Updated description',
            'price': 15.99,
            'category': self.category.pk,
        }
        response = self.client.post(url, data)
        self.item.refresh_from_db()  # обновить объект из базы данных
        self.assertEqual(response.status_code, 302)  # редирект после сохранения
        self.assertEqual(self.item.name, 'Updated Item')

    def test_delete_item(self):
        """Тестируем удаление товара"""
        self.client.login(username='testuser', password='password')
        url = reverse('item:delete', kwargs={'creator': self.user.pk, 'pk': self.item.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # редирект после удаления
        self.assertEqual(Item.objects.count(), 0)  # Товар должен быть удалён
