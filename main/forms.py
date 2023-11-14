from django.utils import timezone
from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Product, User, Purchase, Refund
from django.utils.translation import gettext_lazy as _


class RefundForm(forms.ModelForm):
    class Meta:
        model = Refund
        fields = []

    def __init__(self, *args, **kwargs):
        self.purchase_id = kwargs.pop('purchase_id', None)
        self.request = kwargs.pop('request', None)
        super(RefundForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        try:
            purchase = Purchase.objects.get(pk=self.purchase_id)
            if hasattr(purchase, "refund"):
                messages.error(self.request, "Refund request exists")
                raise ValidationError('Refund request exists')
            time_since_purchase = timezone.now() - purchase.purchase_time
            if time_since_purchase.total_seconds() > 180:
                messages.error(self.request, 'The return period has expired.')
                raise ValidationError('The return period has expired.')
            cleaned_data['purchase'] = purchase
        except Purchase.DoesNotExist:
            raise forms.ValidationError('Purchase with the given ID does not exist.')
        return cleaned_data


class PurchaseForm(forms.ModelForm):
    quantity = forms.IntegerField(label='Quantity', initial=1, min_value=1, required=True, widget=forms.NumberInput)

    class Meta:
        model = Purchase
        fields = ['quantity']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.product = kwargs.pop('product', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        try:
            product = self.product

            if product.stock < cleaned_data['quantity']:
                self.add_error('quantity', 'Not enough products in stock.')
                messages.error(self.request, 'Not enough products in stock.')

            total_price = product.price * cleaned_data['quantity']

            if total_price > self.request.user.wallet:
                self.add_error('quantity', 'Not enough money.')
                messages.error(self.request, "Not enough money.")

        except Product.DoesNotExist:
            self.add_error('quantity', 'Incorrect product id.')
            messages.error(self.request, 'Incorrect product id.')

        return cleaned_data

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']

        if Refund.objects.filter(refund_purchase_id=self.product.pk).exists():
            raise forms.ValidationError('A refund already exists for this purchase.')

        return quantity


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
