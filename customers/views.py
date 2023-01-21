from django.views.generic import DetailView, TemplateView, DeleteView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy

from customers.forms import CustomerForm, HazardFormset, CsvUpdateForm
from customers.models import Customer

from io import StringIO
import csv


class CustomerListView(LoginRequiredMixin, TemplateView):
    template_name = "customers/list.html"

    def get(self, request, *args, **kwargs):
        new_customer = Customer()
        customer_form = CustomerForm()
        hazard_formset = HazardFormset(instance=new_customer)

        context = self.get_context_data(**kwargs)
        context["form"] = customer_form
        context["formset"] = hazard_formset

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        customer_form = CustomerForm(self.request.POST, self.request.FILES)
        new_customer = Customer()
        if customer_form.is_valid():
            new_customer = customer_form.save(commit=False)
            hazard_formset = HazardFormset(self.request.POST, instance=new_customer)
            if hazard_formset.is_valid():
                new_customer.save()
                hazard_formset.save()
                return HttpResponseRedirect(self.get_success_url())

        hazard_formset = HazardFormset(self.request.POST, instance=new_customer)

        context = self.get_context_data(**kwargs)
        context["form"] = customer_form
        context["formset"] = hazard_formset

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        customers_with_order = Customer.objects.exclude(order=None).order_by("order")
        customers_without_order = Customer.objects.filter(order=None).order_by(
            "address"
        )
        kwargs["customers"] = list(customers_with_order) + list(customers_without_order)

        return super().get_context_data(**kwargs)

    def get_success_url(self):
        url = reverse_lazy("home")
        return url


class CustomerDetailView(LoginRequiredMixin, DetailView):
    model = Customer
    context_object_name = "customer"
    template_name = "customers/detail.html"

    def get_context_data(self, **kwargs):

        if self.object.order:
            prev_customer = (
                Customer.objects.filter(order__lt=self.object.order)
                .order_by("order")
                .last()
            )

            next_customer = (
                Customer.objects.filter(order__gt=self.object.order)
                .order_by("order")
                .first()
            )
        else:
            prev_customer = None
            next_customer = None

        kwargs["next_customer"] = next_customer
        kwargs["prev_customer"] = prev_customer

        return super().get_context_data(**kwargs)


class CustomerEditView(LoginRequiredMixin, TemplateView):
    template_name = "customers/edit.html"

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        customer = Customer.objects.filter(pk=pk).get()
        customer_form = CustomerForm(
            data=self.request.POST, files=self.request.FILES, instance=customer
        )
        if customer_form.is_valid():
            new_customer = customer_form.save(commit=False)
            hazard_formset = HazardFormset(self.request.POST, instance=customer)
            if hazard_formset.is_valid():
                new_customer.save()
                hazards_saved = hazard_formset.save()
                for hazard in hazards_saved:
                    if hazard.content == "":
                        hazard.delete()
                return HttpResponseRedirect(self.get_success_url())

        kwargs["form"] = customer_form
        kwargs["formset"] = hazard_formset

        return self.render_to_response(kwargs)

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get("pk")
        customer = Customer.objects.filter(pk=pk).get()
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
        customers = []
        for i, row in enumerate(csv_data):
            if i == 0:
                headers = row
            else:
                customer_data_dict = {}
                for i, header in enumerate(headers):
                    customer_data_dict[header] = row[i]

                customer, created = Customer.objects.get_or_create(
                    address=customer_data_dict["address"],
                    zip_code=customer_data_dict["zip_code"],
                )

                if created:
                    if customer_data_dict["first_name"]:
                        customer.first_name = customer_data_dict["first_name"]
                    if customer_data_dict["last_name"]:
                        customer.last_name = customer_data_dict["last_name"]
                    if customer_data_dict["blowing_direction"]:
                        customer.blowing_direction = customer_data_dict[
                            "blowing_direction"
                        ]
                    if customer_data_dict["notes"]:
                        customer.notes = customer_data_dict["notes"]

                if customer_data_dict["order"]:
                    customer.order = customer_data_dict["order"]
                else:
                    customer.order = None

                customers.append(customer)

        Customer.objects.bulk_update(
            customers,
            ["first_name", "last_name", "blowing_direction", "notes", "order"],
        )
        return HttpResponseRedirect(self.get_success_url())


@login_required
def export_customers(request):

    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="customer_export'},
    )

    writer = csv.writer(response)

    customers = Customer.objects.all().order_by("order")

    writer.writerow(
        [
            "first_name",
            "last_name",
            "driver",
            "address",
            "zip_code",
            "blowing_direction",
            "notes",
            "order",
        ]
    )
    for customer in customers:
        writer.writerow(
            [
                customer.first_name,
                customer.last_name,
                "",
                customer.address,
                customer.zip_code,
                customer.blowing_direction,
                customer.notes,
                customer.order,
            ]
        )

    return response
