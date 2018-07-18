from django.db import models
from database.models.custom_base_model import CustomBaseModel
from django.contrib.postgres.fields import DateRangeField, ArrayField
from database.models.geographic_area import GeographicArea


# TODO: put this someplace that all models can use
def clean_date(date_range):
    date = None
    if date_range is not None:
        if date_range.lower is not None and date_range.upper is not None:
            if date_range.lower.year == date_range.upper.year:
                date = str(date_range.upper.year)
            else:
                date = str(date_range.lower.year) + '-' + str(date_range.upper.year)
        if date_range.lower is not None and date_range.upper is None:
            date = str(date_range.lower.year)
        if date_range.lower is None and date_range.upper is not None:
            date = str(date_range.upper.year)
    return date


class Person(CustomBaseModel):
    """Represents a real world person that contributed to a musical work"""
    given_name = models.CharField(max_length=100, null=False, blank=False,
                                  help_text='The given name of this Person',
                                  default="")
    surname = models.CharField(max_length=100, null=False, blank=True,
                               default="",
                               help_text='The surname of this Person, '
                                         'leave blank if it is unknown')
    range_date_birth = DateRangeField(null=True,
                                      help_text='The birth year of this '
                                                'Person. If certain, put the '
                                                'beginning and end of the '
                                                'range as the same. If '
                                                'uncertain, enter a range '
                                                'that is generally accepted')
    range_date_death = DateRangeField(null=True,
                                      help_text='The death year of this '
                                                'Person. If certain, put the '
                                                'beginning and end of the '
                                                'range as the same. If '
                                                'uncertain, enter a range '
                                                'that is generally accepted')
    birth_location = models.ForeignKey(GeographicArea, null=True,
                                       on_delete=models.SET_NULL, blank=True,
                                       related_name='birth_location_of',
                                       help_text='The birth location of this '
                                                 'Person. Choose the most '
                                                 'specific possible.')
    death_location = models.ForeignKey(GeographicArea, null=True,
                                       on_delete=models.SET_NULL, blank=True,
                                       related_name='death_location_of',
                                       help_text='The death location of this '
                                                 'Person. Choose the most '
                                                 'specific possible.')
    authority_control_url = models.URLField(null=True, blank=True,
                                            help_text='An URI linking to an '
                                                      'authority control '
                                                      'description of this '
                                                      'Person')
    authority_control_key = models.IntegerField(unique=True, blank=True,
                                                null=True,
                                                help_text='The identifier of '
                                                          'this Person '
                                                          'in the authority '
                                                          'control')
    parts_contributed_to = models.ManyToManyField(
            'Part',
            through='ContributedTo',
            through_fields=('person', 'contributed_to_part'),
            help_text='The Parts that this Person contributed to'
    )
    sections_contributed_to = models.ManyToManyField(
            'Section',
            through='ContributedTo',
            through_fields=('person', 'contributed_to_section'),
            help_text='The Sections that this Person contributed to'
    )
    works_contributed_to = models.ManyToManyField(
            'MusicalWork',
            through='ContributedTo',
            through_fields=('person', 'contributed_to_work'),
            help_text='The Musical Works that this Person contributed to'
    )

    @staticmethod
    def __get_contributions_by_role(queryset, role):
        """
        Gets the Works/Sections/Parts this Person contributed to in a certain role

        :param queryset: the queryset of relationships
        :param role: The role of this Person in the ContributedTo relationship
        :return: A dictionary containing the following members
            `role`: the role of the Person, same as what was passed
            `works`: a set of MusicalWorks
            `sections`: a set of Sections
            `parts`: a set of Parts
        """
        works = set()
        sections = set()
        parts = set()
        role_dict_name = role.lower()
        for relationship in queryset.iterator():
            if relationship.role == role:
                if relationship.contributed_to_work:
                    works.add(relationship.contributed_to_work)
                if relationship.contributed_to_section:
                    sections.add(relationship.contributed_to_section)
                if relationship.contributed_to_part:
                    parts.add(relationship.contributed_to_part)

        return_dict = {'role':     role_dict_name,
                       'works':    works,
                       'sections': sections,
                       'parts':    parts}
        return return_dict

    @staticmethod
    def __composed(queryset):
        """Get all the Works/Sections/Parts that this Person composed"""
        return Person.__get_contributions_by_role(queryset, 'COMPOSER')

    @staticmethod
    def __arranged(queryset):
        """Get all the Works/Sections/Parts that this Person arranged"""
        return Person.__get_contributions_by_role(queryset, 'ARRANGER')

    @staticmethod
    def __authored(queryset):
        """Get all the Works/Sections/Parts that this Person authored"""
        return Person.__get_contributions_by_role(queryset, 'AUTHOR')

    @staticmethod
    def __transcribed(queryset):
        """Get all the Works/Sections/Parts that this Person transcribed"""
        return Person.__get_contributions_by_role(queryset, 'TRANSCRIBER')

    @staticmethod
    def __performed(queryset):
        """Get all the Works/Sections/Parts that this Person performed"""
        return Person.__get_contributions_by_role(queryset, 'PERFORMER')

    @staticmethod
    def __improvised(queryset):
        """Get all the Works/Sections/Parts that this Person improvised"""
        return Person.__get_contributions_by_role(queryset, 'IMPROVISER')

    def __str__(self):
        if self.surname and self.given_name:
            return "{0}, {1}".format(self.surname, self.given_name)
        if self.given_name and not self.surname:
            return '{0}'.format(self.given_name)
        if self.surname and not self.given_name:
            return '{0}'.format(self.surname)

    def __get_life_span(self):
        if self.range_date_birth and self.range_date_death:
            return ' (' + clean_date(self.range_date_birth) + '-' + clean_date(self.range_date_death) + ')'
        else:
            return ""

    def __badge_name(self):
        if self.__count_works() > 1:
            return 'musical works'
        else:
            return 'musical work'

    def prepare_summary(self):
        summary = {'display': self.__str__() + self.__get_life_span(),
                   'url': self.get_absolute_url(),
                   'badge_count': self.__count_works(),
                   'badge_name': self.__badge_name(),
                   'sections': self.__count_sections()
                   }
        return summary
        
    class Meta(CustomBaseModel.Meta):
        db_table = 'person'
