from typing import Any
from django.views.generic import (
    DetailView,
    ListView,
    TemplateView,
    DeleteView,
    FormView,
    CreateView,
    UpdateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.forms import modelform_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from django_htmx.http import HttpResponseClientRedirect

from customers.forms import CustomerForm, HazardFormset, CsvUpdateForm
from customers.models import Customer, Membership, Route, RouteType, Session, SessionVisit

from io import StringIO
import csv
import datetime


def check_admin(user):
    return user.is_superuser

class IsSuperUserMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

class CustomerListView(LoginRequiredMixin, IsSuperUserMixin, TemplateView):
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
        customers_with_membership = Customer.objects.exclude(order=None).prefetch_related('memberships__route').order_by("memberships__route")
        customers_without_membership = Customer.objects.filter(order=None).prefetch_related('memberships__route').order_by(
            "address"
        )
        kwargs["customers"] = list(customers_with_membership) + list(customers_without_membership)

        return super().get_context_data(**kwargs)

    def get_success_url(self):
        url = reverse_lazy("customers")
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
        url = reverse_lazy("customers")
        return url


@login_required
@user_passes_test(check_admin)
def customer_delete(request, pk):

    customer = Customer.objects.get(id=pk)

    if request.method == "DELETE":

        Customer.objects.filter(id=pk).delete()

        return HttpResponseClientRedirect(reverse("customers"))

    return render(
        request, "customers/partials/customer_delete.html", {"customer": customer}
    )


@login_required
@user_passes_test(check_admin)
def membership_delete(request, pk):

    membership = Membership.objects.get(id=pk)

    if request.method == "DELETE":

        route = membership.route

        membership.delete()

        remaining = Membership.objects.filter(route_id=route.id).order_by("order")

        for index, membership in enumerate(remaining, start=1):
            membership.order = index
            membership.save()

        return HttpResponseClientRedirect(
            reverse("route_details", kwargs={"route_id": membership.route.id})
        )

    return render(
        request, "customers/partials/membership_delete.html", {"membership": membership}
    )


class RouteCreateView(LoginRequiredMixin, IsSuperUserMixin, CreateView):
    model = Route
    fields = ["name", "operator", "type", "details"]
    template_name = "customers/route_create.html"
    success_url = reverse_lazy("routes")

class RouteListView(LoginRequiredMixin, ListView):
    model = Route
    context_object_name = "routes"
    template_name = "customers/route_list.html"

    def get_context_data(self, **kwargs):

        user_routes = self.model.objects.filter(operator=self.request.user)
        routes = self.model.objects.exclude(operator=self.request.user)

        kwargs.update({"user_routes": user_routes, "routes": routes})

        return super().get_context_data(**kwargs)


class RouteDetailView(LoginRequiredMixin, TemplateView):
    template_name = "customers/route_details.html"

    def get_context_data(self, **kwargs):
        route = Route.objects.get(id=kwargs["route_id"])
        customers = route.memberships
        customers_with_order = customers.exclude(order=None).order_by("order")
        customers_without_order = customers.filter(order=None).order_by(
            "customer__address"
        )
        kwargs["memberships"] = list(customers_with_order) + list(
            customers_without_order
        )

        kwargs["route"] = route

        return super().get_context_data(**kwargs)


class RouteEditView(LoginRequiredMixin, UpdateView):
    model = Route
    pk_url_kwarg = "route_id"
    template_name = "customers/route_edit.html"
    fields = ["name", "operator", "type", "details"]
    context_object_name = "route"
    success_url = reverse_lazy("routes")


@login_required
def edit_route(request, route_id=None):
    route = Route.objects.get(id=route_id) if route_id else None

    form_class = modelform_factory(
        Route, fields=["name", "operator", "type", "details"]
    )

    if request.method == "POST":
        form = form_class(request.POST, instance=route)

        if form.is_valid:
            form.save()

        return HttpResponseClientRedirect("/")

    form = form_class(instance=route)

    return render(
        request, "routes/partials/route_edit.html", {"form": form, "route": route}
    )

@login_required
def delete_route(request, route_id=None):
    route = Route.objects.get(id=route_id)

    if request.method == "DELETE":

        Route.objects.filter(id=route_id).delete()

        return HttpResponseClientRedirect(reverse("routes"))

    return render(
        request, "routes/partials/route_delete.html", {"route": route}
    )


class SessionsListView(LoginRequiredMixin, IsSuperUserMixin, ListView):
    permission_required = "sessions.session.view_session"
    model = Session
    context_object_name = "sessions"
    template_name = "routes/session_list.html"

    def get_context_data(self, **kwargs):
        context = {}
        sessions = (
            self.model.objects.all()
            .annotate(route_length=Count("route__memberships"))
            .order_by("-start_time")
        )

        context["sessions"] = sessions

        return context


@login_required
def create_session(request, route_id):

    route = Route.objects.get(id=route_id)
    if request.method == "POST":
        session = Session.objects.create(
            route=route, operator=request.user
        )
        membership = session.route.memberships.first()


        return redirect(
            "session",
            route_id=session.route.id,
            session_id=session.id,
            membership_id=membership.id,
        )
    else:
        return redirect("route_list")


@login_required
def complete_session(request, route_id, session_id):

    route = Route.objects.get(id=route_id)
    session = Session.objects.get(id=session_id)
    session.end_time = datetime.datetime.now()

    membership = Membership.objects.filter(route=route_id).last()
    visit = SessionVisit.objects.filter(route=route, session=session, customer=membership.customer).get()
    visit.end_time = timezone.now()
    visit.save()
    session.save()
    return HttpResponseClientRedirect(reverse("routes"))


@login_required
def session(request, route_id, session_id, membership_id):

    route = Route.objects.get(id=route_id)
    session = Session.objects.get(id=session_id)
    membership = Membership.objects.get(id=membership_id)
    session.current_membership = membership
    session.save()

    prev_membership = (
        Membership.objects.filter(route_id=route_id, order__lt=membership.order)
        .order_by("order")
        .last()
    )

    next_membership = (
        Membership.objects.filter(route_id=route_id, order__gt=membership.order)
        .order_by("order")
        .first()
    )

    new_visit = SessionVisit.objects.create(route=route, session=session, customer=membership.customer)
    
    if prev_membership:
        prev_visit = SessionVisit.objects.filter(route=route, session=session, customer=prev_membership.customer).get()
        prev_visit.end_time = timezone.now()
        prev_visit.save()

    route_length = route.memberships.count()

    if request.htmx:
        template = "routes/partials/session.html"
    else:
        template = "routes/session.html"

    return render(
        request,
        template,
        context={
            "membership": membership,
            "next_membership": next_membership,
            "prev_membership": prev_membership,
            "customer": membership.customer,
            "session": session,
            "route_id": route_id,
            "route_length": route_length,
        },
    )


@login_required
def get_customer(request):
    current_customer = request.GET["membership"]
    direction = request.GET["direction"]

    if direction == "next":
        order = current_customer.order + 1
    else:
        order = current_customer.order - 1

    next_customer = Membership.objects.filter(route=current_customer.route).get(
        order=order
    )

    return


class UploadCustomersView(LoginRequiredMixin, IsSuperUserMixin, FormView):
    form_class = CsvUpdateForm
    template_name = "customers/partials/upload_partial.html"
    success_url = reverse_lazy("customers")

    def form_valid(self, form):
        file = form.cleaned_data["csv_file"]
        file_data = file.read().decode("utf-8")
        csv_data = csv.reader(StringIO(file_data), delimiter=",")

        Customer.objects.update(order=None)
        customers = []
        memberships = []
        route_created_or_cleared = []
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

                if customer_data_dict["route"]:

                    route, created = Route.objects.get_or_create(
                        name__iexact=customer_data_dict["route"], defaults={'name': customer_data_dict["route"]}
                    )

                    if created and route.name not in route_created_or_cleared :
                        route_created_or_cleared.append(route.name)

                    if route.name not in route_created_or_cleared:
                        Membership.objects.filter(route=route).delete()
                        route_created_or_cleared.append(route.name)

                    membership, created = Membership.objects.get_or_create(
                        route=route, customer=customer
                    )

                    if membership:
                        membership.order = customer_data_dict["order"]

                    memberships.append(membership)

                customers.append(customer)

        Customer.objects.bulk_update(
            customers,
            ["first_name", "last_name", "blowing_direction", "notes", "order"],
        )

        Membership.objects.bulk_update(memberships, ["order"])

        return HttpResponseRedirect(self.get_success_url())


@login_required
@user_passes_test(check_admin)
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
            "route",
            "order",
        ]
    )
    for customer in customers:
        
        if customer.memberships.exists():
            route = customer.memberships.first().route
            order = customer.memberships.first().order
        else:
            route=""
            order=""

        writer.writerow(
            [
                customer.first_name,
                customer.last_name,
                "",
                customer.address,
                customer.zip_code,
                customer.blowing_direction,
                customer.notes,
                route,
                order,
            ]
        )

    return response
