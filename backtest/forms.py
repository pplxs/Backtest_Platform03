from django import forms
from django_ace import AceWidget

class CodeForm(forms.Form):
    code = forms.CharField(widget=AceWidget(
        mode='python',  # try for example "python"
        theme='monokai',  # try for example "twilight"
        wordwrap=False,
        width="500px",
        height="5px",
        minlines=None,
        maxlines=None,
        showprintmargin=True,
        showinvisibles=False,
        usesofttabs=True,
        tabsize=None,
        fontsize=None,
        toolbar=True,
        readonly=False,
        showgutter=True,  # To hide/show line numbers
        behaviours=True,  # To disable auto-append of quote when quotes are entered
    ))