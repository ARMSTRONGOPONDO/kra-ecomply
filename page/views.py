from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login ,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage


from ecomply import settings


class HomePageView(TemplateView):
    template_name = 'hero.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(username=username)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, self.template_name)

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')

@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'dashboard/home.html'







# from requests.auth import HTTPBasicAuth # Not needed anymore, as we are doing manual encoding

class InvoiceView(TemplateView):
    template_name = 'invoice.html'



class InsideView(TemplateView):
    template_name = 'dashboard/in.html'



@method_decorator(login_required, name='dispatch')
class UploadStatementView(View):
    template_name = 'dashboard/home.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        uploaded_file = request.FILES.get('statement')
        if not uploaded_file:
            messages.error(request, "Please select a file to upload.")
            return redirect('upload_statement')

        # Save file using Django’s built-in file system storage
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_url = fs.url(filename)

        messages.success(request, f"File '{uploaded_file.name}' uploaded successfully.")
        return render(request, self.template_name, {'file_url': file_url})