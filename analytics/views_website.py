from pyramid.view import view_config
from pyramid.response import Response
import pyramid.httpexceptions as exc
import datetime

from dogpile.cache import make_region

from analytics import utils

cache_region = make_region(name='views_website_cache')

def check_session(wrapped):
    """
        Decorator to check and update session attributes.
    """

    def check(request, *arg, **kwargs):
        collection = request.GET.get('collection', None)
        journal = request.GET.get('journal', None)
        document = request.GET.get('document', None)
        range_start = request.GET.get('range_start', None)
        range_end = request.GET.get('range_end', None)
        locale = request.GET.get('_LOCALE_', request.locale_name)

        if journal == 'clean' and 'journal' in request.session:
            del(request.session['journal'])
            journal = None
            if 'document' in request.session:
                del(request.session['document'])
                document = None

        if document == 'clean' and 'document' in request.session:
            del(request.session['document'])
            document = None


        session_collection = request.session.get('collection', None)
        session_journal = request.session.get('journal', None)
        session_document = request.session.get('document', None)
        session_range_start = request.session.get('range_start', None)
        session_range_end = request.session.get('range_end', None)
        session_locale = request.session.get('_LOCALE_', None)

        if collection and collection != session_collection:
            request.session['collection'] = collection
            if 'journal' in request.session:
                del(request.session['journal'])
        elif not session_collection:
            request.session['collection'] = 'scl'

        if journal and journal != session_journal:
            request.session['journal'] = journal

        if document and document != session_document:
            request.session['document'] = document
            request.session['journal'] = document[1:10]

        if range_start and range_start != session_range_start:
            request.session['range_start'] = range_start

        if range_end and range_end != session_range_end:
            request.session['range_end'] = range_end

        if locale and locale != session_locale:
            request.session['_LOCALE_'] = locale

        return wrapped(request, *arg, **kwargs)

    check.__doc__ = wrapped.__doc__

    return check


def base_data_manager(wrapped):
    """
        Decorator to load common data used by all views
    """

    @check_session
    def wrapper(request, *arg, **kwargs):

        @cache_region.cache_on_arguments()
        def get_data_manager(collection, journal, document, range_start, range_end):
            code = document or journal or collection
            data = {}
            if document:
                data['selected_document'] = request.articlemeta.document(document, collection)
                data['selected_document_code'] = document
                journal = document[1:10]

            collections = request.articlemeta.certified_collections()
            journals = request.articlemeta.collections_journals(collection)
            selected_journal = journals.get(journal, None)
            selected_journal_code = journal if journal in journals else None

            today = datetime.datetime.now()
            y3 = today - datetime.timedelta(365*3)
            y2 = today - datetime.timedelta(365*2)
            y1 = today - datetime.timedelta(365*1)

            data.update({
                'collections': collections,
                'selected_code': code,
                'selected_journal': selected_journal,
                'selected_journal_code': selected_journal_code,
                'selected_collection': collections[collection],
                'selected_collection_code': collection,
                'journals': journals,
                'range_start': range_start,
                'range_end': range_end,
                'today': today.isoformat()[0:10],
                'y3': y3.isoformat()[0:10],
                'y2': y2.isoformat()[0:10],
                'y1': y1.isoformat()[0:10]
            })

            return data

        collection_code = request.session.get('collection', None)
        journal_code = request.session.get('journal', None)
        range_end = request.session.get('range_end', datetime.datetime.now().isoformat()[0:10])
        range_start = request.session.get('range_start', (datetime.datetime.now() - datetime.timedelta(365*3)).isoformat()[0:10])
        document_code = utils.REGEX_ARTICLE.match(request.session.get('document', ''))
        if document_code:
            document_code = document_code.string

        data = get_data_manager(collection_code, journal_code, document_code, range_start, range_end)
        data['locale'] = request.session.get('_LOCALE_', request.locale_name)
        setattr(request, 'data_manager', data)

        return wrapped(request, *arg, **kwargs)

    wrapper.__doc__ = wrapped.__doc__

    return wrapper

@view_config(route_name='index_web', renderer='templates/website/home.mako')
@base_data_manager
def index(request):
    data = request.data_manager
    data['page'] = 'home'

    return data


@view_config(route_name='faq_web', renderer='templates/website/faq.mako')
@base_data_manager
def faq(request):

    data = request.data_manager
    data['page'] = 'faq'

    return data


@view_config(route_name='accesses_list_journals_web', renderer='templates/website/access_list_journals.mako')
@base_data_manager
def accesses_list_journals(request):

    data = request.data_manager
    data['page'] = 'accesses'

    data['aclist'] = request.accessstats.list_journals(
        data['selected_code'],
        data['selected_collection_code'],
        data['range_start'],
        data['range_end']
    )

    return data


@view_config(route_name='accesses_list_issues_web', renderer='templates/website/access_list_issues.mako')
@base_data_manager
def accesses_list_issues(request):

    data = request.data_manager
    data['page'] = 'accesses'

    data['aclist'] = request.accessstats.list_issues(
        data['selected_code'],
        data['selected_collection_code'],
        data['range_start'],
        data['range_end']
    )

    return data


@view_config(route_name='accesses_list_articles_web', renderer='templates/website/access_list_articles.mako')
@base_data_manager
def accesses_list_articles(request):

    data = request.data_manager
    data['page'] = 'accesses'

    data['aclist'] = request.accessstats.list_articles(
        data['selected_code'],
        data['selected_collection_code'],
        data['range_start'],
        data['range_end']
    )

    return data


@view_config(route_name='accesses_web', renderer='templates/website/accesses.mako')
@base_data_manager
def accesses(request):

    data = request.data_manager
    data['page'] = 'accesses'

    return data

@view_config(route_name='publication_journal_web', renderer='templates/website/publication_journal.mako')
@base_data_manager
def publication_journal(request):

    data = request.data_manager
    data['page'] = 'publication'

    return data

@view_config(route_name='publication_article_web', renderer='templates/website/publication_article.mako')
@base_data_manager
def publication_article(request):

    data = request.data_manager
    data['page'] = 'publication'

    return data