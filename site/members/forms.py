from django import forms

from members.models import Player, Venue, Committee
from members.validators import validate_policy_date

from crispy_forms.helper import FormHelper


class DateInput(forms.DateInput):
    input_type = 'date'


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = [
            'firstname',
            'lastname',
            'dob',
            'email',
            'phone',
            'address',
            'umpire_accreditation',
            'joined',
            'media_release',
            'media_release_date',
            'vanda_policy',
            'vanda_policy_date'
        ]
        widgets = {
            'dob': DateInput(),
            'joined': DateInput(),
            'media_release_date': DateInput(),
            'vanda_policy_date': DateInput()
        }

    def __init__(self, *args, **kwargs):
        super(PlayerForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper

    def clean(self):
        cleaned_data = super(PlayerForm, self).clean()

        media_release = cleaned_data.get('media_release', '')
        media_release_date = cleaned_data.get('media_release_date', '')
        validate_policy_date(
            media_release,
            media_release_date,
            "Media Release"
        )

        vanda_policy = cleaned_data.get('vanda_policy', '')
        vanda_policy_date = cleaned_data.get('vanda_policy_date', '')
        validate_policy_date(
            vanda_policy,
            vanda_policy_date,
            "Violence and Agression Policy"
        )

        return cleaned_data


class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = [
            'name',
            'address',
            'tables',
            'phone',
            'email',
            'contact_name'
        ]

    def __init__(self, *args, **kwargs):
        super(VenueForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper


class CommitteeForm(forms.ModelForm):
    class Meta:
        model = Committee
        fields = [
            'president',
            'vice_president',
            'treasurer',
            'statistician',
            'secretary',
            'assistant_secretary',
            'start_date',
            'end_date'
        ]
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput()
        }
