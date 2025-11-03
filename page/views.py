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
import logging
import traceback

logger = logging.getLogger(__name__)  

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

        try:
            # Ensure media directory exists
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = os.path.join(settings.MEDIA_ROOT, filename)

            logger.info(f"File saved: {file_path}")

            # Save UploadedStatement record
            try:
                UploadedStatement.objects.create(
                    user=request.user,
                    file=filename
                )
                logger.info(f"UploadedStatement created for user {request.user.username}")
            except Exception as db_error:
                logger.error(f"Database error creating UploadedStatement: {str(db_error)}")
                raise

            # Parse PDF
            try:
                pdf_text = ""
                with fitz.open(file_path) as doc:
                    for page in doc:
                        pdf_text += page.get_text("text")
                logger.info(f"PDF parsed, extracted {len(pdf_text)} characters")
            except Exception as pdf_error:
                logger.error(f"PDF parsing error: {str(pdf_error)}")
                messages.error(request, "Failed to read PDF file. Please ensure it's a valid PDF.")
                return redirect('upload_statement')

            lines = [line.strip() for line in pdf_text.splitlines() if line.strip()]
            logger.info(f"Extracted {len(lines)} lines from PDF")

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
                        logger.info(f"Invoice created: {receipt_no[:8]} - {details} - {amount}")
                        i += 7 
                    except (IndexError, ValueError) as parse_error:
                        logger.debug(f"Skipping line {i}: {parse_error}")
                        i += 1  
                    except Exception as invoice_error:
                        logger.error(f"Error creating invoice at line {i}: {str(invoice_error)}")
                        i += 1
                else:
                    i += 1

            logger.info(f"Total invoices created: {invoice_count}")

            if invoice_count == 0:
                messages.warning(request, "No transactions were detected in the uploaded statement. Please check the format.")
            else:
                messages.success(request, f"{invoice_count} invoices generated successfully.")

            return redirect('invoices')
            
        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"Upload failed for user {request.user.username}: {error_details}")
            messages.error(request, f"Upload failed: {str(e)}. Please check the file format and try again.")
            return redirect('upload_statement')


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
