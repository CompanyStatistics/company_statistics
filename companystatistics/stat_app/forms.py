from django import forms

from .models import Stat, StatTitle


class StatForm(forms.ModelForm):

    class Meta:
        model = Stat
        fields = ('amount', 'date',)


class StatTitleForm(forms.ModelForm):

    class Meta:
        model = StatTitle
        fields = ('title', 'overview',)
