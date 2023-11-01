from datetime import timezone
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import FormView
from .forms import UserCreationForm, ProductForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Purchase, Refund
from django.utils import timezone


class CreateRefund(LoginRequiredMixin, View):
    def post(self, request, purchase_id):
        purchase = get_object_or_404(Purchase, pk=purchase_id)

        if Refund.objects.filter(refund_purchase=purchase).exists():
            messages.error(request, 'A refund already exists for this purchase.')
            return redirect('purchase_list')

        time_since_purchase = timezone.localtime(timezone.now()) - purchase.purchase_time
        if time_since_purchase.total_seconds() > 180:
            messages.error(request, 'The return period has expired.')
            return redirect('purchase_list')

        refund = Refund.objects.create(refund_purchase=purchase)
        return render(request, 'main/refund/confirm_refund.html', {'refund': refund})


class RefundList(LoginRequiredMixin, ListView):
    model = Refund
    template_name = 'main/refund/refund_list.html'


class RefundAgree(LoginRequiredMixin, View):
    def post(self, request, refund_id):
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


class BuyProduct(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity'))

        if product.stock < quantity:
            return render(request, 'main/product/product_list.html', {'error_message': 'Not enough items in stock.'})

        user = request.user
        total_price = product.price * quantity

        if total_price > request.user.wallet:
            messages.error(request, "You don't have enough funds for this purchase")
            return render(request, 'main/product/product_list.html', {'error_message': "You don't have enough money."})

        user.wallet -= total_price
        user.save()

        Purchase.objects.create(user=request.user, product=product, quantity=quantity)

        product.stock -= quantity
        product.save()

        return redirect('product_list')


class PurchaseList(LoginRequiredMixin, ListView):
    model = Purchase
    template_name = 'main/purchase/purchase_list.html'
    context_object_name = 'purchases'

    def get_queryset(self):
        return Purchase.objects.filter(user=self.request.user)


class DeleteProduct(LoginRequiredMixin, View):
    def get(self, request, product_id):
        if not request.user.is_staff:
            return redirect('login')

        product = get_object_or_404(Product, pk=product_id)
        product.delete()
        return redirect('product_list')


class EditProduct(LoginRequiredMixin, View):
    def get(self, request, product_id):
        if not request.user.is_staff:
            return redirect('login')

        product = get_object_or_404(Product, id=product_id)
        form = ProductForm(instance=product)
        return render(request, 'main/product/edit_product.html', {'form': form})

    def post(self, request, product_id):
        if not request.user.is_staff:
            return redirect('login')

        product = get_object_or_404(Product, id=product_id)
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
        return render(request, 'main/product/edit_product.html', {'form': form})


class AddProduct(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.is_staff:
            return redirect('login')

        form = ProductForm()
        return render(request, 'main/product/add_product.html', {'form': form})

    def post(self, request):
        if not request.user.is_staff:
            return redirect('login')

        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
        return render(request, 'main/product/add_product.html', {'form': form})


class ProductList(ListView):
    model = Product
    template_name = 'main/product/product_list.html'
    context_object_name = 'products'


class Login(LoginView):
    template_name = 'main/user/login.html'
    success_url = '.'
    next_page = 'home'

    def form_valid(self, form):
        response = super().form_valid(form)
        return response

    def form_invalid(self, form):
        return super().form_invalid(form)


class Logout(LogoutView):
    next_page = 'home'


class Register(FormView):
    template_name = 'main/user/register.html'
    form_class = UserCreationForm
    success_url = 'home'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)
