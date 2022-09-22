from django.urls import path
from customers.views import CustomerListView, CustomerDetailView

urlpatterns = [
    path("<int:pk>/", CustomerDetailView.as_view(), name="customer_detail"),
    path("", CustomerListView.as_view(), name="customer_list"),
]
