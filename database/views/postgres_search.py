from typing import List, Optional, Dict
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Count, F, Q, QuerySet
from django.http import Http404, HttpResponse, HttpRequest
from django.views.generic.base import TemplateView
from database.forms.feature_search_form import FeatureSearchForm
from django.core.paginator import Paginator
from database.forms.facet_search_form import FacetSearchForm
from database.models import (
    ExtractedFeature,
    FeatureType,
    MusicalWork,
    Section,
    File,
)
from database.views.facets import (
    Facet,
    TypeFacet,
    StyleFacet,
    ComposerFacet,
    FileFormatFacet,
    InstrumentFacet,
    SacredFacet,
)


class FeatureFilter(object):
    def __init__(self, code: str, min_val: int, max_val: int) -> None:
        self.code = code
        self.min_val = min_val
        self.max_val = max_val


class PostgresSearchView(TemplateView):
    template_name = "search/pg_search.html"
    http_method_names = ["get"]
    feature_types = FeatureType.objects.exclude(dimensions__gt=1)
    codes = feature_types.values_list("code", flat=True)
    paginate_by = 10
    facet_name_list = [
        "types",
        "styles",
        "composers",
        "instruments",
        "file_formats",
        "sacred",
    ]

    def read_request_facets(
        self, request: HttpRequest, facet_name_list: List[str]
    ) -> List[Facet]:
        facets: List[Facet] = []
        for facet_name in facet_name_list:
            facet: Facet
            selected = request.GET.getlist(facet_name)
            if facet_name == "types":
                facet = TypeFacet(selected=selected)
            elif facet_name == "styles":
                facet = StyleFacet(selected=selected)
            elif facet_name == "composers":
                facet = ComposerFacet(selected=selected)
            elif facet_name == "instruments":
                facet = InstrumentFacet(selected=selected)
            elif facet_name == "file_formats":
                facet = FileFormatFacet(selected=selected)
            elif facet_name == "sacred":
                facet = SacredFacet(selected=selected)
            facets.append(facet)
        return facets

    def is_content_search_on(self, request: HttpRequest, codes: List[str]) -> bool:
        if any(key in codes for key in request.GET):
            return True
        else:
            return False

    def keyword_search(self, keyword: str) -> QuerySet:
        query = SearchQuery(keyword)
        rank_annotation = SearchRank(F("search_document"), query)
        queryset = (
            MusicalWork.objects.annotate(rank=rank_annotation)
            .filter(search_document=query)
            .order_by("-rank")
        )
        return queryset

    def make_facet_query(self, facet: Facet) -> Q:
        q_objects = Q()
        for selection in facet.selected:
            kwarg = {facet.lookup: selection}
            q_objects |= Q(**kwarg)
        return q_objects

    def facet_filter(self, queryset: QuerySet, facets: List[Facet]) -> QuerySet:
        querys = Q()
        for facet in facets:
            querys &= self.make_facet_query(facet)
        return queryset.filter(querys)

    def read_request_feature_filters(
        self, request: HttpRequest, codes: List[str]
    ) -> List[FeatureFilter]:
        feature_filters = []
        for key, value in request.GET.lists():
            if key in codes:
                code = key
                min_val, max_val = value[0].split(",")
                feature_filter = FeatureFilter(
                    code=code, min_val=min_val, max_val=max_val
                )
                feature_filters.append(feature_filter)
        return feature_filters

    def single_feature_filter(self, feature_filter: FeatureFilter) -> Q:
        ids = ExtractedFeature.objects.filter(
            instance_of_feature__code=feature_filter.code,
            value__0__gte=feature_filter.min_val,
            value__0__lte=feature_filter.max_val,
        ).values_list("feature_of_id", flat=True)
        return Q(id__in=ids)

    def content_search(
        self, request: HttpRequest, codes: List[str], files: QuerySet
    ) -> QuerySet:
        feature_filters = self.read_request_feature_filters(request, codes)
        q_feature_filters = Q()
        for feature_filter in feature_filters:
            q_feature_filters &= self.single_feature_filter(feature_filter)
        return files.filter(q_feature_filters)

    def filter_works_with_no_files(self, works: QuerySet, files: QuerySet) -> QuerySet:
        return works.filter(
            Q(source_instantiations__files__in=files)
            | Q(sections__source_instantiations__files__in=files)
        ).distinct()

    def get_context_data(
        self,
        works: QuerySet,
        file_ids: List[int],
        facet_form: FacetSearchForm,
        feature_form: FeatureSearchForm,
        content_search_on: bool,
        page: int,
        **kwargs
    ) -> Dict:
        context = super(PostgresSearchView, self).get_context_data(**kwargs)
        context["paginator"] = Paginator(works, self.paginate_by)
        context["is_paginated"] = True
        context["works"] = context["paginator"].get_page(page)
        context["facet_form"] = facet_form
        context["feature_form"] = feature_form
        context["file_ids"] = file_ids
        context["content_search_on"] = content_search_on

        return context

    def get(self, request: HttpRequest) -> HttpResponse:
        codes = self.codes
        feature_types = self.feature_types
        facet_name_list = self.facet_name_list

        q = request.GET.get("q")
        page = request.GET.get("page")
        if not page:
            page = 1
        facets = self.read_request_facets(request, facet_name_list)
        content_search_on = self.is_content_search_on(request, codes)
        works = self.facet_filter(self.keyword_search(q), facets)
        sections = Section.objects.filter(musical_work__in=works)
        files = File.objects.filter(
            Q(instantiates__work__in=works) | Q(instantiates__sections__in=sections)
        )

        if content_search_on:
            files = self.content_search(request, codes, files)
            works = self.filter_works_with_no_files(works, files)

        work_ids = works.values_list("id", flat=True)
        file_ids = files.values_list("id", flat=True)

        facet_form = FacetSearchForm(data=request.GET, work_ids=work_ids, facets=facets)
        feature_form = FeatureSearchForm(
            feature_types=feature_types, file_ids=file_ids, data=request.GET
        )

        context = self.get_context_data(
            works, file_ids, facet_form, feature_form, content_search_on, page
        )
        return self.render_to_response(context)
