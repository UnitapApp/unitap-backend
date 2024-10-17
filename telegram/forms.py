from django import forms


class BroadcastMessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea, label="Message")
