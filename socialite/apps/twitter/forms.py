from django import forms

class TweetForm(forms.Form):
    tweet = forms.CharField(max_length=144, widget=forms.Textarea(attrs={'cols':'80', 'rows': '2'}))