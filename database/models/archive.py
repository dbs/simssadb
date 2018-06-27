from django.db import models
from database.models.custom_base_model import CustomBaseModel
from database.models.collection_of_sources import CollectionOfSources
from database.models.institution import Institution


class Archive(CustomBaseModel):
    """
    A location where Sources and Collections of Sources are stored

    e.g: A database or a library
    """
    name = models.CharField(max_length=200, blank=False, null=False)
    collections = models.ManyToManyField(CollectionOfSources,
                                         related_name='in_archive')

    institution = models.ForeignKey(Institution, null=True,
                                    on_delete=models.SET_NULL)

    def __str__(self):
        return "{0}".format(self.name)

    class Meta(CustomBaseModel.Meta):
        db_table = 'archive'
