import django_filters

from complaint_app.models import ComplaintModel, UserProfileModel


class ComplaintFilter(django_filters.FilterSet):
    city = django_filters.CharFilter(field_name='city',method='city_filter', label='City')

    class Meta:
        model = ComplaintModel
        fields = ['status', 'solved_by', 'city']


    def city_filter(self, queryset, city, value):
        queryset = ComplaintModel.objects.filter(user=self.request.user, user__userprofilemodel__city__icontains=value)
        return queryset