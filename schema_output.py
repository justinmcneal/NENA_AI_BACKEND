# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AnalyticsIncomerecord(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    record_date = models.DateField()
    notes = models.TextField()
    created_at = models.DateTimeField()
    user = models.ForeignKey('UsersCustomuser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'analytics_incomerecord'


class AnalyticsUseranalytics(models.Model):
    total_loan_amount = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    total_amount_repaid = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    last_updated = models.DateTimeField()
    user = models.OneToOneField('UsersCustomuser', models.DO_NOTHING)
    average_monthly_income = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    business_consistency_score = models.FloatField()

    class Meta:
        managed = False
        db_table = 'analytics_useranalytics'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class DjangoAdminLog(models.Model):
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('UsersCustomuser', models.DO_NOTHING)
    action_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class DocumentsAttachment(models.Model):
    file = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True, null=True)
    user_request = models.ForeignKey('DocumentsUserrequest', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'documents_attachment'


class DocumentsUserdocument(models.Model):
    document_type = models.CharField(max_length=50)
    file = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField()
    user = models.ForeignKey('UsersCustomuser', models.DO_NOTHING)
    analysis_status = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'documents_userdocument'


class DocumentsUserrequest(models.Model):
    request_type = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20)
    submission_date = models.DateTimeField()
    user = models.ForeignKey('UsersCustomuser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'documents_userrequest'


class LoansLoan(models.Model):
    loan_code = models.CharField(unique=True, max_length=12)
    loaned_amount = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    amount_payable = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    monthly_repayment = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    months_left = models.IntegerField()
    loan_term = models.IntegerField()
    monthly_income = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    created_at = models.DateTimeField()
    status = models.CharField(max_length=20)
    next_repayment_due_date = models.DateField(blank=True, null=True)
    repayment_status = models.CharField(max_length=20)
    user = models.ForeignKey('UsersCustomuser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'loans_loan'


class LoansRepayment(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    payment_date = models.DateTimeField()
    loan = models.ForeignKey(LoansLoan, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'loans_repayment'


class UsersCustomuser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    phone_number = models.CharField(unique=True, max_length=15)
    first_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30)
    last_otp_sent_at = models.DateTimeField(blank=True, null=True)
    last_name = models.CharField(max_length=30)
    pin_hash = models.CharField(max_length=128, blank=True, null=True)
    verification_status = models.CharField(max_length=20)
    is_active = models.BooleanField()
    is_staff = models.BooleanField()
    date_joined = models.DateTimeField()
    income = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    loan_status = models.CharField(max_length=20)
    barangay = models.CharField(max_length=100)
    city_town = models.CharField(max_length=100)
    civil_status = models.CharField(max_length=20)
    date_of_birth = models.DateField(blank=True, null=True)
    education_level = models.CharField(max_length=20)
    gender = models.CharField(max_length=20)
    province = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    business_address = models.CharField(max_length=255)
    business_industry = models.CharField(max_length=100)
    business_name = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'users_customuser'


class UsersCustomuserGroups(models.Model):
    customuser = models.ForeignKey(UsersCustomuser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'users_customuser_groups'
        unique_together = (('customuser', 'group'),)


class UsersCustomuserUserPermissions(models.Model):
    customuser = models.ForeignKey(UsersCustomuser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'users_customuser_user_permissions'
        unique_together = (('customuser', 'permission'),)
