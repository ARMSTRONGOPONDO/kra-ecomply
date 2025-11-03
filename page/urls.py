from django.urls import path

from .views import *
from .debug_views import check_users

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('upload/', UploadStatementView.as_view(), name='upload_statement'),
    path('statements/', StatementListView.as_view(), name='statements'),
    path('invoices/', InvoiceListView.as_view(), name='invoices'),
    path('statements/delete/<int:pk>/', DeleteStatementView.as_view(), name='delete_statement'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Debug endpoint (remove after testing)
    path('debug/users/', check_users, name='debug_users'),
]