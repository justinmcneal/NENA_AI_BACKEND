import os
import django
import sys
from django.utils import timezone
from decimal import Decimal

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nena_ai_backend.settings')
django.setup()

from users.models import CustomUser
from documents.models import UserRequest, Attachment
from loans.models import Loan

def add_sample_data():
    print("Adding sample data...")

    # Create a sample user
    try:
        user, created = CustomUser.objects.get_or_create(
            username='sampleuser',
            defaults={
                'first_name': 'Sample',
                'last_name': 'User',
                'phone_number': '1234567890',
                'income': Decimal('5000.00'),
                'is_staff': True, # Make it staff so it appears in admin
                'is_superuser': True, # Make it superuser for full access
            }
        )
        if created:
            user.set_password('password') # Set a default password
            user.save()
            print(f"Created new user: {user.username}")
        else:
            print(f"User {user.username} already exists.")
        user.set_password('password') # Ensure password is set
        user.save()

    except Exception as e:
        print(f"Error creating/getting user: {e}")
        return

    # Create a sample UserRequest
    try:
        user_request, created = UserRequest.objects.get_or_create(
            user=user,
            request_type='Loan Application',
            description='Request for a personal loan.',
            defaults={
                'status': 'pending',
                'submission_date': timezone.now()
            }
        )
        if created:
            print(f"Created new user request: {user_request.request_type}")
        else:
            print(f"User request {user_request.request_type} already exists for {user.username}.")
    except Exception as e:
        print(f"Error creating/getting user request: {e}")
        return

    # Create a sample Loan
    try:
        loan, created = Loan.objects.get_or_create(
            user=user,
            loaned_amount=Decimal('10000.00'),
            defaults={
                'amount_payable': Decimal('10200.00'),
                'monthly_repayment': Decimal('850.00'),
                'months_left': 12,
                'loan_term': 12,
                'monthly_income': Decimal('5000.00'),
                'is_verified_by_bank': False,
            }
        )
        if created:
            print(f"Created new loan: {loan.loan_code}")
        else:
            print(f"Loan {loan.loan_code} already exists for {user.username}.")
    except Exception as e:
        print(f"Error creating/getting loan: {e}")
        return

    # Optional: Create a sample Attachment (requires a file to upload)
    # For simplicity, we'll skip actual file upload here. You'd need to handle file creation/mocking.
    # print("Skipping attachment creation for simplicity. Requires file handling.")

    print("Sample data added successfully!")

if __name__ == '__main__':
    add_sample_data()