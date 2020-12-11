# Create your models here.

from django.db import models
from django.utils import timezone

import datetime


class Base(models.Model):
    base_name = models.CharField(max_length=300, default='Nothing')
    base_create_date = models.DateField(default=timezone.now)
    base_modified_date = models.DateField(default=timezone.now)
    created_by = models.CharField(max_length=300, default='Nothing')
    technical_name = models.CharField(max_length=300, default='Nothing')
    table_type = models.CharField(max_length=300, default='Nothing')
    discription = models.CharField(max_length=500, default='Nothing')
    purpose = models.CharField(max_length=400, default='Nothing')
    bcp = models.CharField(max_length=300, default='Nothing')
    tags = models.CharField(max_length=400, default='Nothing')
    fk = models.IntegerField(default=1)

    class Meta:
        db_table = 'Base'

    def __int__(self):
        return self.id


class Group_model_primary(models.Model):
    table_id_primary = models.IntegerField(default=0)
    tables_name_primary = models.CharField(default="Nothing", max_length=200)
    created_users_id = models.IntegerField(default=0)
    created_users_email = models.CharField(max_length=300, default="Unknown")
    Group_name = models.CharField(default="Nothing", max_length=100)

    class Meta:
        db_table = 'Model_Group_Primary'

    def __int__(self):
        return self.id


class Group_model_secondary(models.Model):
    secondary_tables_id = models.CharField(default="[]", max_length=200)
    secondary_tables_name = models.CharField(default="Nothing", max_length=200)
    primary_table_fk = models.IntegerField(default=0)

    class Meta:
        db_table = 'Model_Group_Secondary'

    def __int__(self):
        return self.id


class Login(models.Model):
    name = models.CharField(max_length=50, default='Nothing')
    phone = models.CharField(max_length=50, default='0000000000')
    password = models.CharField(max_length=50, default='Nothing')
    email = models.CharField(max_length=50, default='Nothing')
    is_active = models.CharField(max_length=50, default='Nothing')
    created_date = models.DateField(default=timezone.now)
    company_name = models.CharField(max_length=300, default='Unknown')
    profile = models.CharField(max_length=300, default='Unknown')
    role = models.CharField(max_length=300, default='Unknown')
    disable_period = models.CharField(max_length=300, default='Unknown')
    disable_period_end = models.CharField(max_length=300, default='Unknown')
    is_disabled = models.CharField(max_length=300, default='Unknown')
    account_type = models.CharField(max_length=50, default='Unknown')

    class Meta:
        db_table = 'Login'

    def __int__(self):
        return self.id


class Basecolumns(models.Model):
    """
    class for creating and storing table name
    """

    base_name = models.CharField(max_length=300, default='Nothing')
    base_create_date = models.DateField(default=timezone.now)
    base_modified_date = models.DateField(default=timezone.now)
    c_name = models.CharField(max_length=300, default='Nothing')
    t_name = models.CharField(max_length=300, default='Nothing')
    d_type = models.CharField(max_length=300, default='Text')
    nul_type = models.CharField(max_length=300, default='NOTNULL')
    calc_type = models.CharField(max_length=20, default="Nothing")
    d_size = models.IntegerField(default=40)
    base_fk = models.IntegerField(default=0)

    class Meta:
        db_table = 'Basecolumns'

    def __int__(self):
        return self.id


class Basedetails(models.Model):
    """
    class for creating and storing table name
    """
    base_name = models.CharField(max_length=300, default='Nothing')
    c_v = models.CharField(max_length=300, default='Nothing')
    bc_fk = models.IntegerField(default=1)
    row_num = models.IntegerField(default=1)

    class Meta:
        db_table = 'Basedetails'

    def __int__(self):
        return self.id


class Calculation(models.Model):
    equ = models.CharField(max_length=500, default='Nothing')
    equ_normal = models.CharField(max_length=500, default='Nothing')
    createdby = models.CharField(max_length=500, default='Nothing')
    fk_table = models.IntegerField(default=1)
    fk_column = models.IntegerField(default=1)
    type_of_calc = models.CharField(max_length=100, default='Normal_calc')
    const_position = models.IntegerField(default=0)

    class Meta:
        db_table = 'Calculation'

    def __int__(self):
        return self.id


class Profile(models.Model):
    name = models.CharField(max_length=50, default='Nothing')
    lname = models.CharField(max_length=50, default='Nothing')
    phone = models.BigIntegerField(default=0)
    skype = models.CharField(max_length=50, default='Nothing')
    location = models.CharField(max_length=50, default='Nothing')
    user_image = models.FileField(blank=True, upload_to="media")
    log_fk = models.IntegerField(default=1)

    class Meta:
        db_table = 'Profile'

    def __int__(self):
        return self.id


class notification_Messages(models.Model):
    sender_id = models.IntegerField(default=1)
    reciever_id = models.CharField(max_length=100, default='Unknown')
    send_date = models.DateField(default=timezone.now)
    status = models.IntegerField(default=1)
    heading = models.CharField(max_length=200, default='No Message')
    message = models.CharField(max_length=500, default='No Message')
    link = models.CharField(max_length=200, default='No')

    class Meta:
        db_table = 'Notification_tbl'

    def __int__(self):
        return self.id


class user_List(models.Model):
    role = models.IntegerField(default=0)
    profile = models.CharField(max_length=50, default='No')
    table_id = models.IntegerField(default=0)
    report_id = models.IntegerField(default=0)
    admin_id = models.IntegerField(default=1)
    user_id = models.CharField(max_length=200, default='No')
    created_date = models.DateField(default=datetime.date.today())

    class Meta:
        db_table = 'Users_list'

    def __int__(self):
        return self.id


class permissions(models.Model):
    created_user = models.IntegerField(default=0)
    role = models.CharField(max_length=200, default='None')
    about = models.TextField(default='Describe this Role / Group in few words')
    add_user = models.CharField(max_length=20, default="False")
    create_tables = models.CharField(max_length=20, default="False")
    add_data = models.CharField(max_length=20, default="False")
    delete_data = models.CharField(max_length=20, default="False")
    update_data = models.CharField(max_length=20, default="False")
    add_col = models.CharField(max_length=20, default="False")
    delete_col = models.CharField(max_length=20, default="False")
    update_col = models.CharField(max_length=20, default="False")
    delete_report = models.CharField(max_length=20, default="False")
    create_report = models.CharField(max_length=20, default="False")
    view_report = models.CharField(max_length=20, default="False")

    class Meta:
        db_table = 'Permission_tbl'

    def __int__(self):
        return self.id


class Report(models.Model):
    Reportname = models.CharField(max_length=50, default='Nothing')
    DetailRname = models.CharField(max_length=50, default='Nothing')
    table_id = models.IntegerField(default=0)
    created_date = models.DateField(default=datetime.date.today())
    created_by = models.CharField(max_length=300, default='Nothing')

    class Meta:
        db_table = 'report'

    def __int__(self):
        return self.id


class Reportcontent(models.Model):

    reportid = models.IntegerField(default=0)
    column_id = models.IntegerField(default=1)

    class Meta:
        db_table = 'reportid'

    def __int__(self):
        return self.id


class pdfReport(models.Model):
    Reportname = models.CharField(max_length=50, default='Nothing')
    DetailRname = models.CharField(max_length=50, default='Nothing')
    pdf_path = models.FileField(blank=True, upload_to="media/reports")
    created_date = models.DateField(default=datetime.date.today())
    created_by = models.CharField(max_length=300, default='Nothing')

    class Meta:
        db_table = 'report_pdf'

    def __int__(self):
        return self.id

class designation(models.Model):

    profile   = models.CharField(max_length=50, default='No')
    created_by=models.CharField(max_length=300, default='Nothing')

    class Meta:
        db_table = 'designation'

    def __int__(self):
        return self.id

