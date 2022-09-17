from django.views.generic import TemplateView
from allauth.account.forms import LoginForm


class HomePageView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        kwargs["form"] = LoginForm()
        return super().get_context_data(**kwargs)
