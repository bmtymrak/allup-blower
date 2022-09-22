from django.views.generic import CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from customers.models import Customer
from customers.forms import CustomerForm


class CustomerListView(LoginRequiredMixin, CreateView):
    model = Customer
    template_name = "customers/list.html"
    form_class = CustomerForm

    def get_context_data(self, **kwargs):
        cusomters = Customer.objects.all()
        kwargs["customers"] = cusomters
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        url = reverse_lazy("customer_list")
        return url


class CustomerDetailView(LoginRequiredMixin, DetailView):
    model = Customer
    context_object_name = "customer"
    template_name = "customers/detail.html"
