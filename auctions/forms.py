from django import forms
from .models import Category


class ListingForm(forms.Form):
    """An form for creating a new listing.
    Fields: title, starting_bid, categorym image_url, description"""

    title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": 'form-control col-12 inset-bx-sha rounded-s',
                "placeholder": "Title"
            }
        )
    )

    starting_bid = forms.FloatField(
        min_value=0.01,
        max_value=9999999.99,
        label="Starting Bid",
        widget=forms.NumberInput(
            attrs={
                "class": 'form-control col-12 inset-bx-sha rounded-s'
            }
        )
    )

    category = forms.ChoiceField(
        label="Category (optional)",
        required=False,
        choices=((None, '- No Category -'),) + tuple(Category.objects.all().order_by("name").values_list()),
        widget=forms.Select(
            attrs={
                "class": 'form-control col-12 inset-bx-sha rounded-s'
            }
        )
    )

    image_url = forms.CharField(
        required=False,
        max_length=300,
        label="Image URL (optional)",
        widget=forms.TextInput(
            attrs={
                "class": 'form-control col-12 inset-bx-sha rounded-s',
                "placeholder":"Optional image URL"
            }
        )
    )

    description = forms.CharField(
        max_length=600,
        label="Description (max 600)",
        widget=forms.Textarea(
            attrs={
                "class": 'form-control col-12 inset-bx-sha rounded-s',
                "placeholder": "Write a description...",
                "resize": "False",
                "rows":"3"
            }
        )
    )


class BidForm(forms.Form):
    """An form for placing a bid on an auction. 
    Fields: bid_amount"""

    bid_amount = forms.FloatField(
        min_value=0.00,
        max_value=9999999.99,
        label="",
        widget=forms.NumberInput(
            attrs={
                "class": 'form-control inset-bx-sha rounded-h',
                "placeholder": 'New bid'
            }
        )
    )


class CommentForm(forms.Form):
    """An form for placing a comment on an auction. 
    Fields: comment"""

    comment = forms.CharField(
        min_length=1,
        max_length=300,
        label="",
        widget=forms.Textarea(
            attrs={
                "class": "form-control col-12 inset-bx-sha rounded-s",
                "rows": "2",
                "placeholder": "Write a comment..."
            }
        )
    )
