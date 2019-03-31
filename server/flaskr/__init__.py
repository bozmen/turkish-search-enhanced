import os

from flask import Flask, current_app, request
from flaskr.es import EsClient
from flaskr.term_generator import TermGenerator

def create_app(test_config=None):
    #create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        ES_URL='http://172.17.0.1:9200',
        MODEL_PATH='./flaskr/model/model_1.vec'
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    with app.app_context():
        current_app.logger.info("Connectiong to the Elasticsearch client...")
        es_client = EsClient(current_app.config['ES_URL'])
        current_app.logger.info("Loading the FastText model...")
        term_generator = TermGenerator(current_app.config['MODEL_PATH'])
        current_app.logger.info("FastText model has been loaded.")

    # main page
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # enhanced search
    @app.route('/search/<index_name>/<field_name>')
    def search(index_name, field_name):
        request_data = request.get_json()
        topn = request_data.get('topn')
        term = request_data.get('term')
        term_tuples = term_generator.get_similar_terms(term=term, topn=topn)
        return str(es_client.search(index_name, field_name, term, term_tuples, False))

    # default search
    @app.route('/defaultsearch/<index_name>/<field_name>')
    def default_search(index_name, field_name):
        request_data = request.get_json()
        term = request_data.get('term')
        return str(es_client.default_search(index_name, field_name, term))

    return app