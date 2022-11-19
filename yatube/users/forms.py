from django import forms
from django.contrib.auth.forms import UserCreationForm
from posts.models import User

from .models import Contact


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('name', 'email', 'subject', 'body')

    def clean_subject(self):
        data = self.cleaned_data['subject']

        if 'спасибо' not in data.lower():
            raise forms.ValidationError(
                'Вы обязательно должны нас поблагодарить!'
            )
        return data
