from django import forms

from .. import models


class EntityDetailForm(forms.ModelForm):
    entity_uuid = forms.ChoiceField(label="Entity (current only)")

    class Meta:
        model = models.EntityDetail
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_entities = models.Entity.objects.filter(is_current=True)
        choices = [
            (str(e.uuid), f"(uuid:{e.uuid}) - {e.display_name}")
            for e in current_entities
        ]
        self.fields['entity_uuid'].choices = choices