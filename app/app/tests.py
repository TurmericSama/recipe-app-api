from django.test import SimpleTestCase

from app import calc

from rest_framework.test import APIClient  # noqa


class CalcTest(SimpleTestCase):
    """Test the calc module"""

    def test_add_number(self):
        """Adding numbers together"""
        sum = calc.add(5, 6)
        self.assertEqual(sum, 11)

    def test_subtract_number(self):
        """Subtracting numbers"""
        result = calc.subtract(10, 5)
        self.assertEqual(result, 5)
