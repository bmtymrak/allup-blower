from django.test import TestCase

from customers.models import Customer


class TestCustomerModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer1 = Customer.objects.create(
            first_name="first1",
            last_name="last1",
            address="123 Test St",
            zip_code="12345",
            blowing_direction="N",
            notes="Test note",
            order=1,
        )

    def test_customer_str(self):
        self.assertEqual(str(self.customer1), "123 Test St")
