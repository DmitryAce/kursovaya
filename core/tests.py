from django.urls import reverse
from rest_framework.test import APITestCase
from item.models import Category, Item
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django import forms


class TestCoreViews(APITestCase):

    # 1. Тесты для представления 'index'
    def test_index_view_with_items(self):
        # Создаем категорию и товары
        category = Category.objects.create(name="Test Category")
        user = User.objects.create_user(username="testuser", password="testpassword")
        image = SimpleUploadedFile(name='test_image.jpg', content=b'file_content', content_type='image/jpeg')

        item1 = Item.objects.create(name="Test Item 1", is_sold=False, category=category, price=100, created_by=user, image=image)
        item2 = Item.objects.create(name="Test Item 2", is_sold=False, category=category, price=200, created_by=user, image=image)

        url = reverse('core:index')
        response = self.client.get(url)

        assert response.status_code == 200
        assert 'items' in response.context
        assert len(response.context['items']) == 2
        assert 'categories' in response.context

    def test_index_view_no_items(self):
        # Проверка, если нет товаров
        category = Category.objects.create(name="Test Category")
        url = reverse('core:index')
        response = self.client.get(url)

        assert response.status_code == 200
        assert len(response.context['items']) == 0
        assert 'categories' in response.context

    def test_index_view_sorting(self):
        # Проверка сортировки товаров
        category = Category.objects.create(name="Test Category")
        user = User.objects.create_user(username="testuser", password="testpassword")
        image = SimpleUploadedFile(name='test_image.jpg', content=b'file_content', content_type='image/jpeg')

        item1 = Item.objects.create(name="Test Item 1", is_sold=False, category=category, price=100, created_by=user, image=image)
        item2 = Item.objects.create(name="Test Item 2", is_sold=False, category=category, price=200, created_by=user, image=image)

        url = reverse('core:index')
        response = self.client.get(url)

        # Проверим, что товары сортируются по убыванию даты
        assert response.status_code == 200
        assert response.context['items'][0] == item2  # самый новый товар
        assert response.context['items'][1] == item1  # старый товар

    # 2. Тесты для представления 'contact'
    def test_contact_view(self):
        url = reverse('core:contact')
        response = self.client.get(url)

        assert response.status_code == 200

    # 3. Тесты для представления 'signup'
    def test_signup_view_get(self):
        url = reverse('core:signup')
        response = self.client.get(url)

        assert response.status_code == 200
        assert 'form' in response.context

    def test_signup_view_post_valid_data(self):
        # Тест для POST с валидными данными
        url = reverse('core:signup')
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password1": "testpassword123",
            "password2": "testpassword123",
        }
        response = self.client.post(url, data)

        assert response.status_code == 302  # редирект на страницу входа
        assert response.url == '/login/'

        # Проверка, что пользователь был создан
        user = User.objects.get(username="testuser")
        assert user.email == "testuser@example.com"

    def test_signup_view_post_invalid_data(self):
        # Тест для POST с невалидными данными
        url = reverse('core:signup')
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password1": "testpassword123",
            "password2": "wrongpassword123",
        }
        response = self.client.post(url, data)

        assert response.status_code == 200  # Должен остаться на странице с ошибками
        assert 'form' in response.context
        assert 'password2' in response.context['form'].errors  # Ошибка в поле "Подтверждение пароля"

    def test_signup_view_post_empty_data(self):
        # Тест для POST с пустыми данными
        url = reverse('core:signup')
        data = {}
        response = self.client.post(url, data)

        assert response.status_code == 200
        assert 'form' in response.context
        assert 'username' in response.context['form'].errors
        assert 'password1' in response.context['form'].errors

    def test_signup_view_post_existing_user(self):
        # Проверка на существующего пользователя
        User.objects.create_user(username="testuser", email="testuser@example.com", password="testpassword123")

        url = reverse('core:signup')
        data = {
            "username": "testuser",  # Уже существующий пользователь
            "email": "testuser@example.com",
            "password1": "newpassword123",
            "password2": "newpassword123",
        }

        response = self.client.post(url, data)

        assert response.status_code == 200
        assert 'username' in response.context['form'].errors  # Ошибка на уже существующее имя пользователя

    # 4. Тесты на безопасность (CSRF)
    def test_signup_view_csrf_protection(self):
        url = reverse('core:signup')
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password1": "testpassword123",
            "password2": "testpassword123",
        }
        # Передаем пустой CSRF токен, что вызовет редирект на страницу входа
        response = self.client.post(url, data, HTTP_X_CSRFTOKEN="")

        # Проверяем, что был редирект на страницу логина
        assert response.status_code == 302  # Ожидаем редирект, а не 403
        assert response.url == '/login/'  # Проверка на правильность редиректа

