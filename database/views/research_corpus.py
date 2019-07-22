from django.views.generic import DetailView, ListView
from database.models import ResearchCorpus
from extra_views import SearchableListMixin


class ResearchCorpusDetailView(DetailView):
    model = ResearchCorpus
    context_object_name = "research_corpus"
    template_name = "detail.html"


class ResearchCorpusListView(SearchableListMixin, ListView):
    model = ResearchCorpus
    search_fields = ["title"]
    queryset = ResearchCorpus.objects.order_by("title")
    paginate_by = 100
    template_name = "list.html"
