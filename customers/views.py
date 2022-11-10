from django.views.generic import DetailView, TemplateView, DeleteView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from customers.forms import CustomerForm, HazardFormset, CsvUpdateForm
from customers.models import Customer

from io import StringIO
import csv


class CustomerListView(LoginRequiredMixin, TemplateView):
    template_name = "customers/list.html"

    def post(self, request, **kwargs):
        customer_form = CustomerForm(self.request.POST, self.request.FILES)
        if customer_form.is_valid():
            new_customer = customer_form.save(commit=False)
            hazard_formset = HazardFormset(self.request.POST, instance=new_customer)
            if hazard_formset.is_valid():
                new_customer.save()
                hazard_formset.save()
                return HttpResponseRedirect(self.get_success_url())

        kwargs["form"] = customer_form
        kwargs["formset"] = hazard_formset

        return self.render_to_response(kwargs)

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

    def get_context_data(self, **kwargs):
        try:
            next_customer = Customer.objects.get(order=self.object.order + 1)
        except:
            next_customer = 0

        try:
            prev_customer = Customer.objects.get(order=self.object.order - 1)
        except:
            prev_customer = 0

        kwargs["next_customer"] = next_customer
        kwargs["prev_customer"] = prev_customer

        return super().get_context_data(**kwargs)


# class CustomerEditView(LoginRequiredMixin, UpdateView):
#     model = Customer
#     context_object_name = "customer"
#     success_url = reverse_lazy("home")
#     template_name = "customers/edit.html"


class CustomerEditView(LoginRequiredMixin, TemplateView):
    template_name = "customers/edit.html"

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        customer = Customer.objects.filter(pk=pk).get()
        print(customer)
        customer_form = CustomerForm(
            data=self.request.POST, files=self.request.FILES, instance=customer
        )
        if customer_form.is_valid():
            new_customer = customer_form.save(commit=False)
            hazard_formset = HazardFormset(self.request.POST, instance=customer)
            if hazard_formset.is_valid():
                print("formset valid")
                new_customer.save()
                hazard_formset.save()
                return HttpResponseRedirect(self.get_success_url())

        kwargs["form"] = customer_form
        kwargs["formset"] = hazard_formset

        return self.render_to_response(kwargs)

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get("pk")
        customer = Customer.objects.filter(pk=pk).get()
        # kwargs["customers"] = customer

        # if self.request.method == "POST":
        #     customer_form = CustomerForm(data=self.request.POST, instance=customer)
        #     if customer_form.is_valid():
        #         new_customer = customer_form.save(commit=False)
        #         hazard_formset = HazardFormset(self.request.POST, instance=customer)
        #         if hazard_formset.is_valid():
        #             print("formset valid")
        #             new_customer.save()
        #             hazard_formset.save()
        #             return HttpResponseRedirect(self.get_success_url())
        # else:
        customer_form = CustomerForm(instance=customer)
        hazard_formset = HazardFormset(instance=customer)

        kwargs["form"] = customer_form
        kwargs["formset"] = hazard_formset

        return super().get_context_data(**kwargs)

    def get_success_url(self):
        url = reverse_lazy("home")
        return url


class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    success_url = reverse_lazy("home")
    context_object_name = "customer"
    template_name = "customers/delete.html"


class UploadCustomersView(LoginRequiredMixin, FormView):
    form_class = CsvUpdateForm
    template_name = "customers/upload.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        file = form.cleaned_data["csv_file"]
        file_data = file.read().decode("utf-8")
        csv_data = csv.reader(StringIO(file_data), delimiter=",")

        Customer.objects.update(order=None)

        for i, row in enumerate(csv_data):
            if i == 0:
                headers = row
            else:
                customer_data_dict = {}
                for i, header in enumerate(headers):
                    customer_data_dict[header] = row[i]

                customer = Customer.objects.get(
                    address=customer_data_dict["address"],
                    zip_code=customer_data_dict["zip_code"],
                )

                customer.order = customer_data_dict["order"]
                customer.save()

                print(customer)

        return HttpResponseRedirect(self.get_success_url())
