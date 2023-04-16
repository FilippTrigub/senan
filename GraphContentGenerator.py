import seaborn as sns


class GraphContentGenerator:

    @staticmethod
    def get_compound_vs_length_object(text, scores, lengths):
        data = {'scores': scores['compound'],
                'lengths': lengths['data']}
        plot = sns.relplot(data=data, x="scores", y="lengths")
        plot.set(xlabel="Vader scores", ylabel="Lengths")
        return {'text': text,
                'graph': plot}

    @classmethod
    def get_compound_vs_emoji_count_object(cls, text, scores, emoji_counts):
        data = {'scores': scores['compound'],
                'lengths': emoji_counts['data']}
        plot = sns.relplot(data=data, x="scores", y="lengths")
        plot.set(xlabel="Vader scores", ylabel="Emoji counts")
        return {'text': text,
                'graph': plot}

    @classmethod
    def get_basic_score_object(cls, text, vader_scores):
        plot = sns.histplot(x=vader_scores['compound'])
        plot.set(xlabel="Vader scores", ylabel="Count")
        return {'text': text,
                'graph': plot}
