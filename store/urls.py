# store/urls.py
from django.urls import path
from .views import auth_views, home_views, staff_views, customer_views

app_name = 'store'

urlpatterns = [
    # Home & Auth
    path('', home_views.home_view, name='home'),
    path('register/', auth_views.UserRegisterView.as_view(), name='register'),
    path('login/', auth_views.UserLoginView.as_view(), name='login'),
    path('logout/', auth_views.UserLogoutView.as_view(), name='logout'),

    # Staff Dashboard & Product Management
    path('staff/', staff_views.staff_dashboard, name='staff_dashboard'),
    path('staff/products/', staff_views.product_list_staff, name='product_list_staff'),
    path('staff/products/new/', staff_views.ProductCreateView.as_view(), name='product_create_staff'),
    path('staff/products/<int:pk>/edit/', staff_views.ProductUpdateView.as_view(), name='product_update_staff'),
    path('staff/products/<int:pk>/delete/', staff_views.product_delete_staff, name='product_delete_staff'),


    # Staff Basket Management
    path('staff/baskets/', staff_views.basket_list_staff, name='basket_list_staff'),
    path('staff/baskets/<int:pk>/', staff_views.basket_detail_staff, name='basket_detail_staff'),
    path('staff/baskets/<int:pk>/approve/', staff_views.basket_approve, name='basket_approve_staff'),
    path('staff/baskets/<int:pk>/deny/', staff_views.basket_deny, name='basket_deny_staff'),

    # Customer Shop
    path('shop/', customer_views.shop_home, name='shop_home'),
    path('shop/add-to-basket/<int:product_id>/', customer_views.add_to_basket, name='add_to_basket'),
    path('shop/basket/', customer_views.view_basket, name='view_basket'),
    path('shop/basket/update-item/<int:item_id>/', customer_views.update_basket_item, name='update_basket_item'),
    path('shop/basket/remove-item/<int:item_id>/', customer_views.remove_from_basket, name='remove_from_basket'),
    path('shop/basket/submit/', customer_views.submit_basket, name='submit_basket'),
    path('shop/history/', customer_views.basket_history, name='basket_history'),
    
    # If you still want Django's built-in auth URLs for password reset, etc.
    # you can include them here, perhaps namespaced differently or ensure templates are provided.
    # For now, focusing on custom flows.
    # path('accounts/', include('django.contrib.auth.urls')),
]
