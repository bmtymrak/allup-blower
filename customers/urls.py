from django.urls import path
from customers.views import (
    CustomerListView,
    CustomerDetailView,
    CustomerDeleteView,
    CustomerEditView,
    UploadCustomersView,
)

urlpatterns = [
    path("<int:pk>/delete", CustomerDeleteView.as_view(), name="customer_delete"),
    path("<int:pk>/edit", CustomerEditView.as_view(), name="customer_edit"),
    path("<int:pk>/", CustomerDetailView.as_view(), name="customer_detail"),
    path("upload/", UploadCustomersView.as_view(), name="upload_customers"),
    path("", CustomerListView.as_view(), name="home"),
]
