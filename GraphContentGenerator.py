import seaborn as sns


class GraphContentGenerator:

    @staticmethod
    def get_compound_vs_length_object(text, scores, lengths):
        data = {'scores': scores['compound'],
                'lengths': lengths['data']}
        return {'text': text,
                'graph': sns.relplot(data=data, x="scores", y="lengths")}

    @classmethod
    def get_compound_vs_emoji_count_object(cls, text, scores, emoji_counts):
        data = {'scores': scores['compound'],
                'lengths': emoji_counts['data']}
        return {'text': text,
                'graph': sns.relplot(data=data, x="scores", y="lengths")}

    @classmethod
    def get_basic_score_object(cls, text, vader_scores):
        return {'text': text,
                'graph': sns.histplot(x=vader_scores['compound'])}

