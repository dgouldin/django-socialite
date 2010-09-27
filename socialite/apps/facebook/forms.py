from django import forms

class WallPostForm(forms.Form):
    wall_post = forms.CharField(max_length=144, widget=forms.Textarea(attrs={'cols':'80', 'rows': '2'}))