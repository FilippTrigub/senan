import seaborn as sns

MAPPING = {'compound_vs_length': get_compound_vs_length_object,
           'compound_vs_emoji_count': get_compound_vs_emoji_count_object,
           'basic_score': get_basic_score_object}


def get_compound_vs_length_object(text, scores, lengths):
    data = {'scores': scores['compound'],
            'lengths': lengths['data']}
    plot = sns.relplot(data=data, x="scores", y="lengths")
    plot.set(xlabel="Vader scores", ylabel="Lengths")
    return {'text': text,
            'graph': plot}


def get_compound_vs_emoji_count_object(text, scores, emoji_counts):
    data = {'scores': scores['compound'],
            'lengths': emoji_counts['data']}
    plot = sns.relplot(data=data, x="scores", y="lengths")
    plot.set(xlabel="Vader scores", ylabel="Emoji counts")
    return {'text': text,
            'graph': plot}


def get_basic_score_object(text, vader_scores):
    plot = sns.histplot(x=vader_scores['compound'])
    plot.set(xlabel="Vader scores", ylabel="Count")
    return {'text': text,
            'graph': plot}
