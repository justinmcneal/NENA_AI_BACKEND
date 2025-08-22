import re
from rest_framework import serializers
from .models import CustomUser

def validate_ph_phone_number(value):
    # Regex for +63 followed by 10 digits
    if not re.fullmatch(r'\+63\d{10}', value):
        raise serializers.ValidationError("Phone number must be in the format +63XXXXXXXXXX (e.g., +639171234567).")
    return value

class UserRegistrationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15, validators=[validate_ph_phone_number])

    # def validate_phone_number(self, value):
    #     if CustomUser.objects.filter(phone_number=value).exists():
    #         raise serializers.ValidationError("A user with this phone number already exists.")
    #     return value

class OTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15, validators=[validate_ph_phone_number])
    otp_code = serializers.CharField(max_length=6)

class ResendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15, validators=[validate_ph_phone_number])

class ProfileCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'middle_name', 'last_name']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

class SetPINSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15, validators=[validate_ph_phone_number])
    pin = serializers.CharField(min_length=4, max_length=6) # Assuming 4-6 digit PIN

class LoginWithPINSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15, validators=[validate_ph_phone_number])
    pin = serializers.CharField(min_length=4, max_length=6)
