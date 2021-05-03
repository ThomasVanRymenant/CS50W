from django import forms

class createPostForm(forms.Form):
    content = forms.CharField(
        max_length=800,
        label="",
        widget=forms.Textarea(
            attrs={
                "class": 'form-control post-textarea',
                "placeholder": "What's happening?",
                "resize": "False",
                "rows":"1"
            }
        )
    )