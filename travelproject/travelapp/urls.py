from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('category/<slug:slug>/', views.category_packages, name='category'),
    path('package/<int:id>/', views.package_details, name='package_details'),

    path('booking/<int:package_id>/', views.booking, name='booking'),
    path('payment/', views.payment, name='payment'),
    path('success/', views.success, name='success'),

    path('receipt/<int:booking_id>/', views.receipt, name='receipt'),
    path('ticket/<int:booking_id>/', views.e_ticket, name='e_ticket'),

    path('my-trips/', views.my_bookings, name='my_bookings'),
    path('cancel/<int:id>/', views.cancel_booking, name='cancel_booking'),

    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/toggle/<int:package_id>/', views.toggle_wishlist, name='toggle_wishlist'),

    path('trip-planner/', views.trip_planner, name='trip_planner'),
    path('contact/', views.contact, name='contact'),

    path('profile/', views.profile, name='profile'),

    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('dashboard/package/add/', views.admin_add_package, name='admin_add_package'),
    path('dashboard/package/edit/<int:id>/', views.admin_edit_package, name='admin_edit_package'),
    path('dashboard/package/delete/<int:id>/', views.admin_delete_package, name='admin_delete_package'),

    path('dashboard/booking/status/<int:id>/', views.admin_update_booking_status, name='admin_update_booking_status'),

    path('dashboard/refund/approve/<int:id>/', views.admin_approve_refund, name='admin_approve_refund'),
    path('dashboard/refund/reject/<int:id>/', views.admin_reject_refund, name='admin_reject_refund'),
    path('dashboard/refund/complete/<int:id>/', views.admin_complete_refund, name='admin_complete_refund'),

    path('dashboard/enquiry/status/<int:id>/', views.admin_update_enquiry_status, name='admin_update_enquiry_status'),
]