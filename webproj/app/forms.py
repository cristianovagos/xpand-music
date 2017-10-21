from django import forms

class SearchForm(forms.Form):
    searchCriteria = forms.CharField(
        widget=forms.TextInput(
            attrs = {
                'class':'form-control',
                'placeholder': 'Search...'
            })
            ,max_length=100
    )

class CommentForm(forms.Form):
    comment = forms.CharField(
        widget=forms.Textarea(
            attrs = {
                'placeholder': 'Type your message',
                'rows': 5,
                'cols': 50
            })
    )