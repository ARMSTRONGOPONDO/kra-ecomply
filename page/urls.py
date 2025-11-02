from django.urls import path

from .views import *
urlpatterns = [

    path('', HomePageView.as_view(), name='home'),
    path('invoice/', InvoiceView.as_view(), name='invoice'),
    path('inside/', InsideView.as_view(), name='inside'),
        path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('upload/', UploadStatementView.as_view(), name='upload_statement'),
        path('logout/', LogoutView.as_view(), name='logout'),
]