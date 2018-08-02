from django.http import JsonResponse, HttpResponse
from api.viaf import ViafAPI
from SPARQLWrapper import SPARQLWrapper, JSON
from django.shortcuts import redirect
from django.contrib import messages


def GetVIAFResult(request):
    """
    A function that gets VIAF result from the input text
    :param request:
    :return:
    """
    if request.method == "GET" and 'q' in request.GET:
        value = request.GET['q']
        """Return JSON with suggested VIAF ids and display names."""
        viaf = ViafAPI()

        result = viaf.suggest(value)
    return result, viaf


def ViafComposerSearch(request):
    result, viaf = GetVIAFResult(request)
        # check for empty search result and return empty json response
    if result is None:
        return JsonResponse({'results': []})

    result = [item for item in result
       if item['nametype'] == 'personal']

    return JsonResponse({
        'results': [dict(
            uri=viaf.uri_from_id(item['viafid']),
            id=item['viafid'],
            text=item['displayForm'],
        ) for item in result]
    })


def ViafComposerSearchAutoFill(request):
    """
    A function that parses the result from authority control
    :param request:
    :return:
    """
    result, viaf = GetVIAFResult(request)
    for i in range(len(result)):
        print(result[i]['displayForm'])
    if len(result) > 0:
        for i in range(len(result)):
            if i == 3:
                print('debug')
            result_string = result[i]['displayForm']
            print(result_string)
            if result_string.find('-') == -1: continue # discard data with no date
            uri = viaf.uri_from_id(result[i]['recordID'])
            metadata = [result_string.strip(',') for result_string in result_string.split(' ')]
            for i, item in enumerate(metadata):
                if item.find('-') != -1 and any(char.isdigit() for char in item):  # date must have - with digits
                    # for char in item:  # only keep digits
                    #     if not char.isdigit():
                    #         item = item.replace(char,'')
                    date = item.split('-')
                    break
            if date[0] == '' or date[1] == '': continue # only return person with both birth date and death date

            # the 2 lines of code below will refresh messages
            storage = messages.get_messages(request)
            storage.used = True
            # Pass the context info into messages
            messages.error(request, metadata[0], extra_tags='surname')
            if len(metadata)> 1:
                messages.error(request, ' '.join(map(str, metadata[1:i])), extra_tags='given_name')  # consider
            messages.error(request, date[0]+'-01-01', extra_tags='range_date_birth')
            messages.error(request, date[1]+'-01-01', extra_tags='range_date_death')
            messages.error(request, uri, extra_tags='authority_control_url')
    return redirect('person')


def WikidataComposerSearch(request):

    if request.method == "GET" and 'q' in request.GET:
        value = request.GET['q']
        sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
        sparql.setQuery("""
            SELECT ?item ?label ?date_of_birth ?date_of_death WHERE {
            ?item wdt:P106 wd:Q36834.
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
            ?item rdfs:label ?label.
            FILTER((LANG(?label)) = "en")
            FILTER(CONTAINS(lcase(str(?label)), "%s"))
            OPTIONAL { ?item wdt:P569 ?date_of_birth. }
            OPTIONAL { ?item wdt:P570 ?date_of_death. }
            }
        """ % (value.lower()))

        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()

        # check for empty search result and return empty json response
        if result is None:
            return JsonResponse({'results': []})

        return JsonResponse({
            'results': [dict(
                uri=item["item"]["value"],
                text=item["label"]["value"],
                # birth=item["date_of_birth"]["value"],
                # death=item["date_of_death"]["value"],
            ) for item in result["results"]["bindings"]]
        })