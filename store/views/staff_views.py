# store/views/staff_views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib import messages
from django.db import transaction # Import transaction
from ..models import Product, Basket, BasketItem
from ..forms import ProductForm

# --- Decorators for role checking ---
def is_staff(user):
    return user.is_authenticated and user.role == 'staff'

staff_login_required = user_passes_test(is_staff, login_url='store:login')

@staff_login_required
def staff_dashboard(request):
    return render(request, 'store/staff/staff_dashboard.html')

# --- Product Management ---
# (Product views remain the same)
@staff_login_required
def product_list_staff(request):
    products = Product.objects.all().order_by('name')
    return render(request, 'store/staff/product_list.html', {'products': products})

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'store/staff/product_form.html'
    success_url = reverse_lazy('store:product_list_staff')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create New Product'
        return context
    
    def dispatch(self, *args, **kwargs):
        return staff_login_required(super().dispatch)(*args, **kwargs)


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'store/staff/product_form.html'
    success_url = reverse_lazy('store:product_list_staff')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Edit Product: {self.object.name}'
        return context

    def dispatch(self, *args, **kwargs):
        return staff_login_required(super().dispatch)(*args, **kwargs)

@staff_login_required
def product_delete_staff(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, f"Product '{product.name}' deleted successfully.")
        return redirect('store:product_list_staff')
    return render(request, 'store/staff/product_confirm_delete.html', {'product': product})


# --- Basket Management ---
@staff_login_required
def basket_list_staff(request):
    status_filter = request.GET.get('status', 'submitted')
    baskets = Basket.objects.filter(status=status_filter).order_by('-updated_at')
    valid_statuses = [choice[0] for choice in Basket.STATUS_CHOICES if choice[0] not in ['active', 'abandoned']]
    return render(request, 'store/staff/basket_list.html', {
        'baskets': baskets,
        'current_status': status_filter,
        'status_choices': Basket.STATUS_CHOICES,
        'valid_statuses_for_filter': valid_statuses
    })

@staff_login_required
def basket_detail_staff(request, pk):
    basket = get_object_or_404(Basket.objects.prefetch_related('items__product', 'user'), pk=pk)
    return render(request, 'store/staff/basket_detail.html', {'basket': basket})

@staff_login_required
@transaction.atomic # Ensures stock updates and basket status change are all or nothing
def basket_approve(request, pk):
    basket = get_object_or_404(Basket.objects.select_related('user').prefetch_related('items__product'), pk=pk)
    if basket.status == 'submitted':
        # Check stock for all items before proceeding
        can_approve = True
        for item in basket.items.all():
            if item.quantity > item.product.stock:
                messages.error(request, f"Cannot approve: Not enough stock for {item.product.name}. Required: {item.quantity}, Available: {item.product.stock}.")
                can_approve = False
                break # Stop checking if one item is out of stock
        
        if can_approve:
            # Deduct stock
            for item in basket.items.all():
                product = item.product
                product.stock -= item.quantity
                product.save()
            
            basket.status = 'approved'
            basket.save()
            messages.success(request, f"Basket {basket.id} has been approved and stock updated.")
            # TODO: Add notifications to customer, etc.
        # If not can_approve, messages already added.
    else:
        messages.warning(request, f"Basket {basket.id} is not in a 'submitted' state and cannot be approved directly.")
    return redirect('store:basket_detail_staff', pk=pk)

@staff_login_required
def basket_deny(request, pk):
    basket = get_object_or_404(Basket, pk=pk)
    if basket.status == 'submitted':
        basket.status = 'denied'
        basket.save()
        messages.success(request, f"Basket {basket.id} has been denied.")
        # No stock adjustment needed here if stock is only deducted on approval.
        # If stock was "reserved" on submission, it would be added back here.
        # TODO: Add notifications, etc.
    else:
        messages.warning(request, f"Basket {basket.id} is not in a 'submitted' state and cannot be denied directly.")
    return redirect('store:basket_detail_staff', pk=pk)
