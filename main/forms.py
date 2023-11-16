from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Product, Purchase, Refund, User
from myshop import settings


class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


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
            # if hasattr(purchase, "refund"):
            #     messages.error(self.request, "Refund request exists")
            #     raise ValidationError('Refund request exists')
            time_since_purchase = timezone.now() - purchase.purchase_time
            if time_since_purchase.total_seconds() > settings.REFUND_LIMIT_TIME:
                messages.error(self.request, 'The return period has expired.')
                raise ValidationError('The return period has expired.')
            # if Refund.objects.filter(id=self.request.POST.get('purchase_id').exists()):
            #     raise ValidationError('Refund already exists')
            else:
                self.purchase = purchase

        except Purchase.DoesNotExist:
            raise forms.ValidationError('Purchase with the given ID does not exist.')

    def save(self, commit=True):
        Refund.objects.create(refund_purchase=self.purchase)


class PurchaseForm(forms.ModelForm):
    quantity = forms.IntegerField(label='Quantity', initial=1, required=True, widget=forms.NumberInput)

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


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock']
