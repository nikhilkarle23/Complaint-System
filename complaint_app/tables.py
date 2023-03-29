from datetime import date

from django.contrib.auth.models import User
from django.utils.html import format_html
from django_tables2 import tables

from complaint_app.models import ComplaintModel, UserProfileModel


class ComplaintTable(tables.Table):
    city = tables.columns.Column(accessor='pk')

    view = tables.columns.TemplateColumn(verbose_name='View',
                                         template_name='detailview.html',
                                         orderable=False)

    class Meta:
        model = ComplaintModel
        fields = (
            'id',
            'title',
            'status',
            'created_date',
            'solved_by',
            'solved_date',
        )

    @staticmethod
    def render_city(value):
        obj = ComplaintModel.objects.get(pk=value)
        user_city = UserProfileModel.objects.filter(user=obj.user).first().city
        return user_city

    def render_status(self, value):
        if value == 'Pending':
            return format_html("<span class='badge bg-danger'>{}</span>", value)
        elif value == 'Completed':
            return format_html("<span class='badge bg-success'>{}</span>", value)
        else:
            return format_html("<span class='badge bg-warning'>{}</span>", value)

    def render_created_date(self, value):
        return value.strftime("%b-%d %Y")

    def render_solved_date(self, value):
        if value:
            return value.strftime("%b-%d %Y")
        else:
            return value
