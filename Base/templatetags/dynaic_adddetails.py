from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render


from Base.models import Base, Basecolumns, Basedetails

from django import template
from django.db.models import Q

register = template.Library()


@register.inclusion_tag('option.html')
def dynamic_val(col_id=0):
    data_set = Basecolumns.objects.filter(pk=col_id).values( 'base_name', 'c_name', 'base_fk', 'pk', 'd_type' )
    col=''
    for x in data_set:
        col=x['c_name']
    col = col.split('(')
    print(col)

    # '6', 'Nothing', '2020-06-01', '2020-06-01', 'Qr Code', '1', '2'

    mapp_value = []
    for item in data_set:
        if item['d_type'].isnumeric():
            mapp_value.append(item['d_type'])
        if len( mapp_value ) > 0:
            print("mapp value : "+mapp_value[0])
            print("c_name : "+col[0].strip())
            mapp_filter_columns = Basecolumns.objects.filter(Q(base_fk__in=mapp_value) & Q(c_name=col[0].strip()))\
                .values( 'base_name', 'c_name', 'base_fk', 'pk', 'd_type')
            # '3', 'Nothing', '2020-06-01', '2020-06-01', 'Bay Name', 'Text', '1'
            # '4', 'Nothing', '2020-06-01', '2020-06-01', 'Qr Code', 'Numeric', '1'

            mapp_filter_arry = []
            for item in mapp_filter_columns:
                mapp_filter_arry.append( item['pk'])
                print("x---> " + str(item['pk']))
                # '3'
                # '4'
            filter_value = Basedetails.objects.filter( bc_fk__in=mapp_filter_arry ).values('c_v', 'bc_fk', 'pk',
                                                                                                'row_num').order_by(
                'row_num',
                'bc_fk')

            # '1', 'Nothing', '1', '4', '1'
            # '2', 'Nothing', 'BAY 1', '3', '1'
            # '3', 'Nothing', 'BAY 2', '3', '2'
            # '4', 'Nothing', '2', '4', '2'

            return {'filter_value':filter_value}


