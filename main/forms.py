from django import forms
from django.shortcuts import get_object_or_404, redirect
from .models import Product, User, Purchase, Refund
from django.utils.translation import gettext_lazy as _


class RefundForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.purchase_id = kwargs.pop('purchase_id')
        self.request = kwargs.pop('request')
        super(RefundForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Refund
        fields = []

    def clean_purchase_id(self):
        try:
            purchase = Purchase.objects.get(pk=self.purchase_id)
        except Purchase.DoesNotExist:
            raise forms.ValidationError('Purchase with the given ID does not exist.')

        return self.purchase_id


def clean(self):
    cleaned_data = super().clean()
    if Refund.objects.filter(refund_purchase_id=self.purchase_id).exists():
        raise forms.ValidationError('A refund already exists for this purchase.')


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock']


class UserCreationForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
                                widget=forms.PasswordInput,
                                help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = ("username",)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
