from django.forms import ModelForm, inlineformset_factory

from customers.models import Customer, Hazard


class CustomerForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs["placeholder"] = "First Name"
        self.fields["last_name"].widget.attrs["placeholder"] = "Last Name"
        self.fields["address"].widget.attrs["placeholder"] = "Address"
        self.fields["zip_code"].widget.attrs["placeholder"] = "Zipcode"
        self.fields["blowing_direction"].widget.attrs["placeholder"] = "Direction"
        self.fields["notes"].widget.attrs["placeholder"] = "Notes"

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


HazardFormset = inlineformset_factory(
    Customer, Hazard, fields=["content"], can_delete=False
)
