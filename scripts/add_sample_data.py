from users.models import CustomUser
from documents.models import UserRequest, Attachment
from django.core.files.base import ContentFile

# Get or create a user
user, created = CustomUser.objects.get_or_create(
    phone_number='1234567890',
    defaults={
        'email': 'testuser@example.com',
        'username': 'testuser',
    }
)

if created:
    user.set_password('password')
    user.save()
    print("Created a new user: testuser")
else:
    print("Found existing user: testuser")


# Create a few user requests
request1 = UserRequest.objects.create(
    user=user,
    request_type='Loan Application',
    description='This is a sample loan application request.',
    status='pending'
)
print(f"Created UserRequest: {request1}")

request2 = UserRequest.objects.create(
    user=user,
    request_type='Document Submission',
    description='This is a sample document submission request.',
    status='pending'
)
print(f"Created UserRequest: {request2}")


# Create an attachment for the first request
attachment1 = Attachment.objects.create(
    user_request=request1,
    description='Sample attachment 1'
)
attachment1.file.save('sample1.txt', ContentFile(b'This is a sample file.'))
print(f"Created Attachment: {attachment1}")

print("Sample data created successfully.")
