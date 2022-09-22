from django.forms import ModelForm

from customers.models import Customer


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = [
            "first_name",
            "last_name",
            "address",
            "zip_code",
            "blowing_direction",
            "notes",
        ]
