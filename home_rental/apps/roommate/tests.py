from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient


class RoommateAPITest(TestCase):

    def setUp(self):

        self.client = APIClient()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        logged_in = self.client.login(
            username='testuser',
            password='testpass123'
        )

        print("LOGIN SUCCESS:", logged_in)

    def test_roommate_score_endpoint(self):

        url = reverse('api_roommate_score')

        payload = {
            "profile_a": {
                "budget": 20000,
                "smoking": False,
            },
            "profile_b": {
                "budget": 22000,
                "smoking": False,
            }
        }

        response = self.client.post(
            url,
            data=payload,
            content_type='application/json'
        )

        print("STATUS:", response.status_code)

        try:
            print("JSON:", response.json())
        except Exception:
            print("RAW:", response.content)

        # Main goal: endpoint should not crash
        self.assertNotEqual(response.status_code, 500)