from django import forms

class CSVUploadForm(forms.Form):
    number = forms.CharField(
        max_length=8,
        min_length=8,
        widget=forms.NumberInput(attrs={
            'placeholder': 'KRA PIN',
            'class': 'border px-6 py-2 rounded-md w-full focus:outline-none focus:ring-2 focus:ring-[#002147]'
        })
    )
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'accept': '.csv',
            'class': 'hidden',
            'id': 'csv-file'
        })
    )
