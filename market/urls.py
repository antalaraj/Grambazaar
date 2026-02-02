# d:\Grambazaar\grambazaar\market\urls.py
from django.urls import path
from . import views

app_name = 'market'

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('contact/', views.contact_us, name='contact'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('product/<slug:slug>/order/', views.buyer_order, name='buyer_order'),
    path('product/<slug:slug>/payment/', views.fake_payment, name='fake_payment'),

    # Authentication
    path('signup/', views.shg_signup, name='shg_signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Buyer Authentication
    path('buyer/register/', views.buyer_register, name='buyer_register'),
    path('buyer/login/', views.buyer_login_view, name='buyer_login'),
    path('buyer/logout/', views.buyer_logout, name='buyer_logout'),
    path('buyer/profile/', views.buyer_profile, name='buyer_profile'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),

    # SHG Dashboard
    path('shg/dashboard/', views.shg_dashboard, name='shg_dashboard'),
    path('shg/submit-product/', views.submit_product, name='submit_product'),
    path('shg/product/<int:product_id>/request-removal/', views.request_product_removal, name='request_product_removal'),
    path('shg/wallet/', views.shg_wallet, name='shg_wallet'),
    path('shg/forecast/', views.shg_forecast_view, name='shg_forecast_view'),

    # Admin Dashboard
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/add-product/', views.admin_add_product, name='admin_add_product'),
    path('admin/edit-product/<int:product_id>/', views.admin_edit_product, name='admin_edit_product'),
    path('admin/delete-product/<int:product_id>/', views.admin_delete_product, name='admin_delete_product'),
    path('admin/pending-products/', views.admin_pending_products, name='admin_pending_products'),
    path('admin/approve-product/<int:product_id>/', views.approve_product, name='approve_product'),
    path('admin/reject-product/<int:product_id>/', views.reject_product, name='reject_product'),
    path('admin/approve-removal/<int:product_id>/', views.approve_removal, name='approve_removal'),
    path('admin/reject-removal/<int:product_id>/', views.reject_removal, name='reject_removal'),
    path('admin/orders/', views.admin_orders, name='admin_orders'),
    path('admin/approve-order/<int:order_id>/', views.approve_order, name='approve_order'),
    path('admin/forecast/', views.generate_forecast, name='generate_forecast'),
    path('admin/digicourses/', views.admin_digicourses, name='admin_digicourses'),
    path('admin/digicourses/<int:course_id>/delete/', views.admin_delete_digicourse, name='admin_delete_digicourse'),

    # APIs
    path('instabrand/', views.instabrand_api, name='instabrand_api'),
    path('api/shg/wallet/', views.shg_wallet_api, name='shg_wallet_api'),
    path('api/admin/forecast/', views.admin_forecast_api, name='admin_forecast_api'),
    path('api/notifications/', views.notifications_poll, name='notifications_poll'),
    path('api/mark-notification-read/<int:notif_id>/', views.mark_notification_read, name='mark_notification_read'),
]