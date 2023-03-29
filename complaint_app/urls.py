from django.urls import path

from complaint_app import views

app_name = 'complaint_app'

urlpatterns = [
    path('', views.ComplaintListView.as_view(), name='complaint_list'),
    path('new_complaint/', views.ComplaintFormView.as_view(), name='new_complaint'),
    path('complaint/<int:pk>', views.ComplaintDetailView.as_view(), name='complaint_detail'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('register/', views.RegisterView.as_view(), name='register_page'),
    path('login/', views.LoginView.as_view(), name='login_page'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile_update/<int:pk>/', views.UserUpdateView.as_view(), name='update_profile'),
    path('analytics/', views.chart_testing, name='analytics_page'),

    path('generate-pdf/', views.generate_pdf, name='generate-pdf'),
    path('generate-excel/', views.export_users_xls, name='export_users_xls'),

    path('action_create/<int:pk>', views.ActionCreateView.as_view(), name='action_create'),
    path('update_bulk_action/<int:pk>/<int:pk_action>', views.ActionBulkUpdateView.as_view(), name='update_bulk_action'),
    path('update_document/<int:pk>/<int:pk_complaint>', views.DocumentInlineUpdateView.as_view(), name='update_document'),

    path('update_action/<int:pk>/<int:pk_action>',views.ActionUpdateView.as_view(), name='update_action'),
    path('update_remark/<int:pk>', views.UpdateRemark.as_view(), name='update_remark'),
]
