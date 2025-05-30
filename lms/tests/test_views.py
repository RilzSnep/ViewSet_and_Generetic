from django.test import TestCase

class SimpleTest(TestCase):
    def test_home(self):
        self.assertEqual(1 + 1, 2)
