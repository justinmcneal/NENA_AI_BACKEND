from django.core.management.base import BaseCommand
from loans.models import Loan
from datetime import date

class Command(BaseCommand):
    help = 'Updates the repayment_status of loans to OVERDUE if they are past their due date.'

    def handle(self, *args, **options):
        overdue_loans = Loan.objects.filter(
            status='APPROVED',
            next_repayment_due_date__lt=date.today(),
            repayment_status='ON_TIME'
        )

        for loan in overdue_loans:
            loan.repayment_status = 'OVERDUE'
            loan.save(update_fields=['repayment_status'])
            self.stdout.write(self.style.SUCCESS(f'Successfully updated loan {loan.loan_code} to OVERDUE.'))

        self.stdout.write(self.style.SUCCESS('Finished updating loan statuses.'))