from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import BlogPost, Category

class BlogTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Cardiology',
            description='Heart related articles'
        )
        self.post = BlogPost.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user
        )
        self.post.categories.add(self.category)

    def test_post_list_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        self.assertTemplateUsed(response, 'blog/home.html')

    def test_post_detail_view(self):
        response = self.client.get(self.post.get_absolute_url())
        no_response = self.client.get('/post/2023/01/01/invalid-slug/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(no_response.status_code, 404)
        self.assertContains(response, 'Test Post')
        self.assertTemplateUsed(response, 'blog/post_detail.html')

    def test_post_create_view(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.post(reverse('post_create'), {
            'title': 'New Post',
            'content': 'New content',
            'categories': [self.category.id],
            'published': True
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(BlogPost.objects.last().title, 'New Post')

    def test_post_update_view(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.post(reverse('post_update', kwargs={
            'year': self.post.created_at.year,
            'month': self.post.created_at.month,
            'day': self.post.created_at.day,
            'slug': self.post.slug
        }), {
            'title': 'Updated Post',
            'content': 'Updated content',
            'categories': [self.category.id],
            'published': True
        })
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Post')

    def test_post_delete_view(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.post(reverse('post_delete', kwargs={
            'year': self.post.created_at.year,
            'month': self.post.created_at.month,
            'day': self.post.created_at.day,
            'slug': self.post.slug
        }))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(BlogPost.objects.count(), 0)

    def test_category_filter(self):
        response = self.client.get(f"{reverse('home')}?category={self.category.slug}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')

    def test_search_functionality(self):
        response = self.client.get(f"{reverse('home')}?q=Test")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')



