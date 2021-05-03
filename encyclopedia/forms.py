from django import forms

class NewEntryForm(forms.Form):
    title = forms.CharField(
      widget=forms.TextInput(
        attrs={
          "class": 'form-control col-12 col-sm-10'
        }
      )
    )
    content = forms.CharField(widget=forms.Textarea(attrs={"class":'form-control col-12 col-sm-10'}))

class EditEntryForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={"class":'form-control col-12 col-sm-10',"rows":'17'},),label="")