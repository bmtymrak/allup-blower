from django.urls import path
from customers.views import (
    CustomerListView,
    CustomerDetailView,
    CustomerEditView,
    UploadCustomersView,
    RouteListView,
    RouteDetailView,
    SessionsListView,
    create_session,
    edit_route,
    delete_route,
    export_customers,
    customer_delete,
    membership_delete,
    session,
    complete_session,
)

urlpatterns = [
    path("<int:pk>/delete", customer_delete, name="customer_delete"),
    path("<int:pk>/edit", CustomerEditView.as_view(), name="customer_edit"),
    path("<int:pk>/", CustomerDetailView.as_view(), name="customer_detail"),
    path("upload/", UploadCustomersView.as_view(), name="upload_customers"),
    path(
        "routes/<int:route_id>/session/<int:session_id>/membership/<int:membership_id>",
        session,
        name="session",
    ),
    path(
        "routes/<int:route_id>/session/create/", create_session, name="session_create"
    ),
    path("routes/create/", edit_route, name="route_create"),
    path(
        "routes/<int:route_id>/details",
        RouteDetailView.as_view(),
        name="route_details",
    ),
    path(
        "routes/<int:route_id>/edit",
        edit_route,
        name="route_edit",
    ),
    path("routes/<int:route_id>/delete", delete_route, name="route_delete"),
    path("routes/", RouteListView.as_view(), name="routes"),
    path("routes/sessions/", SessionsListView.as_view(), name="sessions_list"),
    path(
        "routes/sessions/<int:route_id>/<int:session_id>/complete",
        complete_session,
        name="complete_session",
    ),
    path("memberships/<int:pk>/delete", membership_delete, name="membership_delete"),
    path("export/", export_customers, name="export_customers"),
    path("customers/", CustomerListView.as_view(), name="customers"),
    path("", RouteListView.as_view(), name="routes"),
]
