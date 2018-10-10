"""Define a SymbolicMusicFile model"""
import os

from django.db import models
from django.db.models import QuerySet

from database.models.file import File


class SymbolicMusicFile(File):
    """A manifestation of a SourceInstantiation as an digital symbolic music file.

    Manifests one and only one SourceInstantiation.

    Generated by an Encoder and validated against a SourceInstantiation by a
    Validator.

    Attributes
    ----------
    SymbolicMusicFile.file_type : models.CharField
        The format of this SymbolicMusicFile

    SymbolicMusicFile.file_size : models.PositiveIntegerField
        The size of the this SymbolicMusicFile in bytes

    SymbolicMusicFile.version : models.CharField
        The version of the encoding schema of this SymbolicMusicFile

    SymbolicMusicFile.encoding_date : models.DateTimeField
        The date this SymbolicMusicFile was encoded

    SymbolicMusicFile.encoded_with : models.ForeignKey
        A reference to the Encoder of this SymbolicMusicFile

    SymbolicMusicFile.validated_by : models.ForeignKey
        A reference to the Validator of this SymbolicMusicFile

    SymbolicMusicFile.extra_metadata : django.contrib.postgres.fields.JSONField
        Any extra metadata associated with this SymbolicMusicFile

    SymbolicMusicFile.manifests : ForeignKey
        The SourceInstantiation manifested by this SymbolicMusicFile

    SymbolicMusicFile.file : models.FileField
        The path to the actual file stored on disk

    SymbolicMusicFile.in_corpora : models.ManyToManyRel
        References to the ResearchCorpora that contain this SymbolicMusicFile

    SymbolicMusicFile.features : models.ManyToOneRel
        References to the ExtractedFeatures of this SymbolicMusicFile

    SymbolicMusicFile.instruments_used : models.ManyToManyRel
        References to the Instruments declared in this SymbolicMusicFile

    See Also
    --------
    database.models.File : The super class of SymbolicMusicFile
    database.models.CustomBaseModel
    database.models.SourceInstantiation
    database.models.Encoder
    database.models.Validator
    """
    instruments_used = models.ManyToManyField('Instrument',
                                              related_name='sym_files',
                                              help_text='The Instruments used '
                                                        'in this Symbolic '
                                                        'File',
                                              blank=True)
    manifests = models.ForeignKey('SourceInstantiation',
                                  related_name='manifested_by_sym_files',
                                  on_delete=models.CASCADE,
                                  null=False,
                                  help_text='The SourceInstantiation '
                                            'manifested by this '
                                            'Symbolic File')
    file = models.FileField(upload_to='symbolic_music/',
                            help_text='The actual file')

    class Meta:
        db_table = 'symbolic_music_file'

    def __str__(self):
        filename = os.path.basename(self.file.name)
        return "{0}".format(filename)

    @property
    def one_dimensional_features(self) -> QuerySet:
        """Return all the one dimensional features of this file"""
        return self.features.exclude(value__len__gt=1)

    @property
    def histograms(self) -> QuerySet:
        """Return all histograms (multi-dimensional features)"""
        return self.features.exclude(value__len__lte=1)
