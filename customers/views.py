from django.views.generic import DetailView, TemplateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from customers.forms import CustomerForm, HazardFormset

from customers.models import Customer


class CustomerListView(LoginRequiredMixin, TemplateView):
    template_name = "customers/list.html"

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        customers = Customer.objects.all()
        kwargs["customers"] = customers

        new_customer = Customer()

        if self.request.method == "POST":
            customer_form = CustomerForm(self.request.POST)
            if customer_form.is_valid():
                new_customer = customer_form.save(commit=False)
                hazard_formset = HazardFormset(self.request.POST, instance=new_customer)
                if hazard_formset.is_valid():
                    print("formset valid")
                    new_customer.save()
                    hazard_formset.save()
                    return HttpResponseRedirect(self.get_success_url())
        else:
            customer_form = CustomerForm()
            hazard_formset = HazardFormset(instance=new_customer)

        kwargs["form"] = customer_form
        kwargs["formset"] = hazard_formset

        return super().get_context_data(**kwargs)

    def get_success_url(self):
        url = reverse_lazy("home")
        return url


class CustomerDetailView(LoginRequiredMixin, DetailView):
    model = Customer
    context_object_name = "customer"
    template_name = "customers/detail.html"


class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    success_url = reverse_lazy("home")
    context_object_name = "customer"
    template_name = "customers/delete.html"
