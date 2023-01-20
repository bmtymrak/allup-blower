from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from customers.views import CustomerListView
from customers.models import Customer, Hazard

User = get_user_model()


class TestListView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username="testuser1", password="testpass123"
        )

        cls.customer1 = Customer.objects.create(
            first_name="first1",
            last_name="last1",
            address="123 Test St",
            zip_code="12345",
            blowing_direction="N",
            notes="Test note",
            order=1,
        )
        Hazard.objects.create(content="hazard 1", customer=cls.customer1)
        Hazard.objects.create(content="hazard 2", customer=cls.customer1)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get("/")

        self.assertRedirects(
            response,
            f"/accounts/login/?next=/",
        )

    def test_correct_templated_used(self):
        self.client.login(username="testuser1", password="testpass123")
        response = self.client.get("/")

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "customers/list.html")

    def test_view_url_accessible_by_name(self):
        self.client.login(username="testuser1", password="testpass123")
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)

    def test_customers_in_correct_order(self):

        customer2 = Customer.objects.create(
            first_name="first2",
            last_name="last2",
            address="234 Test St",
            zip_code="12345",
            blowing_direction="N",
            notes="Test note",
            order=2,
        )

        customer3 = Customer.objects.create(
            first_name="first3",
            last_name="last3",
            address="345 Test St",
            zip_code="12345",
            blowing_direction="N",
            notes="Test note",
        )

        customer4 = Customer.objects.create(
            first_name="first4",
            last_name="last4",
            address="456 Test St",
            zip_code="12345",
            blowing_direction="N",
            notes="Test note",
            order="5",
        )

        self.client.login(username="testuser1", password="testpass123")
        response = self.client.get("/")

        self.assertEqual(
            [self.customer1, customer2, customer4, customer3],
            response.context["customers"],
        )

    def test_customer_created_on_post(self):
        self.client.login(username="testuser1", password="testpass123")

        data = {
            "first_name": "post",
            "last_name": "test",
            "address": "2345 Test St",
            "zip_code": 54321,
            "blowing_direction": "S",
            "notes": "test post customer",
            "hazards-TOTAL_FORMS": 0,
            "hazards-INITIAL_FORMS": 3,
        }

        response = self.client.post("/", data)

        self.assertEqual(
            Customer.objects.get(first_name="post", last_name="test").first_name, "post"
        )
        self.assertRedirects(response, "/")


class TestCustomerDetailView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username="testuser1", password="testpass123"
        )

        cls.customer1 = Customer.objects.create(
            first_name="first1",
            last_name="last1",
            address="123 Test St",
            zip_code="12345",
            blowing_direction="N",
            notes="Test note",
            order=1,
        )

        cls.customer2 = Customer.objects.create(
            first_name="first2",
            last_name="last2",
            address="234 Test St",
            zip_code="12345",
            blowing_direction="N",
            notes="Test note 2",
            order=2,
        )

        cls.customer3 = Customer.objects.create(
            first_name="first3",
            last_name="last3",
            address="234 Test St",
            zip_code="12345",
            blowing_direction="N",
            notes="Test note 3",
            order=3,
        )

        Hazard.objects.create(content="hazard 1", customer=cls.customer1)
        Hazard.objects.create(content="hazard 2", customer=cls.customer1)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("customer_detail", args=[1]))

        self.assertRedirects(
            response,
            "/accounts/login/?next=/1/",
        )

    def test_correct_templated_used(self):
        self.client.login(username="testuser1", password="testpass123")

        response = self.client.get(reverse("customer_detail", args=[1]))

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "customers/detail.html")

    def test_view_url_accessible_by_name(self):
        self.client.login(username="testuser1", password="testpass123")
        response = self.client.get(reverse("customer_detail", args=[1]))

        self.assertEqual(response.status_code, 200)

    def test_correct_customer_in_view(self):
        self.client.login(username="testuser1", password="testpass123")
        response = self.client.get(reverse("customer_detail", args=[1]))

        self.assertEqual(response.context["customer"], self.customer1)

    def test_correct_next_and_previous_customers(self):
        self.client.login(username="testuser1", password="testpass123")
        response = self.client.get(reverse("customer_detail", args=[1]))

        self.assertEqual(response.context["next_customer"], self.customer2)
        self.assertEqual(response.context["prev_customer"], None)

        response = self.client.get(reverse("customer_detail", args=[2]))

        self.assertEqual(response.context["next_customer"], self.customer3)
        self.assertEqual(response.context["prev_customer"], self.customer1)

        response = self.client.get(reverse("customer_detail", args=[3]))

        self.assertEqual(response.context["next_customer"], None)
        self.assertEqual(response.context["prev_customer"], self.customer2)


class TestCustomerEditView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username="testuser1", password="testpass123"
        )

        cls.customer1 = Customer.objects.create(
            first_name="first1",
            last_name="last1",
            address="123 Test St",
            zip_code="12345",
            blowing_direction="N",
            notes="Test note",
            order=1,
        )

        cls.customer2 = Customer.objects.create(
            first_name="first2",
            last_name="last2",
            address="234 Test St",
            zip_code="12345",
            blowing_direction="N",
            notes="Test note 2",
            order=2,
        )

        cls.customer3 = Customer.objects.create(
            first_name="first3",
            last_name="last3",
            address="234 Test St",
            zip_code="12345",
            blowing_direction="N",
            notes="Test note 3",
            order=3,
        )

        Hazard.objects.create(content="hazard 1", customer=cls.customer1)
        Hazard.objects.create(content="hazard 2", customer=cls.customer1)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("customer_edit", args=[1]))

        self.assertRedirects(
            response,
            "/accounts/login/?next=/1/edit",
        )

    def test_correct_templated_used(self):
        self.client.login(username="testuser1", password="testpass123")

        response = self.client.get(reverse("customer_edit", args=[1]))

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "customers/edit.html")

    def test_view_url_accessible_by_name(self):
        self.client.login(username="testuser1", password="testpass123")
        response = self.client.get(reverse("customer_edit", args=[1]))

        self.assertEqual(response.status_code, 200)

    def test_correct_customer_in_form(self):
        self.client.login(username="testuser1", password="testpass123")
        response = self.client.get(reverse("customer_edit", args=[1]))

        self.assertEqual(
            response.context["form"].initial["first_name"], self.customer1.first_name
        )

    def test_customer_correctly_edited_on_post(self):
        self.client.login(username="testuser1", password="testpass123")
        response = self.client.get(reverse("customer_edit", args=[1]))
        data = response.context["form"].initial
        data["address"] = "new address"
        data["photo"] = ""
        formset_data = {
            "hazards-TOTAL_FORMS": 2,
            "hazards-INITIAL_FORMS": 4,
            "hazards-0-customer": 1,
            "hazards-0-id": 1,
            "hazards-0-content": "hazard 1",
            "hazards-1-customer": 1,
            "hazards-1-id": 2,
            "hazards-1-content": "hazard 2",
        }
        data.update(formset_data)

        response = self.client.post(reverse("customer_edit", args=[1]), data)

        self.assertEqual(
            Customer.objects.get(first_name="first1", last_name="last1").address,
            "new address",
        )
        self.assertRedirects(response, "/")


class TestCustomerDeleteView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username="testuser1", password="testpass123"
        )

        cls.customer1 = Customer.objects.create(
            first_name="first1",
            last_name="last1",
            address="123 Test St",
            zip_code="12345",
            blowing_direction="N",
            notes="Test note",
            order=1,
        )

        cls.customer2 = Customer.objects.create(
            first_name="first2",
            last_name="last2",
            address="234 Test St",
            zip_code="12345",
            blowing_direction="N",
            notes="Test note 2",
            order=2,
        )

        cls.customer3 = Customer.objects.create(
            first_name="first3",
            last_name="last3",
            address="234 Test St",
            zip_code="12345",
            blowing_direction="N",
            notes="Test note 3",
            order=3,
        )

        Hazard.objects.create(content="hazard 1", customer=cls.customer1)
        Hazard.objects.create(content="hazard 2", customer=cls.customer1)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("customer_delete", args=[1]))

        self.assertRedirects(
            response,
            "/accounts/login/?next=/1/delete",
        )

    def test_correct_templated_used(self):
        self.client.login(username="testuser1", password="testpass123")

        response = self.client.get(reverse("customer_delete", args=[1]))

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "customers/delete.html")

    def test_view_url_accessible_by_name(self):
        self.client.login(username="testuser1", password="testpass123")
        response = self.client.get(reverse("customer_delete", args=[1]))

        self.assertEqual(response.status_code, 200)

    def test_correct_customer_in_form(self):
        self.client.login(username="testuser1", password="testpass123")
        response = self.client.get(reverse("customer_delete", args=[1]))

        self.assertEqual(response.context["customer"], self.customer1)

    def test_customer_deleted_on_post(self):
        self.client.login(username="testuser1", password="testpass123")
        self.assertEqual(Customer.objects.all().count(), 3)

        response = self.client.post(reverse("customer_delete", args=[1]))

        self.assertEqual(Customer.objects.all().count(), 2)
        self.assertFalse(self.customer1 in Customer.objects.all())
        self.assertEqual(Hazard.objects.all().count(), 0)
        self.assertRedirects(response, "/")


class TestUploadCustomersView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username="testuser1", password="testpass123"
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("upload_customers"))

        self.assertRedirects(
            response,
            "/accounts/login/?next=/upload/",
        )

    def test_correct_templated_used(self):
        self.client.login(username="testuser1", password="testpass123")
        response = self.client.get(reverse("upload_customers"))

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "customers/upload.html")
