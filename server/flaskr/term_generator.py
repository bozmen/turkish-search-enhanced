from gensim.models import KeyedVectors

class TermGenerator:
    def __init__(self, model_path):
        self.model = KeyedVectors.load_word2vec_format(model_path, limit=500000)

    def get_similar_terms(self, term, topn=50):
        term_tuples = self.model.most_similar(term, topn=topn)
        return term_tuples

    def extract_words(self, term_tuples):
        return [term_tuple[0] for term_tuple in term_tuples]