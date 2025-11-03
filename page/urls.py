from django.urls import path

from .views import *
urlpatterns = [

    path('', HomePageView.as_view(), name='home'),
        path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('upload/', UploadStatementView.as_view(), name='upload_statement'),
        path('statements/', StatementListView.as_view(), name='statements'),
            path('statements/delete/<int:pk>/', DeleteStatementView.as_view(), name='delete_statement'),
        path('logout/', LogoutView.as_view(), name='logout'),
]