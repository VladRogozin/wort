from django import forms
from .models import Playlist, Word

# Просто утилита, не наследуется от forms.Form
class BootstrapFormMixin:
    def apply_bootstrap_classes(self):
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class PlaylistForm(forms.ModelForm, BootstrapFormMixin):
    class Meta:
        model = Playlist
        fields = ['title', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap_classes()

class WordForm(forms.ModelForm, BootstrapFormMixin):
    class Meta:
        model = Word
        fields = ['word', 'translation', 'details', 'context', 'playlists']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap_classes()


class WordBulkUploadForm(forms.Form):
    playlist = forms.ModelChoiceField(queryset=Playlist.objects.all(), label="Плейлист")
    json_data = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 15}),
        label="JSON-данные со словами",
        help_text="Вставьте JSON-массив объектов со словами"
    )


