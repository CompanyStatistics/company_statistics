from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
import django.forms as forms

from .models import CSUser, CSUserProfile


class CSUserLoginForm(AuthenticationForm):
    class Meta:
        model = CSUser
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        super(CSUserLoginForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class CSUserEditForm(UserChangeForm):
    class Meta:
        model = CSUser
        fields = (
            'username',
            'first_name',
            'email',
            'password'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = ''
            if field_name == 'password':
                field.widget = forms.HiddenInput()


class CSUserProfileEditForm(forms.ModelForm):
    class Meta:
        model = CSUserProfile
        fields = (

        )

    def __init__(self, *args, **kwargs):
        super(CSUserProfileEditForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
