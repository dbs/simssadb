from database.views.generic_model_viewset import GenericModelViewSet
from database.serializers import MusicalWorkSerializer
from database.models.musical_work import MusicalWork


class MusicalWorkViewSet(GenericModelViewSet):
    queryset = MusicalWork.objects.all().prefetch_related('contributed_to', 'contributors', 'sections',
                                                          'sections__parts')
    serializer_class = MusicalWorkSerializer


