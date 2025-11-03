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
from .models import UploadedStatement ,Invoice
import os
import fitz  

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


@method_decorator(login_required, name='dispatch')
class UploadStatementView(View):
    template_name = 'dashboard/home.html'



@method_decorator(login_required, name='dispatch')
class UploadStatementView(View):
    template_name = 'dashboard/upload.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        uploaded_file = request.FILES.get('statement')
        if not uploaded_file:
            messages.error(request, "Please select a file to upload.")
            return redirect('upload_statement')

        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        # Save UploadedStatement record
        UploadedStatement.objects.create(
            user=request.user,
            file=f'statements/{uploaded_file.name}'
        )

        pdf_text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                pdf_text += page.get_text("text")

        lines = [line.strip() for line in pdf_text.splitlines() if line.strip()]

        invoice_count = 0
        i = 0

        while i < len(lines):
            line = lines[i]

         
            if line.isalnum() and 8 <= len(line) <= 12:
                try:
                    receipt_no = line
                    completion_time = lines[i + 1] 
                    details = lines[i + 2]         
                    transaction_status = lines[i + 3]  
                    paid_in = lines[i + 4]
                    withdraw = lines[i + 5]         
                    balance = lines[i + 6]         

                    amount = float(paid_in.replace(",", ""))

                   
                    Invoice.objects.create(
                        user=request.user,
                        number=receipt_no[:8],
                        item=details,
                        amount=amount
                    )
                    invoice_count += 1
                    i += 7 
                except (IndexError, ValueError):
                    i += 1  
            else:
                i += 1

        if invoice_count == 0:
            messages.warning(request, "No transactions were detected in the uploaded statement.")
        else:
            messages.success(request, f"{invoice_count} invoices generated successfully.")

        return redirect('invoices')


@method_decorator(login_required, name='dispatch')
class StatementListView(View):
    template_name = 'dashboard/statements.html'

    def get(self, request):
        statements = UploadedStatement.objects.filter(user=request.user).order_by('-uploaded_at')
        return render(request, self.template_name, {'statements': statements})
    
@method_decorator(login_required, name='dispatch')
class DeleteStatementView(View):
    def post(self, request, pk):
        try:
            statement = UploadedStatement.objects.get(pk=pk, user=request.user)
          
            file_path = os.path.join(settings.MEDIA_ROOT, str(statement.file))
            if os.path.exists(file_path):
                os.remove(file_path)
          
            statement.delete()
            messages.success(request, "Deleted successfully.")
        except UploadedStatement.DoesNotExist:
            messages.error(request, "Statement not found or unauthorized access.")
        return redirect('statements')
    

@method_decorator(login_required, name='dispatch')
class InvoiceListView(View):
    template_name = 'dashboard/invoice.html'

    def get(self, request):
        invoices = Invoice.objects.filter(user=request.user).order_by('-created_at')
        return render(request, self.template_name, {'invoices': invoices})
