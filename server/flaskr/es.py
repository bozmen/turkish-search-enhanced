from flaskr import http
import json

class EsClient:
    def __init__(self, url):
        self.url = url

    def search(self, index_name, field_name, term, term_tuples, original_term_is_a_must=True):
        should_terms = []
        must_terms = []
        for term_tuple in term_tuples:
            should_terms.append(self.create_term(field_name, term_tuple[0], term_tuple[1]**3))
        term_query = self.create_term(field_name, term, 1)
        if original_term_is_a_must:
            must_terms.append(term_query)
        else:
            should_terms.append(term_query)
        query = {
            "query": {
                "bool": {
                    "must": must_terms,
                    "should": should_terms
                }
            }
        }
        print(self.url)
        headers = {'content-type': 'application/json'}
        return http.get(f'{self.url}/{index_name}/_search', json.dumps(query), headers).text

    def default_search(self, index_name, field_name, term):
        return http.get(f'{self.url}/{index_name}/_search?q={field_name}:{term}').text

    def create_term(self, field_name, value, boost):
        cur_term = {}
        cur_term[field_name] = {
            "value": value,
            "boost": boost
        }
        return {
            "term": cur_term
        }
