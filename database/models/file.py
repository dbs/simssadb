"""Defines a File model"""
from typing import List
import os
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import QuerySet
from database.models.custom_base_model import CustomBaseModel


class File(CustomBaseModel):
    """A file containing or representing music.
    Can be a Symbolic Music File, Image, Text or Audio.

    Attributes
    ----------
    file_type : models.CharField
        The type of this file (Symbolic Music, Image, Text or Audio)

    file_format: models.CharField
        The format of this file

    version: models.CharField
        The version of the encoding schema i.e. MEI 2.0

    encoding_date: modelsDateTimeField
        The date the File was encoded

    licensing_info: models.TextField
        Any licensing information related to this file

    encoding_workflow: models.ForeignKey
        A reference to the Encoding Workflow of this File

    validation_workflow: models.ForeignKey
        A reference to the Validation Workflow of this File

    extra_metadata: postgres.fields.JSONField
        Any extra metadata associated with this File

    instantiates: models.ForeignKey
        The SourceInstantiation manifested by this File

    file : models.FileField
        The path to the actual file stored on disk

    feature_files: models.models.fields.related_descriptors.ReverseManyToOneDescriptor
        Reference to feature files that contain features extracted from this File
    
    features: models.models.fields.related_descriptors.ReverseManyToOneDescriptor
        Reference to the ExtractedFeatures extracted from this File
    
    in_corpora: models.fields.related_descriptors.ManyToManyDescriptor
        References to Research Corpora that contain this file
    """

    TYPES = (
        ("sym", "Symbolic Music"),
        ("txt", "Text"),
        ("img", "Image"),
        ("audio", "Audio"),
    )
    file_type = models.CharField(
        default="sym", max_length=10, choices=TYPES, help_text="The type of the file"
    )
    file_format = models.CharField(max_length=10, help_text="The format of the file")
    version = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="The version of the encoding schema i.e. MEI 2.0",
    )
    encoding_date = models.DateTimeField(
        null=True, blank=True, help_text="The date the File was encoded"
    )
    licensing_info = models.TextField(
        null=True,
        blank=True,
        help_text="Any licensing information related to this file",
    )
    encoding_workflow = models.ForeignKey(
        "EncodingWorkflow",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The Encoding Workflow of this File",
    )
    validation_workflow = models.ForeignKey(
        "ValidationWorkflow",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The Validation Workflow of this File",
    )
    extra_metadata = JSONField(
        null=True, blank=True, help_text="Any extra metadata associated with the File"
    )
    instantiates = models.ForeignKey(
        "SourceInstantiation",
        related_name="files",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        help_text="The SourceInstantiation manifested by this File",
    )
    file = models.FileField(upload_to="user_files/", help_text="The actual file")

    class Meta(CustomBaseModel.Meta):
        db_table = "files"
        verbose_name_plural = "Files"

    def __str__(self) -> str:
        return os.path.basename(self.file.name)

    @property
    def histograms(self) -> QuerySet:
        """Returns the features of this file that are histograms
        
        Histograms are features with more than one dimension

        Returns
        -------
        histograms: QuerySet
            A QuerySet of features with more than one dimension
        """
        return self.features.filter(instance_of_feature__dimensions__gt=1)

    @property
    def scalar_features(self) -> QuerySet:
        """Returns the features of this file that are scalar features
        
        Scalar features are features with only one dimension

        Returns
        -------
        scalars: QuerySet
            A QuerySet of features with exactly one dimension
        """
        return self.features.filter(instance_of_feature__dimensions=1)
