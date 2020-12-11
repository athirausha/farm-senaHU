"""Farm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url 
from django.conf import settings
from django.conf.urls.static import static

from Base import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login',views.fn_login),
    path('register', views.Register),
    path('company_ind_reg_load', views.Register_users_load),
    path('company_registration', views.Register_users),
    path('personal_registration', views.personal_registration),
    path('logout', views.Logout),
    path('index', views.index),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',views.activate_account, name='activate'),
    path('basemater', views.Basecreation),
    path('addcolumns', views.Addcolumns),
    path('relation_maters', views.relation_maters),
    path('filter_columns_for_relation', views.filter_columns_for_relation),
    path('save_relation_column', views.save_relation_column),
    path('viewbase/<int:pkp>', views.Details),
    path('adddetails', views.Adddetails),
    path('save_relation_column_page_one', views.save_relation_column_page_one),
    path('adddetails', views.Adddetails),
    path('Newcol', views.Newcol),
    path('forgetpassword', views.forgetpassword),
    path('updatepass',views.Updatepassword),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z]+)/(?P<token>.+)/$',views.password_reset_confirm, name='password_reset_confirm'),
    path('newpassword', views.Newpassword),
    path('referanfce_col_filter', views.referanfce_col_filter),
    path('inline_type', views.inline_type),
    path('inlineedit', views.Updatedetails),
    path('delete_row', views.delete_row),
    path('deletecolumn', views.Columndelete),
    path('edit_column', views.edit_column),
    path('deletebase', views.Deletebase),
    path('deletedetails', views.Deletebasedetails),
    path('calculation_page', views.calculation_page),
    path('calc_save', views.calc_save),
    path('cal_add_details', views.cal_add_details),
    path('permission_user_list', views.permission_user_list),
    path('email_autoconplite', views.email_autoconplite),
    path('user_list_update', views.user_list_update),
    path('role_add', views.save_role),
    path('role_update_fetch', views.role_update_fetch),
    path('role_update', views.update_role),
    path('userprofile', views.userprofile),
    path('imageprofile', views.imageprofile),
    path('delete_user', views.delete_user_from_list),
    # Deleting Notification Individually
    path('delete_notification', views.delete_notification),
    # Deleting Notification All
    path('delete_notification_all', views.delete_notification_all),
    # Clearing Notification Individually
    path('clear_notification', views.clear_notification),
    # DELETE ACOOUNT OF USER
    path('delete_account', views.delete_account),
    path('delete_tables',views.Delete_tables),
    path('truncate_tables',views.Truncate_tables),
    path('delete_users',views.Delete_users),
    path('pro_update_fetch', views.pro_update_fetch),
    path('pro_update', views.update_pro),
    path('edit_modal',views.Editinmodal),
    path('fetch_columns', views.schema_fetchcolumns),
    path('schema_save', views.schemasave),
    path('colfilter', views.Col_filter),
    path('importx', views.importx),
    path('infoedit',views.infoedit),
    path('disable_account',views.disable_account),
    path('disable_user_account',views.disable_user_account),
    path('load_reportpage',views.report),
    path('load_reportpagefetch',views.reportfetch),
    # path('save_reportpage',views.getpdf),
    path('save_reportpage',views.reportsave),
    path('view_reportpage/<int:pkp>',views.viewreport),
    path('del_reportpage',views.deletereport),
    path('delete_userfrom_userlist',views.delete_users_from_userlist),
    path('load_detailsfetch',views.detailsmodel),
    path('detail_update',views.detailsupdate),
    path('loaddashboard',views.getdashboard),
    path('chartdata_fetch',views.create_chart),
    path('Models', views.group_models),
    path('Create_tbl_group', views.Create_tbl_group),
    path('delete_secondry_tbl', views.delete_secondry_tbl),
    path('Tables', views.additional_table),
    path('fetch_user_role',views.fetch_user_role),
    path('remove_user_account',views.remove_user_account),
    path('inline_type_sub_table',views.inline_type_sub_table),
    path('calc_equation_fetch', views.calc_equation_fetch),
    path('calc_edit', views.calc_edit),
    path('editcol',views.edit_tblcol),
    path('data_image_upload', views.data_image_upload),
    path('inline_update_image', views.inline_update_image),
    path('create_users_profle', views.create_profle_users),
    path('group_update_fetch', views.Group_update_fetch),
    path('update_group', views.Group_update),
    path('col-property-edit', views.col_property_edit),
    path('edit-column-property', views.edit_column_property),
    path('admin-user-management', views.admin_user_management),
    path('fetch_update_user', views.fetch_update_user),
    path('update_user_account', views.update_user_account),
    path('get_row', views.get_row),




]+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+static(settings.MEDIA_URL,
                                                                         document_root=settings.MEDIA_ROOT)
