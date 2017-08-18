from django.test import TestCase, Client
from django.shortcuts import reverse

class ViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super(ViewTests, cls).setUpClass()
        cls.client = Client()

    def test_get_home_view(self):
        response = self.client.get(reverse("machine-learning:home"))

        self.assertEqual(response.status_code, 200)


    def test_get_regression_view(self):
        response = self.client.get(reverse("machine-learning:regression"))

        self.assertEqual(response.status_code, 200)


    def test_get_classification_view(self):
        response = self.client.get(reverse("machine-learning:classification"))

        self.assertEqual(response.status_code, 200)


    def test_get_clustering_view(self):
        response = self.client.get(reverse("machine-learning:clustering"))

        self.assertEqual(response.status_code, 200)

