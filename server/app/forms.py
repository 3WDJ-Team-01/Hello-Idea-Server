from django import forms
from .models import Image

class ImageUpload(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('file',)

        def save(self):
            image = super(ImageUpload, self).save()
            return image