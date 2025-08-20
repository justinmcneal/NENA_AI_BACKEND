from rest_framework import serializers
from .models import CustomUser

class UserRegistrationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

    def validate_phone_number(self, value):
        if CustomUser.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

class OTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    otp_code = serializers.CharField(max_length=6)

class ProfileCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'middle_name', 'last_name']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

class SetPINSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    pin = serializers.CharField(min_length=4, max_length=6) # Assuming 4-6 digit PIN

class LoginWithPINSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    pin = serializers.CharField(min_length=4, max_length=6)
