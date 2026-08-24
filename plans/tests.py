from django.contrib.auth import get_user_model
from django.test import TestCase


class PlansHomeViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='plan-user',
            password='test-password',
        )

    def test_plans_home_requires_authentication(self):
        response = self.client.get('/plans/')

        self.assertRedirects(response, '/accounts/login/?next=/plans/')

    def test_authenticated_user_can_view_plans_home(self):
        self.client.force_login(self.user)

        response = self.client.get('/plans/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Plans</h1>', html=False)

    def test_authenticated_user_sees_plans_nav_item(self):
        self.client.force_login(self.user)

        response = self.client.get('/plans/')

        self.assertContains(response, 'href="/plans/"')
        self.assertContains(response, 'class="nav-link active"')
