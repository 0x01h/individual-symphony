from django import forms

answers = ((1, 'Disagree Strongly',), (2, 'Disagree A Little',), 
           (3, 'Neutral',), (4, 'Agree A Little',), (5, 'Agree Strongly',))

age_groups = (('12-19', '12-19',), ('20-39', '20-39',), ('40-65', '40-65',))


class BFPTForm(forms.Form):
    age_group = forms.CharField(label='Is in this age group', widget=forms.Select(choices=age_groups))
    question_1 = forms.ChoiceField(label='Is talkative', choices=answers, widget=forms.RadioSelect)
    question_2 = forms.ChoiceField(label='Tends to find fault with others', choices=answers, widget=forms.RadioSelect)
    question_3 = forms.ChoiceField(label='Does a thorough job', choices=answers, widget=forms.RadioSelect)
    question_4 = forms.ChoiceField(label='Is depressed, blue', choices=answers, widget=forms.RadioSelect)
    question_5 = forms.ChoiceField(label='Is original, comes up with new ideas', choices=answers, widget=forms.RadioSelect)
    question_6 = forms.ChoiceField(label='Is reserved', choices=answers, widget=forms.RadioSelect)
    question_7 = forms.ChoiceField(label='Is helpful and unselfish with others', choices=answers, widget=forms.RadioSelect)
    question_8 = forms.ChoiceField(label='Can be somewhat careless', choices=answers, widget=forms.RadioSelect)
    question_9 = forms.ChoiceField(label='Is relaxed, handles stress well', choices=answers, widget=forms.RadioSelect)
    question_10 = forms.ChoiceField(label='Is curious about many different things', choices=answers, widget=forms.RadioSelect)
    question_11 = forms.ChoiceField(label='Is full of energy', choices=answers, widget=forms.RadioSelect)
    question_12 = forms.ChoiceField(label='Starts quarrels with others', choices=answers, widget=forms.RadioSelect)
    question_13 = forms.ChoiceField(label='Is a reliable worker', choices=answers, widget=forms.RadioSelect)
    question_14 = forms.ChoiceField(label='Can be tense', choices=answers, widget=forms.RadioSelect)
    question_15 = forms.ChoiceField(label='Is ingenious, a deep thinker', choices=answers, widget=forms.RadioSelect)
    question_16 = forms.ChoiceField(label='Generates a lot of enthusiasm', choices=answers, widget=forms.RadioSelect)
    question_17 = forms.ChoiceField(label='Has a forgiving nature', choices=answers, widget=forms.RadioSelect)
    question_18 = forms.ChoiceField(label='Tends to be disorganized', choices=answers, widget=forms.RadioSelect)
    question_19 = forms.ChoiceField(label='Worries a lot', choices=answers, widget=forms.RadioSelect)
    question_20 = forms.ChoiceField(label='Has an active imagination', choices=answers, widget=forms.RadioSelect)
    question_21 = forms.ChoiceField(label='Tends to be quiet', choices=answers, widget=forms.RadioSelect)
    question_22 = forms.ChoiceField(label='Is generally trusting', choices=answers, widget=forms.RadioSelect)
    question_23 = forms.ChoiceField(label='Tends to be lazy', choices=answers, widget=forms.RadioSelect)
    question_24 = forms.ChoiceField(label='Is emotionally stable, not easily upset', choices=answers, widget=forms.RadioSelect)
    question_25 = forms.ChoiceField(label='Is inventive', choices=answers, widget=forms.RadioSelect)
    question_26 = forms.ChoiceField(label='Has an assertive personality', choices=answers, widget=forms.RadioSelect)
    question_27 = forms.ChoiceField(label='Can be cold and aloof', choices=answers, widget=forms.RadioSelect)
    question_28 = forms.ChoiceField(label='Perseveres until the task is finished', choices=answers, widget=forms.RadioSelect)
    question_29 = forms.ChoiceField(label='Can be moody', choices=answers, widget=forms.RadioSelect)
    question_30 = forms.ChoiceField(label='Values artistic, aesthetic experiences', choices=answers, widget=forms.RadioSelect)
    question_31 = forms.ChoiceField(label='Is sometimes shy, inhibited', choices=answers, widget=forms.RadioSelect)
    question_32 = forms.ChoiceField(label='Is considerate and kind to almost everyone', choices=answers, widget=forms.RadioSelect)
    question_33 = forms.ChoiceField(label='Does things efficiently', choices=answers, widget=forms.RadioSelect)
    question_34 = forms.ChoiceField(label='Remains calm in tense situations', choices=answers, widget=forms.RadioSelect)
    question_35 = forms.ChoiceField(label='Prefers work that is routine', choices=answers, widget=forms.RadioSelect)
    question_36 = forms.ChoiceField(label='Is outgoing, sociable', choices=answers, widget=forms.RadioSelect)
    question_37 = forms.ChoiceField(label='Is sometimes rude to others', choices=answers, widget=forms.RadioSelect)
    question_38 = forms.ChoiceField(label='Makes plans and follows through with them', choices=answers, widget=forms.RadioSelect)
    question_39 = forms.ChoiceField(label='Gets nervous easily', choices=answers, widget=forms.RadioSelect)
    question_40 = forms.ChoiceField(label='Likes to reflect, play with ideas', choices=answers, widget=forms.RadioSelect)
    question_41 = forms.ChoiceField(label='Has few artistic interests', choices=answers, widget=forms.RadioSelect)
    question_42 = forms.ChoiceField(label='Likes to cooperate with others', choices=answers, widget=forms.RadioSelect)
    question_43 = forms.ChoiceField(label='Is easily distracted', choices=answers, widget=forms.RadioSelect)
    question_44 = forms.ChoiceField(label='Is sophisticated in art, music, or literature', choices=answers, widget=forms.RadioSelect)