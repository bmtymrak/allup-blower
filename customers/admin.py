from django.contrib import admin
from customers.models import Customer, Hazard, Route, RouteType, Membership, Session, SessionVisit


admin.site.register(Customer)

admin.site.register(Hazard)
admin.site.register(Route)
admin.site.register(RouteType)
admin.site.register(Membership)
admin.site.register(Session)
admin.site.register(SessionVisit)