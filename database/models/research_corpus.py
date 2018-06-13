from django.db import models
from database.models.custom_base_model import CustomBaseModel
from database.models.extracted_feature import ExtractedFeature
from database.models.symbolic_music_file import SymbolicMusicFile
from django.contrib.auth.models import User


class ResearchCorpus(CustomBaseModel):
    """A collection of files that can be used in specific empirical studies"""
    title = models.CharField(max_length=200, blank=False)
    features = models.ManyToManyField(ExtractedFeature)
    creators = models.ManyToManyField(User, related_name='created_corpora')
    curators = models.ManyToManyField(User, related_name='curated_corpora')
    files = models.ManyToManyField(SymbolicMusicFile)

    def __str__(self):
        return "{0}".format(self.title)

    class Meta(CustomBaseModel.Meta):
        db_table = 'research_corpus'
        verbose_name_plural = 'Research Corpora'
