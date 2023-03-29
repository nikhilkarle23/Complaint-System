import datetime
from io import BytesIO

import xlwt
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import transaction
from django.forms import modelformset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView, DetailView
from django_filters.views import FilterView
from django_tables2 import SingleTableView
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from complaint_app.filter import ComplaintFilter
from complaint_app.form import UserRegisterForm, UserProfileForm, UserUpdateForm, UserProfileUpdateForm, ComplaintForm, \
    ActionInlineFormSet, ActionUpdateFormset, ActionCreateFormset, DocumentUpdateInlineFormSet, ActionForm
from complaint_app.models import UserProfileModel, ComplaintModel, ComplaintDocument, ActionModel
from complaint_app.tables import ComplaintTable


# Create your views here.
class ComplaintListView(LoginRequiredMixin, FilterView, SingleTableView):
    template_name = "complaint_list.html"
    model = ComplaintModel
    table_class = ComplaintTable
    filterset_class = ComplaintFilter

    def get_queryset(self):
        if self.request.user.userprofilemodel.user_type == 'customer':
            return ComplaintModel.objects.filter(user_id=self.request.user.pk)
        else:
            return ComplaintModel.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        f = context['filter']
        has_filter = any(field in self.request.GET for field in set(f.get_fields()))
        context['has_filter'] = has_filter
        return context


class ComplaintFormView(CreateView):
    template_name = 'complaint_page.html'
    model = ComplaintModel
    form_class = ComplaintForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        if self.request.POST:
            context['action_form_set'] = ActionInlineFormSet(self.request.POST, prefix='action_form_set')
        else:
            context['action_form_set'] = ActionInlineFormSet(prefix='action_form_set')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        action_form_set = context['action_form_set']

        # save User Data
        form.instance.user = self.request.user
        form.instance.created_by = self.request.user.username
        self.object = form.save()
        if action_form_set.is_valid():
            action_form_set.instance = self.object
            action_form_set.save()

        if self.request.FILES:
            for f in self.request.FILES.getlist('complaint_file'):
                ComplaintDocument.objects.create(file=f, complaint=self.object)
        return super(ComplaintFormView, self).form_valid(form)

    def get_success_url(self):
        return reverse(viewname='complaint_app:complaint_list')


class ComplaintDetailView(DetailView):
    template_name = 'complaint_detail.html'
    model = ComplaintModel

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['action_list'] = ActionModel.objects.filter(complaint_id=self.kwargs.get('pk'))
        return context

    # def post(self, request, *args, **kwargs):
    #     status = request.POST['status']
    #     comments = request.POST['comments']
    #     update_remark = ComplaintModel.objects.filter(pk=self.kwargs.get('pk'))
    #     for update in update_remark:
    #         update.status = status
    #         update.comments = comments
    #         if status == 'Completed':
    #             update.solved_date = datetime.datetime.now()
    #             update.solved_by = self.request.user.username
    #         update.save()
    #     return JsonResponse({"status": status, "comments": comments}, status=200)

    # def form_valid(self, form):
    #     obj = form.save(commit=False)
    #     status = form.cleaned_data['status']
    #     comments = form.cleaned_data['comments']
    #     if status == 'completed':
    #         obj.solved_date = datetime.datetime.now()
    #         obj.solved_by = self.request.user.username
    #     obj.save()
    #     return JsonResponse({"status": obj.get_status_display(), "comments": comments }, status=200)

class UpdateRemark(View):

    def post(self, request, *args, **kwargs):
        status = self.request.POST['status']
        comments = self.request.POST['comments']
        update_remark = ComplaintModel.objects.filter(pk=self.kwargs.get('pk'))
        for update in update_remark:
            update.status = status
            update.comments = comments
            if status == 'Completed':
                update.solved_date = datetime.datetime.now()
                update.solved_by = self.request.user.username
            update.save()
        return JsonResponse({"status": status, "comments": comments}, status=200)


def update_remark(request, pk):
    status = request.POST['status']
    comments = request.POST['comments']
    update_remark = ComplaintModel.objects.filter(pk=pk)
    for update in update_remark:
        update.status = status
        update.comments = comments
        if status == 'Completed':
            update.solved_date = datetime.datetime.now()
            update.solved_by = request.user.username
        update.save()
    return JsonResponse({"status": status, "comments": comments}, status=200)


class AboutView(TemplateView):
    template_name = 'about_page.html'


class RegisterView(CreateView):
    template_name = 'register_page.html'
    model = User
    success_url = reverse_lazy('complaint_app:login_page')
    form_class = UserRegisterForm

    def get_context_data(self, **kwargs):
        context = super(RegisterView, self).get_context_data()
        context['user_profile_form'] = UserProfileForm(prefix='user_profile_form')
        if self.request.POST:
            context['user_profile_form'] = UserProfileForm(self.request.POST, prefix='user_profile_form')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        user_profile_form = context['user_profile_form']
        user_obj = form.save()
        if user_profile_form.is_valid():
            user_profile_form.instance.user = user_obj
            user_profile_form.save()
            return super(RegisterView, self).form_valid(form)
        return self.render_to_response(context)


class LoginView(TemplateView):
    template_name = 'login_page.html'

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('complaint_app:complaint_list')
        else:
            messages.error(request, 'Credentials are incorrect..')
            return redirect('complaint_app:login_page')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('complaint_app:login_page')


class UserUpdateView(UpdateView):
    template_name = 'user_profile.html'
    model = User
    form_class = UserUpdateForm
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super(UserUpdateView, self).get_context_data()
        context['user_profile_form'] = UserProfileUpdateForm(prefix='user_profile_form',
                                                             instance=self.object.userprofilemodel)
        if self.request.POST:
            context['user_profile_form'] = UserProfileUpdateForm(self.request.POST, prefix='user_profile_form',
                                                                 instance=self.object.userprofilemodel)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        user_profile_form = context['user_profile_form']
        user_profile_form.save()
        user_data = ComplaintModel.objects.filter(user_id=self.request.user.pk)
        for user in user_data:
            user.created_by = form.cleaned_data['username']
            user.save()
        return super(UserUpdateView, self).form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return super(UserUpdateView, self).form_invalid(form)

    def get_success_url(self):
        return reverse('complaint_app:update_profile', kwargs={'pk': self.kwargs.get('pk')})


@login_required
def chart_testing(request):
    Ahmedabad = UserProfileModel.objects.filter(city='ahmedabad').count()
    Pune = UserProfileModel.objects.filter(city='pune').count()
    Mumbai = UserProfileModel.objects.filter(city='mumbai').count()
    Dehli = UserProfileModel.objects.filter(city='dehli').count()

    myPendingData = ComplaintModel.objects.filter(status='pending').values_list('status').count()
    myWorkInProgressData = ComplaintModel.objects.filter(status='Work in Progress').values_list('status').count()
    myCompletedData = ComplaintModel.objects.filter(status='Completed').values_list('status').count()
    template = loader.get_template('analytics_page.html')

    context = {
        'Ahmedabad': Ahmedabad,
        'Pune': Pune,
        'Mumbai': Mumbai,
        'Dehli': Dehli,
        'myPendingData': myPendingData,
        'myWorkInProgressData': myWorkInProgressData,
        'myCompletedData': myCompletedData,
    }
    return HttpResponse(template.render(context, request))


def generate_pdf(request):
    model = ComplaintModel.objects.all().values()
    # fetch data from complaint model
    for data in model:
        comp_title = data['title']
        comp_description = data['description']
        comp_created_by = data['created_by']
        comp_created_at = data['created_date']
        comp_solved_by = data['solved_by']
        comp_solved_at = data['solved_date']

    responce = HttpResponse(content_type='application/pdf')
    d = datetime.datetime.today().strftime('%y-%m-%d')
    responce['Content-Disposition'] = f'inline; filename ="{d}.pdf"'

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    data = {
        'User Detail': [
            {'address1': request.user.userprofilemodel.address1},
            {'address2': request.user.userprofilemodel.address1},
            {'pin-code': request.user.userprofilemodel.pin_code},
            {'city': request.user.userprofilemodel.city},
        ],
        'Complaint Detail': [
            {'title': comp_title},
            {'description': comp_description},
            {'created_by': comp_created_by},
            {'created_date': comp_created_at},
            {'solved_by': comp_solved_by},
            {'solved_date': comp_solved_at}
        ],
    }

    p.setFont('Helvetica', 16, leading=None)
    p.setFillColorRGB(0.2929, 0.4531, 0.6093)
    p.drawString(260, 800, "Complaint Report")
    p.line(0, 780, 1000, 780)
    p.line(0, 778, 1000, 778)
    x1 = 20
    y1 = 740

    for k, v in data.items():
        p.setFont('Helvetica', 22, leading=None)
        p.drawString(x1, y1, f'{k}')
        for value in v:
            for key, val in value.items():
                p.setFont('Helvetica', 16, leading=None)
                p.drawString(x1, y1 - 20, f"{key}: {val}")
                y1 = y1 - 40

    p.setTitle(f'Report on {d}')
    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    responce.write(pdf)
    return responce


def export_users_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="users.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users Data')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Username', 'First Name', 'Last Name', 'Email Address', ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)  # at 0 row 0 column

        # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    # user_ids = UserProfileModel.objects.filter(user_type='customer').values_list('user__id', flat=True)
    #
    # rows = User.objects.filter(id__in=user_ids).values_list('username', 'first_name', 'last_name', 'email')
    rows = User.objects.filter(userprofilemodel__user_type='customer').values_list('username', 'first_name',
                                                                                   'last_name', 'email')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)

    return response


class ActionCreateView(LoginRequiredMixin, CreateView):
    model = ActionModel
    template_name = 'action_create_form.html'
    fields = []

    def get_context_data(self, **kwargs):
        context = super(ActionCreateView, self).get_context_data(**kwargs)

        queryset = ActionModel.objects.none()
        if self.request.POST:
            action_create_formset = ActionCreateFormset(self.request.POST, queryset=queryset,
                                                        prefix='action_create_formset')
        else:
            action_create_formset = ActionCreateFormset(queryset=queryset,
                                                        prefix='action_create_formset')
        context['action_create_formset'] = action_create_formset
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        action_create_formset = context['action_create_formset']
        if action_create_formset.is_valid():
            for form in action_create_formset:
                form.instance.complaint = ComplaintModel.objects.get(pk=self.kwargs.get('pk'))
                form.instance.save()
        return super(ActionCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('complaint_app:complaint_detail', kwargs={'pk': self.kwargs.get('pk')})


class ActionBulkUpdateView(LoginRequiredMixin, UpdateView):
    model = ActionModel
    template_name = 'action_update_form.html'
    fields = []
    pk_url_kwarg = 'pk_action'

    def get_context_data(self, **kwargs):
        context = super(ActionBulkUpdateView, self).get_context_data(**kwargs)

        queryset = ActionModel.objects.filter(complaint=ComplaintModel.objects.get(pk=self.kwargs.get('pk')))
        if self.request.POST:
            action_update_formset = ActionUpdateFormset(self.request.POST, queryset=queryset,
                                                        prefix='action_update_formset')
        else:
            action_update_formset = ActionUpdateFormset(queryset=queryset,
                                                        prefix='action_update_formset')
        context['action_update_formset'] = action_update_formset
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        action_update_formset = context['action_update_formset']
        print(action_update_formset.errors)
        if action_update_formset.is_valid():
            for action in action_update_formset:
                action.save()
            # action_update_formset.save()
        return super(ActionBulkUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('complaint_app:complaint_detail', kwargs={'pk': self.kwargs.get('pk')})


class DocumentInlineUpdateView(UpdateView):
    model = ComplaintDocument
    template_name = 'document_update.html'
    fields = []
    pk_url_kwarg = 'pk_complaint'

    def get_context_data(self, **kwargs):
        context = super(DocumentInlineUpdateView, self).get_context_data()
        complaint_obj = ComplaintModel.objects.get(pk=self.kwargs.get('pk'))
        if self.request.POST:
            document_inline = DocumentUpdateInlineFormSet(self.request.POST, self.request.FILES,
                                                          instance=complaint_obj,
                                                          prefix='document_inline')
        else:
            document_inline = DocumentUpdateInlineFormSet(instance=complaint_obj, prefix='document_inline')
        context['document_inline'] = document_inline
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        document_inline = context['document_inline']
        with transaction.atomic():
            if document_inline.is_valid():
                print(document_inline.save())
                document_inline.save()
        return super(DocumentInlineUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('complaint_app:complaint_detail', kwargs={'pk': self.kwargs.get('pk')})


class ActionUpdateView(UpdateView):
    model = ActionModel
    fields = []
    template_name = 'action_update.html'
    pk_url_kwarg = 'pk_action'

    def get_context_data(self, **kwargs):
        context = super(ActionUpdateView, self).get_context_data()
        ActionFormset = modelformset_factory(ActionModel, form=ActionForm, extra=0)
        context['action_update_formset'] = ActionFormset(queryset=ActionModel.objects.filter(
            complaint_id=self.kwargs.get('pk')))
        if self.request.POST:
            context['action_update_formset'] = ActionFormset(self.request.POST,
                                                             queryset=ActionModel.objects.filter(
                                                                 complaint_id=self.kwargs.get('pk')))
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        action_update_formset = context['action_update_formset']
        if action_update_formset.is_valid():
            action_update_formset.save()
            print(action_update_formset.save())
        return super(ActionUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('complaint_app:complaint_detail', kwargs={'pk': self.kwargs.get('pk')})
