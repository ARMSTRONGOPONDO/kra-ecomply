from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from page.models import Invoice, UploadedStatement


class Command(BaseCommand):
    help = 'Check invoices for a specific user or all users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username to check invoices for',
        )

    def handle(self, *args, **options):
        username = options.get('username')

        if username:
            try:
                user = User.objects.get(username=username)
                self.check_user_invoices(user)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User "{username}" does not exist'))
        else:
            # Check all users
            users = User.objects.all()
            for user in users:
                self.check_user_invoices(user)
                self.stdout.write('-' * 50)

    def check_user_invoices(self, user):
        self.stdout.write(self.style.SUCCESS(f'\n=== User: {user.username} ==='))
        
        # Check uploaded statements
        statements = UploadedStatement.objects.filter(user=user).order_by('-uploaded_at')
        self.stdout.write(f'Total Statements Uploaded: {statements.count()}')
        
        if statements.exists():
            self.stdout.write('\nRecent Statements:')
            for stmt in statements[:5]:
                self.stdout.write(f'  - {stmt.file.name} (uploaded: {stmt.uploaded_at})')
        
        # Check invoices
        invoices = Invoice.objects.filter(user=user).order_by('-created_at')
        self.stdout.write(f'\nTotal Invoices: {invoices.count()}')
        
        if invoices.exists():
            self.stdout.write('\nRecent Invoices:')
            for inv in invoices[:10]:
                self.stdout.write(
                    f'  - {inv.number} | {inv.item[:50]} | '
                    f'Ksh {inv.amount} | {inv.created_at}'
                )
        else:
            self.stdout.write(self.style.WARNING('  No invoices found for this user'))
