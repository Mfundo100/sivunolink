from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication (Standard)
    path('accounts/login/', views.CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('register/', views.register_buyer, name='register'),
    
    # Core App
    path('', views.landing_page, name='landing_page'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('marketplace/', views.marketplace_view, name='marketplace'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('verify-delivery/', views.verify_delivery_pin_view, name='verify_delivery'),
    path('driver-portal/', views.driver_portal, name='driver_portal'),
    path('dispute/<int:order_id>/', views.raise_dispute, name='raise_dispute'),
    path('payment/process/<int:order_id>/', views.process_payment, name='process_payment'),
    path('farmer/fulfilments/', views.farmer_fulfilments, name='farmer_fulfilments'),
    path('farmer/complete-fulfilment/<int:fulfilment_id>/', views.complete_fulfilment, name='complete_fulfilment'),
    path('archive-order/<int:order_id>/', views.archive_order, name='archive_order'),
    
    # Custom Admin Hub
    path('admin-dashboard/settings/', views.custom_admin_settings, name='custom_admin_settings'),
    path('admin-dashboard/users/', views.admin_users, name='admin_users'),
    path('admin-dashboard/approvals/', views.admin_approvals, name='admin_approvals'),
    path('admin-dashboard/assign/', views.admin_driver_assignment, name='admin_driver_assignment'),
    path('admin-dashboard/monitor/', views.admin_monitoring, name='admin_monitoring'),
    path('admin-dashboard/toggle-user/<int:user_id>/', views.toggle_user_status, name='toggle_user'),
    path('admin-dashboard/reports/', views.admin_reports, name='admin_reports'),
    path('admin-dashboard/export-csv/', views.export_csv, name='export_csv'),
    path('admin-dashboard/settings/commission/', views.admin_settings, name='admin_settings'),
    path('admin-dashboard/delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)