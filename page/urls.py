from django.urls import path

from .views import *
urlpatterns = [

    path('', HomePageView.as_view(), name='home'),
        path('dashboard/', DashboardView.as_view(), name='dashboard'),
        path('logout/', LogoutView.as_view(), name='logout'),
]