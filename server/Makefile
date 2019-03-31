prepare-es:
	python3.7 scripts/WikiExtractor.py -o ./dataset/extractor --json ./dataset/wiki_tr && \
	python3.7 scripts/bulk_creator.py ./dataset/extractor http://172.17.0.1:9200 && \
	rm -rf .dataset/extractor