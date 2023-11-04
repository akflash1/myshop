from datetime import timezone
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import FormView, CreateView, DeleteView, UpdateView
from .forms import ProductForm, RefundForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Purchase, Refund
from django.utils import timezone


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return redirect('login')


class CreateRefund(AdminRequiredMixin, CreateView):
    model = Refund
    form_class = RefundForm
    success_url = reverse_lazy('purchase_list')

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()

        purchase_id = self.kwargs['purchase_id']
        return form_class(purchase_id=purchase_id, request=self.request, **self.get_form_kwargs())

    def form_valid(self, form):
        purchase = get_object_or_404(Purchase, pk=self.kwargs['purchase_id'])

        if Refund.objects.filter(refund_purchase=purchase).exists():
            messages.error(self.request, 'A refund already exists for this purchase.')
            return reverse_lazy('purchase_list')

        time_since_purchase = timezone.now() - purchase.purchase_time
        if time_since_purchase.total_seconds() > 180:
            messages.error(self.request, 'The return period has expired.')
            return reverse_lazy('purchase_list')

        form.instance.refund_purchase = purchase
        return super().form_valid(form)


class RefundList(AdminRequiredMixin, ListView):
    model = Refund
    template_name = 'main/refund/refund_list.html'


class RefundAgree(AdminRequiredMixin, View):
    def post(self, request, refund_id):
        print("RefundAgree post method called")
        if not request.user.is_staff:
            messages.error(request, "The administrator must confirm your refund.")
            return redirect('login')

        refund = get_object_or_404(Refund, pk=refund_id)
        action = request.POST.get('action')

        if action == 'agree':
            purchase = refund.refund_purchase

            product = purchase.product
            product.stock += purchase.quantity
            product.save()

            purchase.delete()
            refund.delete()
        elif action == 'reject':
            refund.delete()

        return redirect('refunds')


class BuyProduct(LoginRequiredMixin, CreateView):
    model = Purchase
    fields = ['quantity']
    success_url = '/product_list/'

    def form_valid(self, form):
        product = get_object_or_404(Product, id=self.kwargs['product_id'])
        quantity = form.cleaned_data['quantity']

        if product.stock < quantity:
            return render(self.request, 'main/product/product_list.html',
                          {'error_message': 'Not enough items in stock.'})

        total_price = product.price * quantity

        if total_price > self.request.user.wallet:
            messages.error(self.request, "You don't have enough funds for this purchase")
            return render(self.request, 'main/product/product_list.html',
                          {'error_message': "You don't have enough money."})

        with transaction.atomic():
            self.request.user.wallet -= total_price
            self.request.user.save()

            purchase = form.save(commit=False)
            purchase.user = self.request.user
            purchase.product = product
            purchase.save()

            product.stock -= quantity
            product.save()

        return super().form_valid(form)


class PurchaseList(LoginRequiredMixin, ListView):
    model = Purchase
    template_name = 'main/purchase/purchase_list.html'
    context_object_name = 'purchases'

    def get_queryset(self):
        return Purchase.objects.filter(user=self.request.user)


class DeleteProduct(AdminRequiredMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('product_list')

    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('login')
        return super().post(request, *args, **kwargs)


class EditProduct(AdminRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'main/product/edit_product.html'
    success_url = reverse_lazy('product_list')


class AddProduct(AdminRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'main/product/add_product.html'
    success_url = reverse_lazy('product_list')


class ProductList(ListView):
    model = Product
    template_name = 'main/product/product_list.html'
    context_object_name = 'products'


class Login(LoginView):
    template_name = 'main/user/login.html'
    success_url = '.'
    next_page = 'home'


class Logout(LogoutView):
    next_page = 'home'


class Register(FormView):
    template_name = 'main/user/register.html'
    success_url = 'home'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)
