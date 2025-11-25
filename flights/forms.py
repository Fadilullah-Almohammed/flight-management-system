from django import forms
from .models import Flight
from django.core.exceptions import ValidationError


class NewFlightForm(forms.ModelForm):

    class Meta:

        model = Flight
        fields = [
            'flight_number',
            'departure_datetime',
            'arrival_datetime',
            'economy_price',
            'business_price',
            'first_class_price',
            'departure_airport',
            'arrival_airport',
            'aircraft'
        ]

        widgets = {
            'departure_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'arrival_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name ,field in self.fields.items():

            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })

            self.fields['aircraft'].widget.attrs.update({'class': 'form-select'})
            self.fields['departure_airport'].widget.attrs.update({'class': 'form-select'})
            self.fields['arrival_airport'].widget.attrs.update({'class': 'form-select'})

            self.fields['aircraft'].empty_label = 'Select Aircraft Type'
            self.fields['departure_airport'].empty_label = 'Select Departure Airport'
            self.fields['arrival_airport'].empty_label = 'Select Destination Airport'

    
    def clean(self):
        """
        Override clean() method to validate model
        """

        cleaned_data = super().clean()
        flight = Flight(**cleaned_data)

        try:
            flight.check_flight()
        except ValidationError as e:
            raise forms.ValidationError(e.message)
        
        return cleaned_data
    
    