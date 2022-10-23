from django.forms import ModelForm, inlineformset_factory
from customers.models import Customer, Hazard


class CustomerForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs.update(
            placeholder="First Name", size="12"
        )
        self.fields["last_name"].widget.attrs.update(placeholder="Last Name", size="12")
        self.fields["address"].widget.attrs["placeholder"] = "Address"
        self.fields["zip_code"].widget.attrs.update(placeholder="Zipcode")
        self.fields["blowing_direction"].widget.attrs["placeholder"] = "Direction"
        self.fields["notes"].widget.attrs.update(
            placeholder="Notes", cols="20", rows="5"
        )

    class Meta:
        model = Customer
        fields = [
            "first_name",
            "last_name",
            "address",
            "zip_code",
            "blowing_direction",
            "notes",
            "photo",
        ]


HazardFormset = inlineformset_factory(
    Customer, Hazard, fields=["content"], can_delete=False
)
