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
from django.http import HttpResponse
from ecomply import settings
from .models import UploadedStatement ,Invoice
import os
import fitz
import logging
import traceback
import csv
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO
from datetime import datetime

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

            # Detect file type and parse accordingly
            file_extension = os.path.splitext(filename)[1].lower()
            logger.info(f"File type detected: {file_extension}")
            
            lines = []
            
            if file_extension == '.pdf':
                # Parse PDF
                try:
                    pdf_text = ""
                    with fitz.open(file_path) as doc:
                        for page in doc:
                            pdf_text += page.get_text("text")
                    logger.info(f"PDF parsed, extracted {len(pdf_text)} characters")
                    lines = [line.strip() for line in pdf_text.splitlines() if line.strip()]
                except Exception as pdf_error:
                    logger.error(f"PDF parsing error: {str(pdf_error)}")
                    messages.error(request, "Failed to read PDF file. Please ensure it's a valid PDF.")
                    return redirect('upload_statement')
                    
            elif file_extension == '.csv':
                # Parse CSV
                try:
                    with open(file_path, 'r', encoding='utf-8-sig') as csvfile:
                        # Read all rows
                        csv_reader = csv.reader(csvfile)
                        for row in csv_reader:
                            # Add each cell as a line
                            for cell in row:
                                if cell.strip():
                                    lines.append(cell.strip())
                    logger.info(f"CSV parsed, extracted {len(lines)} cells")
                except Exception as csv_error:
                    logger.error(f"CSV parsing error: {str(csv_error)}")
                    messages.error(request, "Failed to read CSV file. Please ensure it's a valid CSV.")
                    return redirect('upload_statement')
                    
            else:
                logger.error(f"Unsupported file type: {file_extension}")
                messages.error(request, f"Unsupported file type: {file_extension}. Please upload a PDF or CSV file.")
                return redirect('upload_statement')
            
            logger.info(f"Extracted {len(lines)} lines from file")

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


@method_decorator(login_required, name='dispatch')
class DownloadInvoicesPDFView(View):
    def get(self, request):
        # Get all invoices for the user
        invoices = Invoice.objects.filter(user=request.user).order_by('-created_at')
        
        if not invoices.exists():
            messages.warning(request, "No invoices to download.")
            return redirect('invoices')
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        
        # Container for PDF elements
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a202c'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#4a5568'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        # Add title
        title = Paragraph("Invoice Report", title_style)
        elements.append(title)
        
        # Add date and user info
        date_info = Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M')}<br/>User: {request.user.username}", subtitle_style)
        elements.append(date_info)
        elements.append(Spacer(1, 20))
        
        # Create table data
        data = [['Invoice No', 'Description', 'Amount (Ksh)', 'Date']]
        
        total_amount = 0
        for invoice in invoices:
            data.append([
                invoice.number,
                invoice.item[:50],  # Truncate long descriptions
                f"{invoice.amount:,.2f}",
                invoice.created_at.strftime('%b %d, %Y')
            ])
            total_amount += float(invoice.amount)
        
        # Add total row
        data.append(['', '', f"Total: {total_amount:,.2f}", ''])
        
        # Create table
        table = Table(data, colWidths=[1.5*inch, 3*inch, 1.5*inch, 1.5*inch])
        
        # Style the table
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Body styling
            ('BACKGROUND', (0, 1), (-1, -2), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
            ('ALIGN', (0, 1), (0, -2), 'LEFT'),
            ('ALIGN', (2, 1), (2, -2), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f7fafc')]),
            
            # Total row styling
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#edf2f7')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('ALIGN', (2, -1), (2, -1), 'RIGHT'),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(table)
        
        # Add footer
        elements.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#718096'),
            alignment=TA_CENTER
        )
        footer = Paragraph(f"Total Invoices: {invoices.count()} | Generated by eComply System", footer_style)
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF from buffer
        pdf = buffer.getvalue()
        buffer.close()
        
        # Create response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoices_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        response.write(pdf)
        
        logger.info(f"User {request.user.username} downloaded {invoices.count()} invoices as PDF")
        
        return response
