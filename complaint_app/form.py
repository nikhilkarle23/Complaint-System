from django import forms
from django.contrib.auth.models import User
from django.forms import ClearableFileInput, inlineformset_factory, BaseInlineFormSet, modelformset_factory, \
    formset_factory

from complaint_app.models import UserProfileModel, ComplaintModel, ActionModel, ComplaintDocument
from django.contrib.auth.forms import UserCreationForm


class UserRegisterForm(UserCreationForm):
    email = forms.EmailInput()

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        )

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfileModel
        fields = (
            'phone_number',
            'address1',
            'address2',
            'pin_code',
            'city',
            'user_type',
        )

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailInput()

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
        )

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfileModel
        fields = (
            'phone_number',
            'address1',
            'address2',
            'pin_code',
            'city',
        )

class ComplaintForm(forms.ModelForm):
    complaint_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = ComplaintModel
        fields = (
            'title',
            'description',
            'complaint_file',
        )
        widgets = {
            'complaint_file': ClearableFileInput(attrs={'multiple': True}),
        }

class ActionForm(forms.ModelForm):
    class Meta:
        model = ActionModel
        fields = (
            'action',
        )

class ComplaintDocForm(forms.ModelForm):
    class Meta:
        model = ComplaintDocument
        fields = (
            'file',
        )

ActionInlineFormSet = inlineformset_factory(ComplaintModel, ActionModel, ActionForm, extra=1,
                                            widgets={'action': forms.Textarea(attrs={'rows': 2})})

DocumentUpdateInlineFormSet = inlineformset_factory(ComplaintModel, ComplaintDocument, form=ComplaintDocForm,
                                                    extra=0, can_delete=False)

ActionCreateFormset = modelformset_factory(ActionModel, form=ActionForm, extra=1,
                                           widgets={'action': forms.Textarea(attrs={'rows': 2})})
ActionUpdateFormset = modelformset_factory(ActionModel, form=ActionForm, extra=0,
                                           widgets={'action': forms.Textarea(attrs={'rows': 2})})

class UpdateStatusForm(forms.ModelForm):
    comments = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = ComplaintModel
        fields = (
            'status',
            'comments'
        )
