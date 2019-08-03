import logging
import numpy as np
import random as rn

from .models import RecommendationResults
from .models import SongGenrePredictions
from django.db import transaction
from django.core.cache import cache
from website.settings import DEBUG
from website.settings import QUERY_LIMIT
from website.settings import KNN_LIMIT
from website.settings import CACHE_TTL
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors


corr_scaler = MinMaxScaler()
genre_corr_scaler = MinMaxScaler()
logger = logging.getLogger(__name__)


def predictions_to_knn(request):
    genre_predictions = SongGenrePredictions.objects.order_by('?')[:KNN_LIMIT]
    knn_values = np.array([[x.r_b, x.rap, x.electronic, x.rock, x.new_age, x.classical, x.reggae, x.blues, x.country, x.world, x.folk, x.easy_listening, x.jazz, x.vocal, x.punk, x.alternative, x.pop, x.heavy_metal] for x in genre_predictions])
    cache.get_or_set('knn_info', [[x.id, x.name, round(x.r_b, 2), round(x.rap, 2), round(x.electronic, 2), round(x.rock, 2), round(x.new_age, 2), round(x.classical, 2), round(x.reggae, 2), round(x.blues, 2), round(x.country, 2), round(x.world, 2), round(x.folk, 2), round(x.easy_listening, 2), round(x.jazz, 2), round(x.vocal, 2), round(x.punk, 2), round(x.alternative, 2), round(x.pop, 2), round(x.heavy_metal, 2)] for x in genre_predictions], timeout=CACHE_TTL)
    cache.get_or_set('knn_query', NearestNeighbors(QUERY_LIMIT).fit(knn_values), timeout=CACHE_TTL)
    del genre_predictions
    del knn_values
    return cache.get('knn_query'), cache.get('knn_info')


def create_ql(genre_corr_result, request):
    genre_corr_matrix = [genre_corr_result['r_b'], genre_corr_result['rap'], genre_corr_result['electronic'],
    genre_corr_result['rock'], genre_corr_result['new_age'], genre_corr_result['classical'], genre_corr_result['reggae'],
    genre_corr_result['blues'], genre_corr_result['country'], genre_corr_result['world'], genre_corr_result['folk'],
    genre_corr_result['easy_listening'], genre_corr_result['jazz'], genre_corr_result['vocal'], genre_corr_result['punk'],
    genre_corr_result['alternative'], genre_corr_result['pop'], genre_corr_result['heavy_metal']]
    genre_corr_matrix = np.array(genre_corr_matrix).reshape(1, -1)
    print(genre_corr_matrix) if DEBUG else None
    if (cache.get('knn_query') and cache.get('knn_info')):
        knn_query, knn_info = cache.get('knn_query'), cache.get('knn_info')
    else:
        knn_query, knn_info = predictions_to_knn(request)
    knn_result = knn_query.kneighbors(genre_corr_matrix, return_distance=False)
    print(knn_result) if DEBUG else None
    selected_keys = [x for x in knn_result[0]]
    query_list = [[knn_info[int(selected_key)][0], knn_info[int(selected_key)][1], knn_info[int(selected_key)][2], knn_info[int(selected_key)][3], \
        knn_info[int(selected_key)][4], knn_info[int(selected_key)][5], knn_info[int(selected_key)][6], knn_info[int(selected_key)][7], knn_info[int(selected_key)][8], \
        knn_info[int(selected_key)][9], knn_info[int(selected_key)][10], knn_info[int(selected_key)][11], knn_info[int(selected_key)][12], knn_info[int(selected_key)][13], \
        knn_info[int(selected_key)][14], knn_info[int(selected_key)][15], knn_info[int(selected_key)][16], knn_info[int(selected_key)][17], knn_info[int(selected_key)][18], \
        knn_info[int(selected_key)][19]] for selected_key in selected_keys]
    print(query_list) if DEBUG else None

    return query_list


def eval_bfpt(form_inputs):
    extraversion = 0
    agreeableness = 0
    conscientiousness = 0
    neuroticism = 0
    openness = 0
    age_group = form_inputs['age_group']

    extraversion_p = int(form_inputs['question_1']) + int(form_inputs['question_11']) + \
    int(form_inputs['question_16']) + int(form_inputs['question_26']) + \
    int(form_inputs['question_36'])
    extraversion_r = 18 - (int(form_inputs['question_6']) + int(form_inputs['question_21']) + \
    int(form_inputs['question_31']))
    extraversion = (extraversion_p + extraversion_r) / 8
    extraversion = (extraversion - 1) / 4  # Normalize BFP values.

    agreeableness_p = int(form_inputs['question_7']) + int(form_inputs['question_17']) + \
    int(form_inputs['question_22']) + int(form_inputs['question_32']) + \
    int(form_inputs['question_42'])
    agreeableness_r = 24 - (int(form_inputs['question_2']) + int(form_inputs['question_12']) + \
    int(form_inputs['question_27']) + int(form_inputs['question_37']))
    agreeableness = (agreeableness_p + agreeableness_r) / 9
    agreeableness = (agreeableness - 1) / 4

    conscientiousness_p = int(form_inputs['question_3']) + int(form_inputs['question_13']) + \
    int(form_inputs['question_28']) + int(form_inputs['question_33']) + \
    int(form_inputs['question_38'])
    conscientiousness_r = 24 - (int(form_inputs['question_8']) + int(form_inputs['question_18']) + \
    int(form_inputs['question_23']) + int(form_inputs['question_43']))
    conscientiousness = (conscientiousness_p + conscientiousness_r) / 9
    conscientiousness = (conscientiousness - 1) / 4

    neuroticism_p = int(form_inputs['question_4']) + int(form_inputs['question_14']) + \
    int(form_inputs['question_19']) + int(form_inputs['question_29']) + \
    int(form_inputs['question_39'])
    neuroticism_r = 18 - (int(form_inputs['question_9']) + int(form_inputs['question_24']) + \
    int(form_inputs['question_34']))
    neuroticism = (neuroticism_p + neuroticism_r) / 8
    neuroticism = (neuroticism - 1) / 4

    openness_p = int(form_inputs['question_5']) + int(form_inputs['question_10']) + \
    int(form_inputs['question_15']) + int(form_inputs['question_20']) + \
    int(form_inputs['question_25']) + int(form_inputs['question_30']) + \
    int(form_inputs['question_40']) + int(form_inputs['question_44'])
    openness_r = 12 - (int(form_inputs['question_35']) + int(form_inputs['question_41']))
    openness = (openness_p + openness_r) / 10
    openness = (openness - 1) / 4

    bfpt_result = {
        'age_group': age_group,
        'extraversion': extraversion, 
        'agreeableness': agreeableness, 
        'conscientiousness': conscientiousness,
        'neuroticism': neuroticism, 
        'openness': openness
        }

    return bfpt_result


@transaction.atomic
def create_rr(query_list, genre_corr_result, bfpt_result):
    rr = RecommendationResults.objects.create(
        song1_id=query_list[0][0], song2_id=query_list[1][0], 
        song3_id=query_list[2][0], song4_id=query_list[3][0],
        song5_id=query_list[4][0], song6_id=query_list[5][0], 
        song7_id=query_list[6][0], song8_id=query_list[7][0],
        song9_id=query_list[8][0], song10_id=query_list[9][0],
        song1_feedback=True, song2_feedback=True, 
        song3_feedback=True, song4_feedback=True, 
        song5_feedback=True, song6_feedback=True, 
        song7_feedback=True, song8_feedback=True, 
        song9_feedback=True, song10_feedback=True,
        r_b=genre_corr_result['r_b'], 
        rap=genre_corr_result['rap'], 
        electronic=genre_corr_result['electronic'],
        rock=genre_corr_result['rock'], 
        new_age=genre_corr_result['new_age'], 
        classical=genre_corr_result['classical'],
        reggae=genre_corr_result['reggae'], 
        blues=genre_corr_result['blues'], 
        country=genre_corr_result['country'],
        world=genre_corr_result['world'], 
        folk=genre_corr_result['folk'], 
        easy_listening=genre_corr_result['easy_listening'],
        jazz=genre_corr_result['jazz'], 
        vocal=genre_corr_result['vocal'], 
        punk=genre_corr_result['punk'], 
        alternative=genre_corr_result['alternative'],
        pop=genre_corr_result['pop'], 
        heavy_metal=genre_corr_result['heavy_metal'],
        age_group=bfpt_result['age_group'],
        openness=bfpt_result['openness'],
        conscientiousness=bfpt_result['conscientiousness'],
        extraversion=bfpt_result['extraversion'],
        agreeableness=bfpt_result['agreeableness'],
        neuroticism=bfpt_result['neuroticism'])

    return RecommendationResults.objects.latest('id')


def eval_genre_corr(bfpt_result):
    ag_12_19 = {}
    ag_12_19['openness'] = {}
    ag_12_19['openness']['r_b'] = -0.019
    ag_12_19['openness']['rap'] = -0.019
    ag_12_19['openness']['electronic'] = 0.046
    ag_12_19['openness']['rock'] = -0.075
    ag_12_19['openness']['new_age'] = 0.142
    ag_12_19['openness']['classical'] = 0.080
    ag_12_19['openness']['reggae'] = -0.015
    ag_12_19['openness']['blues'] = 0.130
    ag_12_19['openness']['country'] = 0.117
    ag_12_19['openness']['world'] = 0.114
    ag_12_19['openness']['folk'] = 0.230
    ag_12_19['openness']['easy_listening'] = 0.084
    ag_12_19['openness']['jazz'] = 0.139
    ag_12_19['openness']['vocal'] = 0.132
    ag_12_19['openness']['punk'] = -0.032
    ag_12_19['openness']['alternative'] = 0.131
    ag_12_19['openness']['pop'] = 0.021
    ag_12_19['openness']['heavy_metal'] = -0.033

    ag_12_19['conscientiousness'] = {}
    ag_12_19['conscientiousness']['r_b'] = -0.026
    ag_12_19['conscientiousness']['rap'] = -0.085
    ag_12_19['conscientiousness']['electronic'] = -0.043
    ag_12_19['conscientiousness']['rock'] = -0.058
    ag_12_19['conscientiousness']['new_age'] = 0.037
    ag_12_19['conscientiousness']['classical'] = 0.028
    ag_12_19['conscientiousness']['reggae'] = -0.102
    ag_12_19['conscientiousness']['blues'] = -0.048
    ag_12_19['conscientiousness']['country'] = -0.067
    ag_12_19['conscientiousness']['world'] = -0.016
    ag_12_19['conscientiousness']['folk'] = -0.014
    ag_12_19['conscientiousness']['easy_listening'] = 0.020
    ag_12_19['conscientiousness']['jazz'] = -0.047
    ag_12_19['conscientiousness']['vocal'] = 0.059
    ag_12_19['conscientiousness']['punk'] = -0.130
    ag_12_19['conscientiousness']['alternative'] = -0.108
    ag_12_19['conscientiousness']['pop'] = 0.045
    ag_12_19['conscientiousness']['heavy_metal'] = -0.005

    ag_12_19['extraversion'] = {}
    ag_12_19['extraversion']['r_b'] = 0.106
    ag_12_19['extraversion']['rap'] = 0.030
    ag_12_19['extraversion']['electronic'] = 0.015
    ag_12_19['extraversion']['rock'] = -0.085
    ag_12_19['extraversion']['new_age'] = -0.022
    ag_12_19['extraversion']['classical'] = -0.136
    ag_12_19['extraversion']['reggae'] = 0.039
    ag_12_19['extraversion']['blues'] = 0.060
    ag_12_19['extraversion']['country'] = 0.005
    ag_12_19['extraversion']['world'] = -0.102
    ag_12_19['extraversion']['folk'] = 0.066
    ag_12_19['extraversion']['easy_listening'] = 0.041
    ag_12_19['extraversion']['jazz'] = 0.005
    ag_12_19['extraversion']['vocal'] = 0.038
    ag_12_19['extraversion']['punk'] = -0.111
    ag_12_19['extraversion']['alternative'] = -0.010
    ag_12_19['extraversion']['pop'] = 0.064
    ag_12_19['extraversion']['heavy_metal'] = -0.148

    ag_12_19['agreeableness'] = {}
    ag_12_19['agreeableness']['r_b'] = -0.049
    ag_12_19['agreeableness']['rap'] = -0.070
    ag_12_19['agreeableness']['electronic'] = -0.090
    ag_12_19['agreeableness']['rock'] = 0.070
    ag_12_19['agreeableness']['new_age'] = 0.008
    ag_12_19['agreeableness']['classical'] = -0.070
    ag_12_19['agreeableness']['reggae'] = -0.032
    ag_12_19['agreeableness']['blues'] = -0.006
    ag_12_19['agreeableness']['country'] = 0.062
    ag_12_19['agreeableness']['world'] = -0.056
    ag_12_19['agreeableness']['folk'] = 0.101
    ag_12_19['agreeableness']['easy_listening'] = -0.073
    ag_12_19['agreeableness']['jazz'] = -0.053
    ag_12_19['agreeableness']['vocal'] = -0.074
    ag_12_19['agreeableness']['punk'] = 0.005
    ag_12_19['agreeableness']['alternative'] = 0.018
    ag_12_19['agreeableness']['pop'] = -0.017
    ag_12_19['agreeableness']['heavy_metal'] = -0.058

    ag_12_19['neuroticism'] = {}
    ag_12_19['neuroticism']['r_b'] = 0.027
    ag_12_19['neuroticism']['rap'] = 0.003
    ag_12_19['neuroticism']['electronic'] = 0.036
    ag_12_19['neuroticism']['rock'] = 0.014
    ag_12_19['neuroticism']['new_age'] = -0.062
    ag_12_19['neuroticism']['classical'] = -0.015
    ag_12_19['neuroticism']['reggae'] = 0.028
    ag_12_19['neuroticism']['blues'] = -0.054
    ag_12_19['neuroticism']['country'] = 0.049
    ag_12_19['neuroticism']['world'] = 0.061
    ag_12_19['neuroticism']['folk'] = -0.064
    ag_12_19['neuroticism']['easy_listening'] = 0.035
    ag_12_19['neuroticism']['jazz'] = -0.039
    ag_12_19['neuroticism']['vocal'] = -0.014
    ag_12_19['neuroticism']['punk'] = 0.101
    ag_12_19['neuroticism']['alternative'] = 0.129
    ag_12_19['neuroticism']['pop'] = 0.040
    ag_12_19['neuroticism']['heavy_metal'] = -0.030

    ag_20_39 = {}
    ag_20_39['openness'] = {}
    ag_20_39['openness']['r_b'] = -0.004
    ag_20_39['openness']['rap'] = -0.011
    ag_20_39['openness']['electronic'] = 0.106
    ag_20_39['openness']['rock'] = -0.104
    ag_20_39['openness']['new_age'] = 0.105
    ag_20_39['openness']['classical'] = 0.038
    ag_20_39['openness']['reggae'] = 0.046
    ag_20_39['openness']['blues'] = 0.167
    ag_20_39['openness']['country'] = 0.126
    ag_20_39['openness']['world'] = 0.217
    ag_20_39['openness']['folk'] = 0.231
    ag_20_39['openness']['easy_listening'] = 0.060
    ag_20_39['openness']['jazz'] = 0.106
    ag_20_39['openness']['vocal'] = 0.170
    ag_20_39['openness']['punk'] = -0.008
    ag_20_39['openness']['alternative'] = 0.116
    ag_20_39['openness']['pop'] = 0.0
    ag_20_39['openness']['heavy_metal'] = -0.044

    ag_20_39['conscientiousness'] = {}
    ag_20_39['conscientiousness']['r_b'] = -0.009
    ag_20_39['conscientiousness']['rap'] = -0.065
    ag_20_39['conscientiousness']['electronic'] = -0.031
    ag_20_39['conscientiousness']['rock'] = 0.016
    ag_20_39['conscientiousness']['new_age'] = -0.053
    ag_20_39['conscientiousness']['classical'] = -0.060
    ag_20_39['conscientiousness']['reggae'] = -0.059
    ag_20_39['conscientiousness']['blues'] = -0.046
    ag_20_39['conscientiousness']['country'] = -0.073
    ag_20_39['conscientiousness']['world'] = -0.009
    ag_20_39['conscientiousness']['folk'] = -0.114
    ag_20_39['conscientiousness']['easy_listening'] = 0.024
    ag_20_39['conscientiousness']['jazz'] = -0.025
    ag_20_39['conscientiousness']['vocal'] = -0.007
    ag_20_39['conscientiousness']['punk'] = -0.103
    ag_20_39['conscientiousness']['alternative'] = -0.165
    ag_20_39['conscientiousness']['pop'] = 0.005
    ag_20_39['conscientiousness']['heavy_metal'] = -0.012

    ag_20_39['extraversion'] = {}
    ag_20_39['extraversion']['r_b'] = 0.065
    ag_20_39['extraversion']['rap'] = 0.108
    ag_20_39['extraversion']['electronic'] = 0.038
    ag_20_39['extraversion']['rock'] = -0.102
    ag_20_39['extraversion']['new_age'] = -0.184
    ag_20_39['extraversion']['classical'] = -0.146
    ag_20_39['extraversion']['reggae'] = 0.025
    ag_20_39['extraversion']['blues'] = 0.032
    ag_20_39['extraversion']['country'] = 0.005
    ag_20_39['extraversion']['world'] = -0.054
    ag_20_39['extraversion']['folk'] = -0.040
    ag_20_39['extraversion']['easy_listening'] = -0.019
    ag_20_39['extraversion']['jazz'] = -0.010
    ag_20_39['extraversion']['vocal'] = -0.013
    ag_20_39['extraversion']['punk'] = -0.029
    ag_20_39['extraversion']['alternative'] = -0.052
    ag_20_39['extraversion']['pop'] = 0.017
    ag_20_39['extraversion']['heavy_metal'] = -0.126

    ag_20_39['agreeableness'] = {}
    ag_20_39['agreeableness']['r_b'] = 0.047
    ag_20_39['agreeableness']['rap'] = 0.062
    ag_20_39['agreeableness']['electronic'] = -0.050
    ag_20_39['agreeableness']['rock'] = -0.031
    ag_20_39['agreeableness']['new_age'] = 0.011
    ag_20_39['agreeableness']['classical'] = -0.010
    ag_20_39['agreeableness']['reggae'] = 0.051
    ag_20_39['agreeableness']['blues'] = 0.018
    ag_20_39['agreeableness']['country'] = 0.184
    ag_20_39['agreeableness']['world'] = -0.025
    ag_20_39['agreeableness']['folk'] = 0.110
    ag_20_39['agreeableness']['easy_listening'] = 0.041
    ag_20_39['agreeableness']['jazz'] = -0.068
    ag_20_39['agreeableness']['vocal'] = -0.001
    ag_20_39['agreeableness']['punk'] = 0.006
    ag_20_39['agreeableness']['alternative'] = 0.029
    ag_20_39['agreeableness']['pop'] = 0.194
    ag_20_39['agreeableness']['heavy_metal'] = -0.105

    ag_20_39['neuroticism'] = {}
    ag_20_39['neuroticism']['r_b'] = -0.001
    ag_20_39['neuroticism']['rap'] = -0.072
    ag_20_39['neuroticism']['electronic'] = -0.023
    ag_20_39['neuroticism']['rock'] = 0.053
    ag_20_39['neuroticism']['new_age'] = -0.064
    ag_20_39['neuroticism']['classical'] = -0.005
    ag_20_39['neuroticism']['reggae'] = -0.042
    ag_20_39['neuroticism']['blues'] = -0.005
    ag_20_39['neuroticism']['country'] = -0.027
    ag_20_39['neuroticism']['world'] = -0.014
    ag_20_39['neuroticism']['folk'] = 0.004
    ag_20_39['neuroticism']['easy_listening'] = -0.012
    ag_20_39['neuroticism']['jazz'] = 0.004
    ag_20_39['neuroticism']['vocal'] = 0.002
    ag_20_39['neuroticism']['punk'] = 0.049
    ag_20_39['neuroticism']['alternative'] = 0.137
    ag_20_39['neuroticism']['pop'] = -0.010
    ag_20_39['neuroticism']['heavy_metal'] = -0.030

    ag_40_65 = {}
    ag_40_65['openness'] = {}
    ag_40_65['openness']['r_b'] = -0.053
    ag_40_65['openness']['rap'] = -0.205
    ag_40_65['openness']['electronic'] = -0.138
    ag_40_65['openness']['rock'] = 0.095
    ag_40_65['openness']['new_age'] = 0.133
    ag_40_65['openness']['classical'] = 0.266
    ag_40_65['openness']['reggae'] = 0.185
    ag_40_65['openness']['blues'] = 0.358
    ag_40_65['openness']['country'] = 0.325
    ag_40_65['openness']['world'] = 0.201
    ag_40_65['openness']['folk'] = 0.368
    ag_40_65['openness']['easy_listening'] = -0.161
    ag_40_65['openness']['jazz'] = -0.124
    ag_40_65['openness']['vocal'] = 0.282
    ag_40_65['openness']['punk'] = 0.089
    ag_40_65['openness']['alternative'] = 0.154
    ag_40_65['openness']['pop'] = -0.157
    ag_40_65['openness']['heavy_metal'] = -0.117

    ag_40_65['conscientiousness'] = {}
    ag_40_65['conscientiousness']['r_b'] = 0.150
    ag_40_65['conscientiousness']['rap'] = 0.059
    ag_40_65['conscientiousness']['electronic'] = 0.152
    ag_40_65['conscientiousness']['rock'] = -0.124
    ag_40_65['conscientiousness']['new_age'] = 0.006
    ag_40_65['conscientiousness']['classical'] = 0.261
    ag_40_65['conscientiousness']['reggae'] = -0.059
    ag_40_65['conscientiousness']['blues'] = 0.321
    ag_40_65['conscientiousness']['country'] = 0.154
    ag_40_65['conscientiousness']['world'] = 0.217
    ag_40_65['conscientiousness']['folk'] = -0.268
    ag_40_65['conscientiousness']['easy_listening'] = 0.256
    ag_40_65['conscientiousness']['jazz'] = 0.510
    ag_40_65['conscientiousness']['vocal'] = 0.125
    ag_40_65['conscientiousness']['punk'] = 0.081
    ag_40_65['conscientiousness']['alternative'] = 0.507
    ag_40_65['conscientiousness']['pop'] = 0.052
    ag_40_65['conscientiousness']['heavy_metal'] = 0.038

    ag_40_65['extraversion'] = {}
    ag_40_65['extraversion']['r_b'] = 0.326
    ag_40_65['extraversion']['rap'] = 0.052
    ag_40_65['extraversion']['electronic'] = -0.246
    ag_40_65['extraversion']['rock'] = -0.182
    ag_40_65['extraversion']['new_age'] = -0.209
    ag_40_65['extraversion']['classical'] = -0.136
    ag_40_65['extraversion']['reggae'] = 0.046
    ag_40_65['extraversion']['blues'] = 0.252
    ag_40_65['extraversion']['country'] = 0.128
    ag_40_65['extraversion']['world'] = 0.028
    ag_40_65['extraversion']['folk'] = 0.181
    ag_40_65['extraversion']['easy_listening'] = 0.212
    ag_40_65['extraversion']['jazz'] = 0.062
    ag_40_65['extraversion']['vocal'] = 0.136
    ag_40_65['extraversion']['punk'] = -0.074
    ag_40_65['extraversion']['alternative'] = -0.027
    ag_40_65['extraversion']['pop'] = 0.287
    ag_40_65['extraversion']['heavy_metal'] = -0.339

    ag_40_65['agreeableness'] = {}
    ag_40_65['agreeableness']['r_b'] = 0.326
    ag_40_65['agreeableness']['rap'] = 0.052
    ag_40_65['agreeableness']['electronic'] = -0.246
    ag_40_65['agreeableness']['rock'] = -0.182
    ag_40_65['agreeableness']['new_age'] = -0.209
    ag_40_65['agreeableness']['classical'] = -0.136
    ag_40_65['agreeableness']['reggae'] = 0.046
    ag_40_65['agreeableness']['blues'] = 0.252
    ag_40_65['agreeableness']['country'] = 0.128
    ag_40_65['agreeableness']['world'] = 0.028
    ag_40_65['agreeableness']['folk'] = 0.181
    ag_40_65['agreeableness']['easy_listening'] = 0.212
    ag_40_65['agreeableness']['jazz'] = 0.062
    ag_40_65['agreeableness']['vocal'] = 0.136
    ag_40_65['agreeableness']['punk'] = -0.074
    ag_40_65['agreeableness']['alternative'] = -0.027
    ag_40_65['agreeableness']['pop'] = 0.287
    ag_40_65['agreeableness']['heavy_metal'] = -0.339

    ag_40_65['neuroticism'] = {}
    ag_40_65['neuroticism']['r_b'] = -0.175
    ag_40_65['neuroticism']['rap'] = -0.158
    ag_40_65['neuroticism']['electronic'] = 0.133
    ag_40_65['neuroticism']['rock'] = 0.182
    ag_40_65['neuroticism']['new_age'] = -0.143
    ag_40_65['neuroticism']['classical'] = -0.080
    ag_40_65['neuroticism']['reggae'] = -0.138
    ag_40_65['neuroticism']['blues'] = -0.552
    ag_40_65['neuroticism']['country'] = -0.109
    ag_40_65['neuroticism']['world'] = -0.236
    ag_40_65['neuroticism']['folk'] = -0.217
    ag_40_65['neuroticism']['easy_listening'] = 0.006
    ag_40_65['neuroticism']['jazz'] = -0.106
    ag_40_65['neuroticism']['vocal'] = -0.091
    ag_40_65['neuroticism']['punk'] = 0.220
    ag_40_65['neuroticism']['alternative'] = 0.070
    ag_40_65['neuroticism']['pop'] = -0.275
    ag_40_65['neuroticism']['heavy_metal'] = 0.372

    bfpts = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
    genres = ['r_b', 'rap', 'electronic', 'rock', 'new_age', 'classical', 'reggae', 'blues', 'country',
    'world', 'folk', 'easy_listening', 'jazz', 'vocal', 'punk', 'alternative', 'pop', 'heavy_metal']
    normalize = []
    fill = []

    for bfpt in bfpts:
        for genre in genres:
            fill.append(ag_12_19[bfpt][genre])

        normalize.append(np.array(fill))
        fill = []

        for genre in genres:
            fill.append(ag_20_39[bfpt][genre])

        normalize.append(np.array(fill))
        fill = []

        for genre in genres:
            fill.append(ag_40_65[bfpt][genre])

        normalize.append(np.array(fill))
        fill = []

    normalize = np.array(normalize)
    corr_scaler.fit(normalize)
    normalize = corr_scaler.transform(normalize)
    normalize = normalize.reshape(-1, 1)  # Make plane to process in for loop.

    it = 0
    for bfpt in bfpts:
        for genre in genres:
            ag_12_19[bfpt][genre] = normalize[it]
            it += 1

        for genre in genres:
            ag_20_39[bfpt][genre] = normalize[it]
            it += 1

        for genre in genres:
            ag_40_65[bfpt][genre] = normalize[it]
            it += 1

    genre_corrs = {}
    genre_corrs['r_b'] = 0
    genre_corrs['rap'] = 0
    genre_corrs['electronic'] = 0
    genre_corrs['rock'] = 0
    genre_corrs['new_age'] = 0
    genre_corrs['classical'] = 0
    genre_corrs['reggae'] = 0
    genre_corrs['blues'] = 0
    genre_corrs['country'] = 0
    genre_corrs['world'] = 0
    genre_corrs['folk'] = 0
    genre_corrs['easy_listening'] = 0
    genre_corrs['jazz'] = 0
    genre_corrs['vocal'] = 0
    genre_corrs['punk'] = 0
    genre_corrs['alternative'] = 0
    genre_corrs['pop'] = 0
    genre_corrs['heavy_metal'] = 0
    genre_corrs_dict = {}

    if (bfpt_result['age_group'] == '12-19'):
        genre_corrs['r_b'] += ag_12_19['openness']['r_b'] * bfpt_result['openness']
        genre_corrs['rap'] += ag_12_19['openness']['rap'] * bfpt_result['openness']
        genre_corrs['electronic'] += ag_12_19['openness']['electronic'] * bfpt_result['openness']
        genre_corrs['rock'] += ag_12_19['openness']['rock'] * bfpt_result['openness']
        genre_corrs['new_age'] += ag_12_19['openness']['new_age'] * bfpt_result['openness']
        genre_corrs['classical'] += ag_12_19['openness']['classical'] * bfpt_result['openness']
        genre_corrs['reggae'] += ag_12_19['openness']['reggae'] * bfpt_result['openness']
        genre_corrs['blues'] += ag_12_19['openness']['blues'] * bfpt_result['openness']
        genre_corrs['country'] += ag_12_19['openness']['country'] * bfpt_result['openness']
        genre_corrs['world'] += ag_12_19['openness']['world'] * bfpt_result['openness']
        genre_corrs['folk'] += ag_12_19['openness']['folk'] * bfpt_result['openness']
        genre_corrs['easy_listening'] += ag_12_19['openness']['easy_listening'] * bfpt_result['openness']
        genre_corrs['jazz'] += ag_12_19['openness']['jazz'] * bfpt_result['openness']
        genre_corrs['vocal'] += ag_12_19['openness']['vocal'] * bfpt_result['openness']
        genre_corrs['punk'] += ag_12_19['openness']['punk'] * bfpt_result['openness']
        genre_corrs['alternative'] += ag_12_19['openness']['alternative'] * bfpt_result['openness']
        genre_corrs['pop'] += ag_12_19['openness']['pop'] * bfpt_result['openness']
        genre_corrs['heavy_metal'] += ag_12_19['openness']['heavy_metal'] * bfpt_result['openness']

        genre_corrs['r_b'] += ag_12_19['conscientiousness']['r_b'] * bfpt_result['conscientiousness']
        genre_corrs['rap'] += ag_12_19['conscientiousness']['rap'] * bfpt_result['conscientiousness']
        genre_corrs['electronic'] += ag_12_19['conscientiousness']['electronic'] * bfpt_result['conscientiousness']
        genre_corrs['rock'] += ag_12_19['conscientiousness']['rock'] * bfpt_result['conscientiousness']
        genre_corrs['new_age'] += ag_12_19['conscientiousness']['new_age'] * bfpt_result['conscientiousness']
        genre_corrs['classical'] += ag_12_19['conscientiousness']['classical'] * bfpt_result['conscientiousness']
        genre_corrs['reggae'] += ag_12_19['conscientiousness']['reggae'] * bfpt_result['conscientiousness']
        genre_corrs['blues'] += ag_12_19['conscientiousness']['blues'] * bfpt_result['conscientiousness']
        genre_corrs['country'] += ag_12_19['conscientiousness']['country'] * bfpt_result['conscientiousness']
        genre_corrs['world'] += ag_12_19['conscientiousness']['world'] * bfpt_result['conscientiousness']
        genre_corrs['folk'] += ag_12_19['conscientiousness']['folk'] * bfpt_result['conscientiousness']
        genre_corrs['easy_listening'] += ag_12_19['conscientiousness']['easy_listening'] * bfpt_result['conscientiousness']
        genre_corrs['jazz'] += ag_12_19['conscientiousness']['jazz'] * bfpt_result['conscientiousness']
        genre_corrs['vocal'] += ag_12_19['conscientiousness']['vocal'] * bfpt_result['conscientiousness']
        genre_corrs['punk'] += ag_12_19['conscientiousness']['punk'] * bfpt_result['conscientiousness']
        genre_corrs['alternative'] += ag_12_19['conscientiousness']['alternative'] * bfpt_result['conscientiousness']
        genre_corrs['pop'] += ag_12_19['conscientiousness']['pop'] * bfpt_result['conscientiousness']
        genre_corrs['heavy_metal'] += ag_12_19['conscientiousness']['heavy_metal'] * bfpt_result['conscientiousness']

        genre_corrs['r_b'] += ag_12_19['agreeableness']['r_b'] * bfpt_result['agreeableness']
        genre_corrs['rap'] += ag_12_19['agreeableness']['rap'] * bfpt_result['agreeableness']
        genre_corrs['electronic'] += ag_12_19['agreeableness']['electronic'] * bfpt_result['agreeableness']
        genre_corrs['rock'] += ag_12_19['agreeableness']['rock'] * bfpt_result['agreeableness']
        genre_corrs['new_age'] += ag_12_19['agreeableness']['new_age'] * bfpt_result['agreeableness']
        genre_corrs['classical'] += ag_12_19['agreeableness']['classical'] * bfpt_result['agreeableness']
        genre_corrs['reggae'] += ag_12_19['agreeableness']['reggae'] * bfpt_result['agreeableness']
        genre_corrs['blues'] += ag_12_19['agreeableness']['blues'] * bfpt_result['agreeableness']
        genre_corrs['country'] += ag_12_19['agreeableness']['country'] * bfpt_result['agreeableness']
        genre_corrs['world'] += ag_12_19['agreeableness']['world'] * bfpt_result['agreeableness']
        genre_corrs['folk'] += ag_12_19['agreeableness']['folk'] * bfpt_result['agreeableness']
        genre_corrs['easy_listening'] += ag_12_19['agreeableness']['easy_listening'] * bfpt_result['agreeableness']
        genre_corrs['jazz'] += ag_12_19['agreeableness']['jazz'] * bfpt_result['agreeableness']
        genre_corrs['vocal'] += ag_12_19['agreeableness']['vocal'] * bfpt_result['agreeableness']
        genre_corrs['punk'] += ag_12_19['agreeableness']['punk'] * bfpt_result['agreeableness']
        genre_corrs['alternative'] += ag_12_19['agreeableness']['alternative'] * bfpt_result['agreeableness']
        genre_corrs['pop'] += ag_12_19['agreeableness']['pop'] * bfpt_result['agreeableness']
        genre_corrs['heavy_metal'] += ag_12_19['agreeableness']['heavy_metal'] * bfpt_result['agreeableness']

        genre_corrs['r_b'] += ag_12_19['neuroticism']['r_b'] * bfpt_result['neuroticism']
        genre_corrs['rap'] += ag_12_19['neuroticism']['rap'] * bfpt_result['neuroticism']
        genre_corrs['electronic'] += ag_12_19['neuroticism']['electronic'] * bfpt_result['neuroticism']
        genre_corrs['rock'] += ag_12_19['neuroticism']['rock'] * bfpt_result['neuroticism']
        genre_corrs['new_age'] += ag_12_19['neuroticism']['new_age'] * bfpt_result['neuroticism']
        genre_corrs['classical'] += ag_12_19['neuroticism']['classical'] * bfpt_result['neuroticism']
        genre_corrs['reggae'] += ag_12_19['neuroticism']['reggae'] * bfpt_result['neuroticism']
        genre_corrs['blues'] += ag_12_19['neuroticism']['blues'] * bfpt_result['neuroticism']
        genre_corrs['country'] += ag_12_19['neuroticism']['country'] * bfpt_result['neuroticism']
        genre_corrs['world'] += ag_12_19['neuroticism']['world'] * bfpt_result['neuroticism']
        genre_corrs['folk'] += ag_12_19['neuroticism']['folk'] * bfpt_result['neuroticism']
        genre_corrs['easy_listening'] += ag_12_19['neuroticism']['easy_listening'] * bfpt_result['neuroticism']
        genre_corrs['jazz'] += ag_12_19['neuroticism']['jazz'] * bfpt_result['neuroticism']
        genre_corrs['vocal'] += ag_12_19['neuroticism']['vocal'] * bfpt_result['neuroticism']
        genre_corrs['punk'] += ag_12_19['neuroticism']['punk'] * bfpt_result['neuroticism']
        genre_corrs['alternative'] += ag_12_19['neuroticism']['alternative'] * bfpt_result['neuroticism']
        genre_corrs['pop'] += ag_12_19['neuroticism']['pop'] * bfpt_result['neuroticism']
        genre_corrs['heavy_metal'] += ag_12_19['neuroticism']['heavy_metal'] * bfpt_result['neuroticism']

        genre_corrs['r_b'] += ag_12_19['extraversion']['r_b'] * bfpt_result['extraversion']
        genre_corrs['rap'] += ag_12_19['extraversion']['rap'] * bfpt_result['extraversion']
        genre_corrs['electronic'] += ag_12_19['extraversion']['electronic'] * bfpt_result['extraversion']
        genre_corrs['rock'] += ag_12_19['extraversion']['rock'] * bfpt_result['extraversion']
        genre_corrs['new_age'] += ag_12_19['extraversion']['new_age'] * bfpt_result['extraversion']
        genre_corrs['classical'] += ag_12_19['extraversion']['classical'] * bfpt_result['extraversion']
        genre_corrs['reggae'] += ag_12_19['extraversion']['reggae'] * bfpt_result['extraversion']
        genre_corrs['blues'] += ag_12_19['extraversion']['blues'] * bfpt_result['extraversion']
        genre_corrs['country'] += ag_12_19['extraversion']['country'] * bfpt_result['extraversion']
        genre_corrs['world'] += ag_12_19['extraversion']['world'] * bfpt_result['extraversion']
        genre_corrs['folk'] += ag_12_19['extraversion']['folk'] * bfpt_result['extraversion']
        genre_corrs['easy_listening'] += ag_12_19['extraversion']['easy_listening'] * bfpt_result['extraversion']
        genre_corrs['jazz'] += ag_12_19['extraversion']['jazz'] * bfpt_result['extraversion']
        genre_corrs['vocal'] += ag_12_19['extraversion']['vocal'] * bfpt_result['extraversion']
        genre_corrs['punk'] += ag_12_19['extraversion']['punk'] * bfpt_result['extraversion']
        genre_corrs['alternative'] += ag_12_19['extraversion']['alternative'] * bfpt_result['extraversion']
        genre_corrs['pop'] += ag_12_19['extraversion']['pop'] * bfpt_result['extraversion']
        genre_corrs['heavy_metal'] += ag_12_19['extraversion']['heavy_metal'] * bfpt_result['extraversion']

    elif (bfpt_result['age_group'] == '20-39'):
        genre_corrs['r_b'] += ag_20_39['openness']['r_b'] * bfpt_result['openness']
        genre_corrs['rap'] += ag_20_39['openness']['rap'] * bfpt_result['openness']
        genre_corrs['electronic'] += ag_20_39['openness']['electronic'] * bfpt_result['openness']
        genre_corrs['rock'] += ag_20_39['openness']['rock'] * bfpt_result['openness']
        genre_corrs['new_age'] += ag_20_39['openness']['new_age'] * bfpt_result['openness']
        genre_corrs['classical'] += ag_20_39['openness']['classical'] * bfpt_result['openness']
        genre_corrs['reggae'] += ag_20_39['openness']['reggae'] * bfpt_result['openness']
        genre_corrs['blues'] += ag_20_39['openness']['blues'] * bfpt_result['openness']
        genre_corrs['country'] += ag_20_39['openness']['country'] * bfpt_result['openness']
        genre_corrs['world'] += ag_20_39['openness']['world'] * bfpt_result['openness']
        genre_corrs['folk'] += ag_20_39['openness']['folk'] * bfpt_result['openness']
        genre_corrs['easy_listening'] += ag_20_39['openness']['easy_listening'] * bfpt_result['openness']
        genre_corrs['jazz'] += ag_20_39['openness']['jazz'] * bfpt_result['openness']
        genre_corrs['vocal'] += ag_20_39['openness']['vocal'] * bfpt_result['openness']
        genre_corrs['punk'] += ag_20_39['openness']['punk'] * bfpt_result['openness']
        genre_corrs['alternative'] += ag_20_39['openness']['alternative'] * bfpt_result['openness']
        genre_corrs['pop'] += ag_20_39['openness']['pop'] * bfpt_result['openness']
        genre_corrs['heavy_metal'] += ag_20_39['openness']['heavy_metal'] * bfpt_result['openness']

        genre_corrs['r_b'] += ag_20_39['conscientiousness']['r_b'] * bfpt_result['conscientiousness']
        genre_corrs['rap'] += ag_20_39['conscientiousness']['rap'] * bfpt_result['conscientiousness']
        genre_corrs['electronic'] += ag_20_39['conscientiousness']['electronic'] * bfpt_result['conscientiousness']
        genre_corrs['rock'] += ag_20_39['conscientiousness']['rock'] * bfpt_result['conscientiousness']
        genre_corrs['new_age'] += ag_20_39['conscientiousness']['new_age'] * bfpt_result['conscientiousness']
        genre_corrs['classical'] += ag_20_39['conscientiousness']['classical'] * bfpt_result['conscientiousness']
        genre_corrs['reggae'] += ag_20_39['conscientiousness']['reggae'] * bfpt_result['conscientiousness']
        genre_corrs['blues'] += ag_20_39['conscientiousness']['blues'] * bfpt_result['conscientiousness']
        genre_corrs['country'] += ag_20_39['conscientiousness']['country'] * bfpt_result['conscientiousness']
        genre_corrs['world'] += ag_20_39['conscientiousness']['world'] * bfpt_result['conscientiousness']
        genre_corrs['folk'] += ag_20_39['conscientiousness']['folk'] * bfpt_result['conscientiousness']
        genre_corrs['easy_listening'] += ag_20_39['conscientiousness']['easy_listening'] * bfpt_result['conscientiousness']
        genre_corrs['jazz'] += ag_20_39['conscientiousness']['jazz'] * bfpt_result['conscientiousness']
        genre_corrs['vocal'] += ag_20_39['conscientiousness']['vocal'] * bfpt_result['conscientiousness']
        genre_corrs['punk'] += ag_20_39['conscientiousness']['punk'] * bfpt_result['conscientiousness']
        genre_corrs['alternative'] += ag_20_39['conscientiousness']['alternative'] * bfpt_result['conscientiousness']
        genre_corrs['pop'] += ag_20_39['conscientiousness']['pop'] * bfpt_result['conscientiousness']
        genre_corrs['heavy_metal'] += ag_20_39['conscientiousness']['heavy_metal'] * bfpt_result['conscientiousness']

        genre_corrs['r_b'] += ag_20_39['agreeableness']['r_b'] * bfpt_result['agreeableness']
        genre_corrs['rap'] += ag_20_39['agreeableness']['rap'] * bfpt_result['agreeableness']
        genre_corrs['electronic'] += ag_20_39['agreeableness']['electronic'] * bfpt_result['agreeableness']
        genre_corrs['rock'] += ag_20_39['agreeableness']['rock'] * bfpt_result['agreeableness']
        genre_corrs['new_age'] += ag_20_39['agreeableness']['new_age'] * bfpt_result['agreeableness']
        genre_corrs['classical'] += ag_20_39['agreeableness']['classical'] * bfpt_result['agreeableness']
        genre_corrs['reggae'] += ag_20_39['agreeableness']['reggae'] * bfpt_result['agreeableness']
        genre_corrs['blues'] += ag_20_39['agreeableness']['blues'] * bfpt_result['agreeableness']
        genre_corrs['country'] += ag_20_39['agreeableness']['country'] * bfpt_result['agreeableness']
        genre_corrs['world'] += ag_20_39['agreeableness']['world'] * bfpt_result['agreeableness']
        genre_corrs['folk'] += ag_20_39['agreeableness']['folk'] * bfpt_result['agreeableness']
        genre_corrs['easy_listening'] += ag_20_39['agreeableness']['easy_listening'] * bfpt_result['agreeableness']
        genre_corrs['jazz'] += ag_20_39['agreeableness']['jazz'] * bfpt_result['agreeableness']
        genre_corrs['vocal'] += ag_20_39['agreeableness']['vocal'] * bfpt_result['agreeableness']
        genre_corrs['punk'] += ag_20_39['agreeableness']['punk'] * bfpt_result['agreeableness']
        genre_corrs['alternative'] += ag_20_39['agreeableness']['alternative'] * bfpt_result['agreeableness']
        genre_corrs['pop'] += ag_20_39['agreeableness']['pop'] * bfpt_result['agreeableness']
        genre_corrs['heavy_metal'] += ag_20_39['agreeableness']['heavy_metal'] * bfpt_result['agreeableness']

        genre_corrs['r_b'] += ag_20_39['neuroticism']['r_b'] * bfpt_result['neuroticism']
        genre_corrs['rap'] += ag_20_39['neuroticism']['rap'] * bfpt_result['neuroticism']
        genre_corrs['electronic'] += ag_20_39['neuroticism']['electronic'] * bfpt_result['neuroticism']
        genre_corrs['rock'] += ag_20_39['neuroticism']['rock'] * bfpt_result['neuroticism']
        genre_corrs['new_age'] += ag_20_39['neuroticism']['new_age'] * bfpt_result['neuroticism']
        genre_corrs['classical'] += ag_20_39['neuroticism']['classical'] * bfpt_result['neuroticism']
        genre_corrs['reggae'] += ag_20_39['neuroticism']['reggae'] * bfpt_result['neuroticism']
        genre_corrs['blues'] += ag_20_39['neuroticism']['blues'] * bfpt_result['neuroticism']
        genre_corrs['country'] += ag_20_39['neuroticism']['country'] * bfpt_result['neuroticism']
        genre_corrs['world'] += ag_20_39['neuroticism']['world'] * bfpt_result['neuroticism']
        genre_corrs['folk'] += ag_20_39['neuroticism']['folk'] * bfpt_result['neuroticism']
        genre_corrs['easy_listening'] += ag_20_39['neuroticism']['easy_listening'] * bfpt_result['neuroticism']
        genre_corrs['jazz'] += ag_20_39['neuroticism']['jazz'] * bfpt_result['neuroticism']
        genre_corrs['vocal'] += ag_20_39['neuroticism']['vocal'] * bfpt_result['neuroticism']
        genre_corrs['punk'] += ag_20_39['neuroticism']['punk'] * bfpt_result['neuroticism']
        genre_corrs['alternative'] += ag_20_39['neuroticism']['alternative'] * bfpt_result['neuroticism']
        genre_corrs['pop'] += ag_20_39['neuroticism']['pop'] * bfpt_result['neuroticism']
        genre_corrs['heavy_metal'] += ag_20_39['neuroticism']['heavy_metal'] * bfpt_result['neuroticism']

        genre_corrs['r_b'] += ag_20_39['extraversion']['r_b'] * bfpt_result['extraversion']
        genre_corrs['rap'] += ag_20_39['extraversion']['rap'] * bfpt_result['extraversion']
        genre_corrs['electronic'] += ag_20_39['extraversion']['electronic'] * bfpt_result['extraversion']
        genre_corrs['rock'] += ag_20_39['extraversion']['rock'] * bfpt_result['extraversion']
        genre_corrs['new_age'] += ag_20_39['extraversion']['new_age'] * bfpt_result['extraversion']
        genre_corrs['classical'] += ag_20_39['extraversion']['classical'] * bfpt_result['extraversion']
        genre_corrs['reggae'] += ag_20_39['extraversion']['reggae'] * bfpt_result['extraversion']
        genre_corrs['blues'] += ag_20_39['extraversion']['blues'] * bfpt_result['extraversion']
        genre_corrs['country'] += ag_20_39['extraversion']['country'] * bfpt_result['extraversion']
        genre_corrs['world'] += ag_20_39['extraversion']['world'] * bfpt_result['extraversion']
        genre_corrs['folk'] += ag_20_39['extraversion']['folk'] * bfpt_result['extraversion']
        genre_corrs['easy_listening'] += ag_20_39['extraversion']['easy_listening'] * bfpt_result['extraversion']
        genre_corrs['jazz'] += ag_20_39['extraversion']['jazz'] * bfpt_result['extraversion']
        genre_corrs['vocal'] += ag_20_39['extraversion']['vocal'] * bfpt_result['extraversion']
        genre_corrs['punk'] += ag_20_39['extraversion']['punk'] * bfpt_result['extraversion']
        genre_corrs['alternative'] += ag_20_39['extraversion']['alternative'] * bfpt_result['extraversion']
        genre_corrs['pop'] += ag_20_39['extraversion']['pop'] * bfpt_result['extraversion']
        genre_corrs['heavy_metal'] += ag_20_39['extraversion']['heavy_metal'] * bfpt_result['extraversion']

    elif (bfpt_result['age_group'] == '40-65'):
        genre_corrs['r_b'] += ag_40_65['openness']['r_b'] * bfpt_result['openness']
        genre_corrs['rap'] += ag_40_65['openness']['rap'] * bfpt_result['openness']
        genre_corrs['electronic'] += ag_40_65['openness']['electronic'] * bfpt_result['openness']
        genre_corrs['rock'] += ag_40_65['openness']['rock'] * bfpt_result['openness']
        genre_corrs['new_age'] += ag_40_65['openness']['new_age'] * bfpt_result['openness']
        genre_corrs['classical'] += ag_40_65['openness']['classical'] * bfpt_result['openness']
        genre_corrs['reggae'] += ag_40_65['openness']['reggae'] * bfpt_result['openness']
        genre_corrs['blues'] += ag_40_65['openness']['blues'] * bfpt_result['openness']
        genre_corrs['country'] += ag_40_65['openness']['country'] * bfpt_result['openness']
        genre_corrs['world'] += ag_40_65['openness']['world'] * bfpt_result['openness']
        genre_corrs['folk'] += ag_40_65['openness']['folk'] * bfpt_result['openness']
        genre_corrs['easy_listening'] += ag_40_65['openness']['easy_listening'] * bfpt_result['openness']
        genre_corrs['jazz'] += ag_40_65['openness']['jazz'] * bfpt_result['openness']
        genre_corrs['vocal'] += ag_40_65['openness']['vocal'] * bfpt_result['openness']
        genre_corrs['punk'] += ag_40_65['openness']['punk'] * bfpt_result['openness']
        genre_corrs['alternative'] += ag_40_65['openness']['alternative'] * bfpt_result['openness']
        genre_corrs['pop'] += ag_40_65['openness']['pop'] * bfpt_result['openness']
        genre_corrs['heavy_metal'] += ag_40_65['openness']['heavy_metal'] * bfpt_result['openness']

        genre_corrs['r_b'] += ag_40_65['conscientiousness']['r_b'] * bfpt_result['conscientiousness']
        genre_corrs['rap'] += ag_40_65['conscientiousness']['rap'] * bfpt_result['conscientiousness']
        genre_corrs['electronic'] += ag_40_65['conscientiousness']['electronic'] * bfpt_result['conscientiousness']
        genre_corrs['rock'] += ag_40_65['conscientiousness']['rock'] * bfpt_result['conscientiousness']
        genre_corrs['new_age'] += ag_40_65['conscientiousness']['new_age'] * bfpt_result['conscientiousness']
        genre_corrs['classical'] += ag_40_65['conscientiousness']['classical'] * bfpt_result['conscientiousness']
        genre_corrs['reggae'] += ag_40_65['conscientiousness']['reggae'] * bfpt_result['conscientiousness']
        genre_corrs['blues'] += ag_40_65['conscientiousness']['blues'] * bfpt_result['conscientiousness']
        genre_corrs['country'] += ag_40_65['conscientiousness']['country'] * bfpt_result['conscientiousness']
        genre_corrs['world'] += ag_40_65['conscientiousness']['world'] * bfpt_result['conscientiousness']
        genre_corrs['folk'] += ag_40_65['conscientiousness']['folk'] * bfpt_result['conscientiousness']
        genre_corrs['easy_listening'] += ag_40_65['conscientiousness']['easy_listening'] * bfpt_result['conscientiousness']
        genre_corrs['jazz'] += ag_40_65['conscientiousness']['jazz'] * bfpt_result['conscientiousness']
        genre_corrs['vocal'] += ag_40_65['conscientiousness']['vocal'] * bfpt_result['conscientiousness']
        genre_corrs['punk'] += ag_40_65['conscientiousness']['punk'] * bfpt_result['conscientiousness']
        genre_corrs['alternative'] += ag_40_65['conscientiousness']['alternative'] * bfpt_result['conscientiousness']
        genre_corrs['pop'] += ag_40_65['conscientiousness']['pop'] * bfpt_result['conscientiousness']
        genre_corrs['heavy_metal'] += ag_40_65['conscientiousness']['heavy_metal'] * bfpt_result['conscientiousness']

        genre_corrs['r_b'] += ag_40_65['agreeableness']['r_b'] * bfpt_result['agreeableness']
        genre_corrs['rap'] += ag_40_65['agreeableness']['rap'] * bfpt_result['agreeableness']
        genre_corrs['electronic'] += ag_40_65['agreeableness']['electronic'] * bfpt_result['agreeableness']
        genre_corrs['rock'] += ag_40_65['agreeableness']['rock'] * bfpt_result['agreeableness']
        genre_corrs['new_age'] += ag_40_65['agreeableness']['new_age'] * bfpt_result['agreeableness']
        genre_corrs['classical'] += ag_40_65['agreeableness']['classical'] * bfpt_result['agreeableness']
        genre_corrs['reggae'] += ag_40_65['agreeableness']['reggae'] * bfpt_result['agreeableness']
        genre_corrs['blues'] += ag_40_65['agreeableness']['blues'] * bfpt_result['agreeableness']
        genre_corrs['country'] += ag_40_65['agreeableness']['country'] * bfpt_result['agreeableness']
        genre_corrs['world'] += ag_40_65['agreeableness']['world'] * bfpt_result['agreeableness']
        genre_corrs['folk'] += ag_40_65['agreeableness']['folk'] * bfpt_result['agreeableness']
        genre_corrs['easy_listening'] += ag_40_65['agreeableness']['easy_listening'] * bfpt_result['agreeableness']
        genre_corrs['jazz'] += ag_40_65['agreeableness']['jazz'] * bfpt_result['agreeableness']
        genre_corrs['vocal'] += ag_40_65['agreeableness']['vocal'] * bfpt_result['agreeableness']
        genre_corrs['punk'] += ag_40_65['agreeableness']['punk'] * bfpt_result['agreeableness']
        genre_corrs['alternative'] += ag_40_65['agreeableness']['alternative'] * bfpt_result['agreeableness']
        genre_corrs['pop'] += ag_40_65['agreeableness']['pop'] * bfpt_result['agreeableness']
        genre_corrs['heavy_metal'] += ag_40_65['agreeableness']['heavy_metal'] * bfpt_result['agreeableness']

        genre_corrs['r_b'] += ag_40_65['neuroticism']['r_b'] * bfpt_result['neuroticism']
        genre_corrs['rap'] += ag_40_65['neuroticism']['rap'] * bfpt_result['neuroticism']
        genre_corrs['electronic'] += ag_40_65['neuroticism']['electronic'] * bfpt_result['neuroticism']
        genre_corrs['rock'] += ag_40_65['neuroticism']['rock'] * bfpt_result['neuroticism']
        genre_corrs['new_age'] += ag_40_65['neuroticism']['new_age'] * bfpt_result['neuroticism']
        genre_corrs['classical'] += ag_40_65['neuroticism']['classical'] * bfpt_result['neuroticism']
        genre_corrs['reggae'] += ag_40_65['neuroticism']['reggae'] * bfpt_result['neuroticism']
        genre_corrs['blues'] += ag_40_65['neuroticism']['blues'] * bfpt_result['neuroticism']
        genre_corrs['country'] += ag_40_65['neuroticism']['country'] * bfpt_result['neuroticism']
        genre_corrs['world'] += ag_40_65['neuroticism']['world'] * bfpt_result['neuroticism']
        genre_corrs['folk'] += ag_40_65['neuroticism']['folk'] * bfpt_result['neuroticism']
        genre_corrs['easy_listening'] += ag_40_65['neuroticism']['easy_listening'] * bfpt_result['neuroticism']
        genre_corrs['jazz'] += ag_40_65['neuroticism']['jazz'] * bfpt_result['neuroticism']
        genre_corrs['vocal'] += ag_40_65['neuroticism']['vocal'] * bfpt_result['neuroticism']
        genre_corrs['punk'] += ag_40_65['neuroticism']['punk'] * bfpt_result['neuroticism']
        genre_corrs['alternative'] += ag_40_65['neuroticism']['alternative'] * bfpt_result['neuroticism']
        genre_corrs['pop'] += ag_40_65['neuroticism']['pop'] * bfpt_result['neuroticism']
        genre_corrs['heavy_metal'] += ag_40_65['neuroticism']['heavy_metal'] * bfpt_result['neuroticism']

        genre_corrs['r_b'] += ag_40_65['extraversion']['r_b'] * bfpt_result['extraversion']
        genre_corrs['rap'] += ag_40_65['extraversion']['rap'] * bfpt_result['extraversion']
        genre_corrs['electronic'] += ag_40_65['extraversion']['electronic'] * bfpt_result['extraversion']
        genre_corrs['rock'] += ag_40_65['extraversion']['rock'] * bfpt_result['extraversion']
        genre_corrs['new_age'] += ag_40_65['extraversion']['new_age'] * bfpt_result['extraversion']
        genre_corrs['classical'] += ag_40_65['extraversion']['classical'] * bfpt_result['extraversion']
        genre_corrs['reggae'] += ag_40_65['extraversion']['reggae'] * bfpt_result['extraversion']
        genre_corrs['blues'] += ag_40_65['extraversion']['blues'] * bfpt_result['extraversion']
        genre_corrs['country'] += ag_40_65['extraversion']['country'] * bfpt_result['extraversion']
        genre_corrs['world'] += ag_40_65['extraversion']['world'] * bfpt_result['extraversion']
        genre_corrs['folk'] += ag_40_65['extraversion']['folk'] * bfpt_result['extraversion']
        genre_corrs['easy_listening'] += ag_40_65['extraversion']['easy_listening'] * bfpt_result['extraversion']
        genre_corrs['jazz'] += ag_40_65['extraversion']['jazz'] * bfpt_result['extraversion']
        genre_corrs['vocal'] += ag_40_65['extraversion']['vocal'] * bfpt_result['extraversion']
        genre_corrs['punk'] += ag_40_65['extraversion']['punk'] * bfpt_result['extraversion']
        genre_corrs['alternative'] += ag_40_65['extraversion']['alternative'] * bfpt_result['extraversion']
        genre_corrs['pop'] += ag_40_65['extraversion']['pop'] * bfpt_result['extraversion']
        genre_corrs['heavy_metal'] += ag_40_65['extraversion']['heavy_metal'] * bfpt_result['extraversion']

    else:
        logger.error('EVAL_GENRE_CORR_INVALID_AGE_ERROR')
        print('Not a valid age group!') if DEBUG else None
        return

    genre_corrs = np.array([genre_corrs['r_b'], genre_corrs['rap'], genre_corrs['electronic'],
    genre_corrs['rock'], genre_corrs['new_age'], genre_corrs['classical'], genre_corrs['reggae'],
    genre_corrs['blues'], genre_corrs['country'], genre_corrs['world'], genre_corrs['folk'], genre_corrs['easy_listening'],
    genre_corrs['jazz'], genre_corrs['vocal'], genre_corrs['punk'], genre_corrs['alternative'], genre_corrs['pop'],
    genre_corrs['heavy_metal']])
    genre_corrs = genre_corrs.reshape(-1, 1)
    genre_corr_scaler.fit(genre_corrs)
    genre_corrs = genre_corr_scaler.transform(genre_corrs)
    genre_corrs_dict['r_b'] = round(float(genre_corrs[0]), 2)
    genre_corrs_dict['rap'] = round(float(genre_corrs[1]), 2)
    genre_corrs_dict['electronic'] = round(float(genre_corrs[2]), 2)
    genre_corrs_dict['rock'] = round(float(genre_corrs[3]), 2)
    genre_corrs_dict['new_age'] = round(float(genre_corrs[4]), 2)
    genre_corrs_dict['classical'] = round(float(genre_corrs[5]), 2)
    genre_corrs_dict['reggae'] = round(float(genre_corrs[6]), 2)
    genre_corrs_dict['blues'] = round(float(genre_corrs[7]), 2)
    genre_corrs_dict['country'] = round(float(genre_corrs[8]), 2)
    genre_corrs_dict['world'] = round(float(genre_corrs[9]), 2)
    genre_corrs_dict['folk'] = round(float(genre_corrs[10]), 2)
    genre_corrs_dict['easy_listening'] = round(float(genre_corrs[11]), 2)
    genre_corrs_dict['jazz'] = round(float(genre_corrs[12]), 2)
    genre_corrs_dict['vocal'] = round(float(genre_corrs[13]), 2)
    genre_corrs_dict['punk'] = round(float(genre_corrs[14]), 2)
    genre_corrs_dict['alternative'] = round(float(genre_corrs[15]), 2)
    genre_corrs_dict['pop'] = round(float(genre_corrs[16]), 2)
    genre_corrs_dict['heavy_metal'] = round(float(genre_corrs[17]), 2)

    return genre_corrs_dict