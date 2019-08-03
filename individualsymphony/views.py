import logging
import re

from .utils import create_ql, create_rr, eval_genre_corr, eval_bfpt
from .forms import BFPTForm
from .models import RecommendationResults
from .models import GenreSuggestions
from .models import SongGenreSuggestion
from django.utils import translation
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.http import QueryDict
from website.settings import DEBUG
from website.settings import LANGUAGES
from website.settings import NUMBER_OF_RECOMMENDATIONS


logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def home(request):
    return render(request, 'individualsymphony/home.html')


@require_http_methods(["GET", "POST"])
def evaluate(request):
    if (request.method == 'GET'):
        return redirect('/')
        
    age_group = str(request.POST.get('age_group', -1))
    openness = float(request.POST.get('openness', -1))
    agreeableness = float(request.POST.get('agreeableness', -1))
    neuroticism = float(request.POST.get('neuroticism', -1))
    conscientiousness = float(request.POST.get('conscientiousness', -1))
    extraversion = float(request.POST.get('extraversion', -1))
    recommendation_id = float(request.POST.get('recommendation_id', -1))
    more_suggestions = bool(request.POST.get('more_suggestions', False))
    advanced_mode = bool(request.POST.get('advanced_mode', False))

    if ((not advanced_mode) and (not more_suggestions) and ((age_group != '12-19' and age_group != '20-39' and
          age_group != '40-65') or openness < 20 or openness > 100 or
          agreeableness < 20 or agreeableness > 100 or
          neuroticism < 20 or neuroticism > 100 or
          conscientiousness < 20 or conscientiousness > 100 or
          extraversion < 20 or extraversion > 100)):

        print(advanced_mode, age_group, openness, agreeableness, neuroticism, conscientiousness, extraversion) if DEBUG else None
        logger.error('BASIC_MODE_VALUE_ERROR: advanced_mode {}, age_group {}, openness {}, agreeableness {}, neuroticism {}, conscientiousness {}, extraversion {}'\
            .format(str(advanced_mode), str(age_group), str(openness), str(agreeableness), str(neuroticism), str(conscientiousness), str(extraversion)))
        return render(request, 'individualsymphony/something_went_wrong.html', status=400)

    elif ((more_suggestions) and ((age_group != '12-19' and age_group != '20-39' and
          age_group != '40-65') or openness < 0 or openness > 1 or
          agreeableness < 0 or agreeableness > 1 or
          neuroticism < 0 or neuroticism > 1 or
          conscientiousness < 0 or conscientiousness > 1 or
          extraversion < 0 or extraversion > 1 or
          (recommendation_id == -1))):

        print(recommendation_id, more_suggestions, advanced_mode, age_group, openness, agreeableness, neuroticism, conscientiousness, extraversion) if DEBUG else None
        logger.error('MORE_SUGGESTIONS_VALUE_ERROR: recommendation_id {}, more_suggestions {}, advanced_mode {}, age_group {}, openness {}, agreeableness {}, neuroticism {}, conscientiousness {}, extraversion {}'\
            .format(str(recommendation_id), str(more_suggestions), str(advanced_mode), str(age_group), str(openness), str(agreeableness), str(neuroticism), str(conscientiousness), str(extraversion)))
        return render(request, 'individualsymphony/something_went_wrong.html', status=400)

    elif (more_suggestions):
        try:
            query_list = request.session['query_list']
            genre_corr_result = request.session['genre_corr_result']
            bfpt_result = request.session['bfpt_result']
            remaining_ql = query_list[NUMBER_OF_RECOMMENDATIONS:]
            query_list = query_list[:NUMBER_OF_RECOMMENDATIONS]
            rr_id = create_rr(query_list, genre_corr_result, bfpt_result)
            request.session['recommendation_id'] = rr_id.id
            request.session['query_list'] = remaining_ql
            request.session.set_expiry(60 * 30)

            data = {
                'data': query_list,
                'recommendation_id': rr_id.id
            }
            return JsonResponse(data)
        except Exception as err_msg:
            logger.error('MORE_SUGGESTIONS_ERROR: {}'.format(str(err_msg)))
            return render(request, 'individualsymphony/something_went_wrong.html', status=400)

    else:
        if (advanced_mode):
            form = BFPTForm(request.POST)

            if form.is_valid():
                bfpt_result = eval_bfpt(form.cleaned_data)
                print(bfpt_result) if DEBUG else None
                genre_corr_result = eval_genre_corr(bfpt_result)
                print(genre_corr_result) if DEBUG else None

                try:
                    query_list = create_ql(genre_corr_result, request)
                    remaining_ql = query_list[NUMBER_OF_RECOMMENDATIONS:]
                    query_list = query_list[:NUMBER_OF_RECOMMENDATIONS]
                    rr_id = create_rr(query_list, genre_corr_result, bfpt_result)
                    request.session['recommendation_id'] = rr_id.id
                    request.session['genre_corr_result'] = genre_corr_result
                    request.session['bfpt_result'] = bfpt_result
                    request.session['query_list'] = remaining_ql
                    request.session.set_expiry(60 * 30)  # 30 minutes to expire.
                    analysis_charts = {}
                    analysis_charts.update(genre_corr_result)
                    analysis_charts.update(bfpt_result)
                    print(rr_id.id) if DEBUG else None
                    print(query_list) if DEBUG else None
                except Exception as err_msg:
                    logger.error('ADVANCED_MODE_RECOMMENDATION_ERROR: {}'.format(str(err_msg)))
                    return render(request, 'individualsymphony/something_went_wrong.html', status=400)

                return render(request, 'individualsymphony/results.html', {
                    'data': query_list, 
                    'recommendation_id': rr_id.id,
                    'chart_data': analysis_charts,
                })

            else:
                logger.error('ADVANCED_MODE_FORM_ERROR: {}'.format(str(form.cleaned_data)))
                return render(request, 'individualsymphony/something_went_wrong.html', status=400)

        else:
            bfpt_result = {}
            bfpt_result['age_group'] = age_group
            bfpt_result['openness'] = (openness - 20) / 80
            bfpt_result['agreeableness'] = (agreeableness - 20) / 80
            bfpt_result['extraversion'] = (extraversion - 20) / 80
            bfpt_result['neuroticism'] = (neuroticism - 20) / 80
            bfpt_result['conscientiousness'] = (conscientiousness - 20) / 80
            genre_corr_result = eval_genre_corr(bfpt_result)
            print(genre_corr_result) if DEBUG else None

            try:
                query_list = create_ql(genre_corr_result, request)
                remaining_ql = query_list[NUMBER_OF_RECOMMENDATIONS:]
                query_list = query_list[:NUMBER_OF_RECOMMENDATIONS]
                rr_id = create_rr(query_list, genre_corr_result, bfpt_result)
                request.session['recommendation_id'] = rr_id.id
                request.session['genre_corr_result'] = genre_corr_result
                request.session['bfpt_result'] = bfpt_result
                request.session['query_list'] = remaining_ql
                request.session.set_expiry(60 * 30)  # 30 minutes to expire.
                analysis_charts = {}
                analysis_charts.update(genre_corr_result)
                analysis_charts.update(bfpt_result)
                print(rr_id.id) if DEBUG else None
                print(query_list) if DEBUG else None
            except Exception as err_msg:
                logger.error('BASIC_MODE_RECOMMENDATION_ERROR: {}'.format(str(err_msg)))
                return render(request, 'individualsymphony/something_went_wrong.html', status=400)
            
            return render(request, 'individualsymphony/results.html', {
                    'data': query_list, 
                    'recommendation_id': rr_id.id,
                    'chart_data': analysis_charts
                })


@require_http_methods(["POST", "PATCH", "DELETE"])
def feedback(request):
    if (request.method == "POST"):
        recommendation_id = int(request.POST.get('recommendation_id', -1))
        num = int(request.POST.get('num', -1))

        if (num > NUMBER_OF_RECOMMENDATIONS or recommendation_id <= 0):
            logger.error('FEEDBACK_VALUE_ERROR')
            return render(request, 'individualsymphony/something_went_wrong.html', status=400)

        elif (request.session['recommendation_id'] != recommendation_id):
            data = {
                'recommendation_id': recommendation_id,
                'valid_recommendation_id': request.session['recommendation_id'],
                'num': num
                }
            logger.error('FEEDBACK_POST_RECOMMENDATION_ID_ERROR')
            return render(request, 'individualsymphony/something_went_wrong.html', status=400)

        else:
            r_b = int(request.POST.get('r_b', -1))
            rap = int(request.POST.get('rap', -1))
            electronic = int(request.POST.get('electronic', -1))
            rock = int(request.POST.get('rock', -1))
            new_age = int(request.POST.get('new_age', -1))
            classical = int(request.POST.get('classical', -1))
            reggae = int(request.POST.get('reggae', -1))
            blues = int(request.POST.get('blues', -1))
            country = int(request.POST.get('country', -1))
            world = int(request.POST.get('world', -1))
            folk = int(request.POST.get('folk', -1))
            easy_listening = int(request.POST.get('easy_listening', -1))
            jazz = int(request.POST.get('jazz', -1))
            vocal = int(request.POST.get('vocal', -1))
            punk = int(request.POST.get('punk', -1))
            alternative = int(request.POST.get('alternative', -1))
            pop = int(request.POST.get('pop', -1))
            heavy_metal = int(request.POST.get('heavy_metal', -1))

            if (num == -1):
                if (r_b == -1 or rap == -1 or electronic == -1 or rock == -1 or
                        new_age == -1 or classical == -1 or reggae == -1 or
                        blues == -1 or country == -1 or world == -1 or
                        folk == -1 or easy_listening == -1 or jazz == -1 or
                        vocal == -1 or punk == -1 or alternative == -1 or
                        pop == -1 or heavy_metal == -1):
                    logger.error('FEEDBACK_POST_VALUE_ERROR')
                    return render(request, 'individualsymphony/something_went_wrong.html', status=400)

                else:
                    old_genre_suggestions = GenreSuggestions.objects.filter(
                        recommendation_id=recommendation_id
                    )
                    if (old_genre_suggestions.count() > 0):
                        old_genre_suggestions.update(
                            recommendation_id=recommendation_id,
                            r_b=r_b, rap=rap, electronic=electronic,
                            rock=rock, new_age=new_age,
                            classical=classical, reggae=reggae,
                            blues=blues, country=country, world=world,
                            folk=folk, easy_listening=easy_listening,
                            jazz=jazz, vocal=vocal, punk=punk,
                            alternative=alternative, pop=pop,
                            heavy_metal=heavy_metal
                        )
                    else:
                        create_genre_suggestions = GenreSuggestions.objects.create(
                            recommendation_id=recommendation_id,
                            r_b=r_b, rap=rap, electronic=electronic,
                            rock=rock, new_age=new_age,
                            classical=classical, reggae=reggae,
                            blues=blues, country=country, world=world,
                            folk=folk, easy_listening=easy_listening,
                            jazz=jazz, vocal=vocal, punk=punk,
                            alternative=alternative, pop=pop,
                            heavy_metal=heavy_metal
                            )

                    data = {
                        'recommendation_id': recommendation_id,
                        'r_b': r_b,
                        'rap': rap,
                        'electronic': electronic,
                        'rock': rock,
                        'new_age': new_age,
                        'classical': classical,
                        'reggae': reggae,
                        'blues': blues,
                        'country': country,
                        'world': world,
                        'folk': folk,
                        'easy_listening': easy_listening,
                        'jazz': jazz,
                        'vocal': vocal,
                        'punk': punk,
                        'alternative': alternative,
                        'pop': pop,
                        'heavy_metal': heavy_metal
                        }
                    return JsonResponse(data)
            else:
                if (not (r_b == -1 and rap == -1 and electronic == -1 and
                        rock == -1 and new_age == -1 and classical == -1 and
                        reggae == -1 and blues == -1 and country == -1 and
                        world == -1 and folk == -1 and easy_listening == -1 and
                        jazz == -1 and vocal == -1 and punk == -1 and
                        alternative == -1 and pop == -1 and heavy_metal == -1) or
                        (num < 1)):

                    logger.error('FEEDBACK_POST_VALUE_ERROR')
                    return render(request, 'individualsymphony/something_went_wrong.html', status=400)

                get_query = RecommendationResults.objects.filter(
                    id=recommendation_id)
                if (num == 1):
                    get_query.update(song1_feedback=False)
                elif (num == 2):
                    get_query.update(song2_feedback=False)
                elif (num == 3):
                    get_query.update(song3_feedback=False)
                elif (num == 4):
                    get_query.update(song4_feedback=False)
                elif (num == 5):
                    get_query.update(song5_feedback=False)
                elif (num == 6):
                    get_query.update(song6_feedback=False)
                elif (num == 7):
                    get_query.update(song7_feedback=False)
                elif (num == 8):
                    get_query.update(song8_feedback=False)
                elif (num == 9):
                    get_query.update(song9_feedback=False)
                elif (num == 10):
                    get_query.update(song10_feedback=False)

                data = {
                    'recommendation_id': recommendation_id,
                    'num': num
                    }
                return JsonResponse(data)

    elif (request.method == "PATCH"):
        data = QueryDict(request.body)
        recommendation_id = int(data.get('recommendation_id')) or -1
        num = int(data.get('num', -1)) or -1
        r_b = int(data.get('r_b', -1)) or -1
        rap = int(data.get('rap', -1)) or -1
        electronic = int(data.get('electronic', -1)) or -1
        rock = int(data.get('rock', -1)) or -1
        new_age = int(data.get('new_age', -1)) or -1
        classical = int(data.get('classical', -1)) or -1
        reggae = int(data.get('reggae', -1)) or -1
        blues = int(data.get('blues', -1)) or -1
        country = int(data.get('country', -1)) or -1
        world = int(data.get('world', -1)) or -1
        folk = int(data.get('folk', -1)) or -1
        easy_listening = int(data.get('easy_listening', -1)) or -1
        jazz = int(data.get('jazz', -1)) or -1
        vocal = int(data.get('vocal', -1)) or -1
        punk = int(data.get('punk', -1)) or -1
        alternative = int(data.get('alternative', -1)) or -1
        pop = int(data.get('pop', -1)) or -1
        heavy_metal = int(data.get('heavy_metal', -1)) or -1
        if (num > NUMBER_OF_RECOMMENDATIONS or recommendation_id <= 0):
            logger.error('FEEDBACK_PATCH_VALUE_ERROR')
            return render(request, 'individualsymphony/something_went_wrong.html', status=400)

        elif (request.session['recommendation_id'] != recommendation_id):
            data = {
                'recommendation_id': recommendation_id,
                'valid_recommendation_id': request.session['recommendation_id'],
                'num': num
                }
            logger.error('FEEDBACK_PATCH_RECOMMENDATION_ID_ERROR')
            return render(request, 'individualsymphony/something_went_wrong.html', status=400)

        else:
            if (not (r_b == -1 and rap == -1 and electronic == -1 and
                     rock == -1 and new_age == -1 and classical == -1 and
                     reggae == -1 and blues == -1 and country == -1 and
                     world == -1 and folk == -1 and easy_listening == -1 and
                     jazz == -1 and vocal == -1 and punk == -1 and
                     alternative == -1 and pop == -1 and heavy_metal == -1) or
                    (num < 1)):

                logger.error('FEEDBACK_PATCH_VALUE_ERROR')
                return render(request, 'individualsymphony/something_went_wrong.html', status=400)

            else:
                get_query = RecommendationResults.objects.filter(
                            id=recommendation_id)
                if (num == 1):
                    get_query.update(song1_feedback=True)
                elif (num == 2):
                    get_query.update(song2_feedback=True)
                elif (num == 3):
                    get_query.update(song3_feedback=True)
                elif (num == 4):
                    get_query.update(song4_feedback=True)
                elif (num == 5):
                    get_query.update(song5_feedback=True)
                elif (num == 6):
                    get_query.update(song6_feedback=True)
                elif (num == 7):
                    get_query.update(song7_feedback=True)
                elif (num == 8):
                    get_query.update(song8_feedback=True)
                elif (num == 9):
                    get_query.update(song9_feedback=True)
                elif (num == 10):
                    get_query.update(song10_feedback=True)

                data = {
                    'recommendation_id': recommendation_id,
                    'num': num
                }
                return JsonResponse(data)

    elif (request.method == "DELETE"):
        data = QueryDict(request.body)
        recommendation_id = int(data.get('recommendation_id')) or -1
        num = int(data.get('num', -1)) or -1
        r_b = int(data.get('r_b', -1)) or -1
        rap = int(data.get('rap', -1)) or -1
        electronic = int(data.get('electronic', -1)) or -1
        rock = int(data.get('rock', -1)) or -1
        new_age = int(data.get('new_age', -1)) or -1
        classical = int(data.get('classical', -1)) or -1
        reggae = int(data.get('reggae', -1)) or -1
        blues = int(data.get('blues', -1)) or -1
        country = int(data.get('country', -1)) or -1
        world = int(data.get('world', -1)) or -1
        folk = int(data.get('folk', -1)) or -1
        easy_listening = int(data.get('easy_listening', -1)) or -1
        jazz = int(data.get('jazz', -1)) or -1
        vocal = int(data.get('vocal', -1)) or -1
        punk = int(data.get('punk', -1)) or -1
        alternative = int(data.get('alternative', -1)) or -1
        pop = int(data.get('pop', -1)) or -1
        heavy_metal = int(data.get('heavy_metal', -1)) or -1

        if (num > NUMBER_OF_RECOMMENDATIONS or recommendation_id <= 0):
            logger.error('FEEDBACK_DELETE_VALUE_ERROR')
            return render(request, 'individualsymphony/something_went_wrong.html', status=400)

        elif (request.session['recommendation_id'] != recommendation_id):
            data = {
                'recommendation_id': recommendation_id,
                'valid_recommendation_id': request.session['recommendation_id'],
                'num': num
                }
            logger.error('FEEDBACK_DELETE_RECOMMENDATION_ID_ERROR')
            return render(request, 'individualsymphony/something_went_wrong.html', status=400)

        else:
            if (num == -1):
                if (r_b == -1 or rap == -1 or electronic == -1 or rock == -1 or
                        new_age == -1 or classical == -1 or reggae == -1 or
                        blues == -1 or country == -1 or world == -1 or
                        folk == -1 or easy_listening == -1 or jazz == -1 or
                        vocal == -1 or punk == -1 or alternative == -1 or
                        pop == -1 or heavy_metal == -1):

                    logger.error('FEEDBACK_DELETE_VALUE_ERROR')
                    return render(request, 'individualsymphony/something_went_wrong.html', status=400)
                else:
                    old_genre_suggestions = GenreSuggestions.objects.filter(
                        recommendation_id=recommendation_id
                    )
                    if (old_genre_suggestions.count() > 0):
                        old_genre_suggestions.delete()
                        data = {
                            'recommendation_id': recommendation_id,
                            'detail': 'Genre suggestions are deleted!'
                        }
                        return JsonResponse(data)
                    else:
                        logger.error('FEEDBACK_DELETE_COUNT_ERROR')
                        return render(request, 'individualsymphony/something_went_wrong.html', status=400)
            else:
                logger.error('FEEDBACK_DELETE_VALUE_ERROR')
                return render(request, 'individualsymphony/something_went_wrong.html', status=400)
    else:
        logger.error('FEEDBACK_DELETE_ERROR')
        return render(request, 'individualsymphony/something_went_wrong.html', status=400)


@require_http_methods(["POST"])
def song_genre_suggestion(request):
    valid_genres = ['r_b', 'rap', 'electronic', 'rock', 'new_age', 'classical', 'reggae', 'blues', 'country',
    'world', 'folk', 'easy_listening', 'jazz', 'vocal', 'punk', 'alternative', 'pop', 'heavy_metal']
    genre = str(request.POST.get('genre', 'ERROR'))
    song_id = str(request.POST.get('song_id', 'ERROR'))
    if (song_id != 'ERROR' and genre != 'ERROR' and request.session['recommendation_id'] and genre in valid_genres
        and len(song_id) > 20 and len(song_id) < 30):
        SongGenreSuggestion.objects.create(genre=genre, song_id=song_id)
        data = {
            'genre': genre,
            'song_id': song_id
        }
        return JsonResponse(data)
    else:
        logger.error('SONG_GENRE_SUGGESTION_VALUE_ERROR')
        return render(request, 'individualsymphony/something_went_wrong.html', status=400)


@require_http_methods(["GET"])
def language(request):
    selected_lang = str(request.GET.get('translate', None))
    if (not selected_lang or not selected_lang in [x[0] for x in LANGUAGES]):
        logger.error('LANGUAGE_ERROR')
        return render(request, 'individualsymphony/something_went_wrong.html', status=400)
    else:
        page_url = request.META['HTTP_REFERER']
        page_url = re.sub('/../', '/' + selected_lang + '/', page_url)
        response = redirect(page_url)
        response.set_cookie('django_language', selected_lang)
        translation.activate(selected_lang)
        return response


@require_http_methods(["GET"])
def about(request):
    return render(request, 'individualsymphony/about.html')


@require_http_methods(["GET"])
def whitepaper(request):
    return render(request, 'individualsymphony/whitepaper.html')


@require_http_methods(["GET"])
def references(request):
    return render(request, 'individualsymphony/references.html')


@require_http_methods(["GET"])
def changelog(request):
    return render(request, 'individualsymphony/changelog.html')


@require_http_methods(["GET"])
def contact(request):
    return render(request, 'individualsymphony/contact.html')


def custom400(request, exception):
    return render(request, 'individualsymphony/something_went_wrong.html', status=400)


def custom404(request, exception):
    return render(request, 'individualsymphony/not_found.html', status=404)


def custom500(request):
    return render(request, 'individualsymphony/something_went_wrong.html', status=500)
