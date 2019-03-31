# Turkish Search Enhancer

## Installation

These steps are only need to be done in the initial run.
* Navigate to the server folder, `cd server`
* Run `docker-compose build`
* Download the files and rename accordingly.
    * for the model -> https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.tr.300.vec.gz
      * rename it model_1.vec and put it under server/flaskr/model
    * for the wikipedia dump -> https://dumps.wikimedia.org/trwiki/20190320/trwiki-20190320-pages-articles-multistream.xml.bz2
      * rename it to wiki_tr and put it under server/dataset
* Run `docker-compose up -d`
* Go into the server container with `docker exec -it bash server_turkish-search-enhanced_1`, and run `make prepare-es` there.

## API Endpoints

* GET /search/{index_name}/{field_name>} with a body
    ```
        {
            "term": <term>,
            "topn": <number of closest words to be used in order to enhance the search>
        }
    ```
* GET /defaultsearch/{index_name}/{field_name} with a body
    ```
        {
            "term": <term>
        }
    ```

## Architecture

The application is a simple Flask app that has 2 endpoints, one for an enhanced search and one for the default elasticsearch search. It speaks to the elasticsearch server to send queries, and takes them back, and serves it to the user. 

There are 2 simple classes:
#### ES
ES takes the elasticsearch url as a constructor parameter, and uses that parameter to start connections to the es server to serve the requests. It uses `bool` queries for search, boosting the terms according to their similarity score, which is served by TermGenerator class.
#### TermGenerator
Term generator takes model path for its constructor, reads it, and returns the most similar terms to the given term, along with their scores. 

## Data

Dataset is a recent Turkish wikipedia dump, and it is indexed in elasticsearch, keeping their text, title and wiki ids.
FastText model is the pre-trained model that creators of FastText prepared themselves, along with 156 other languages.

## Discussion

Turkish is a language that has extensive agglutination, resulting in a high number of inflections of a particular word. Check the following examples to see this phenomena:
* Let's start with a noun, ev -> house.
  * evler -> houses
  * evleri -> his/her houses or accusative case of plural of house
  * evlerinin -> of his/her houses
  * evdekiler -> the ones in the house
  * evden -> ablative case of house 
  * eve -> dative case of house
  * evimdekilerden -> ablative case of the ones in my house
* And then, verb, gitmek -> to go.
  * gidiyor -> he/she is going (note t becomes a d, which is another challenge)
  * gidecek -> he/she will go
  * gitmeli -> he/she must go
  * gidebilecek -> he/she will be able to go
  * gitmediklerimden -> ablative case of the ones that I have not gone to
Therefore, word2vec approach is not as useful as it is at English, in which agglutinativity is very litte. For this purpose, I have used a FastText model which was pre-trained on a Turkish corpora. I see it as a better alternative than word2vec, since it basically represents words as a bag of character n-grams, and that represents the inflections better and represents the Turkish morphology, since it is an accurate modeling of Turkish words. For more information, please refer to [here](https://research.fb.com/fasttext/), and [here](https://arxiv.org/abs/1607.04606).
My approach is, find the n most similar words to the search term, and use their similarity score to boost them in the search query, passing them as `should` terms in a query object. An example query is (only first 5 to keep it short):
```
    {
        "query": {
            "bool": {
                "should": [
                    "term": {
                        "value": "ağaç",
                        "boost": 1
                    },
                    "term": {
                        "value": "ağaçlar",
                        "boost": 0.769
                    },
                    "term": {
                        "value": "ağacın",
                        "boost": 0.752
                    },
                    "term": {
                        "value": "ağaçı",
                        "boost": 0.748
                    },
                    "term": {
                        "value": "ağaçların",
                        "boost": 0.729
                    },
                    "term": {
                        "value": "ağaça",
                        "boost": 0.714
                    },
                    "term": {
                        "value": "ağaçların",
                        "boost": 0.729
                    },
                    "term": {
                        "value": "ağaça",
                        "boost": 0.714
                    }
                ]
            }
        }
    }
```

As we can see, the similar words are mostly (in this case, all) the inflections of the word *ağaç*. Even in bigger topn (which represents the number of closest words to be used), there are synonym and hypnoym relations, such as *fidan*, meaning *sapling*, and *bitki*, meaning *plant*.

Here is a comparison of two resuls: First one being the enhanced search and the second one is the default elasticsearch search.

__ağaç__, meaning tree (with topn 20)
**enhanced**
* First two results:
  * Ağaç İnancı
  * Ağaç

**default**
* First two results:
  * Ağaç ev
  * Gri ağaç kurbağası

Here we see that ağaç, as we would expect, is more relevant in the enhanced one, and we see a quite irrelevant one, gri ağaç kurbağası, which translates as "gray tree frog".

__gelecek__, meaning future (or future 3. singular person, to come) (with topn 20)
**enhanced**
* First six results:
  * Nefertiti'nin Kehaneti
  * Gelecek zaman
  * Retrofütürizm
  * Gelecek
  * Gelecek zamanın hikayesi
  * Fütüroloji
  
**default**
* First six results:
  * Gelecek zaman
  * Retrofütürizm
  * Gelecek 
  * Gelecek zamanın hikayesi
  * Gelecek hareketi
  * Future simple

Here we see that, enhanced one is not really much better against the default one, Nefertiti'nin kehaneti (Propechy of Nefertiti) is coming in as first. In a sense, this is still relevant, but maybe not as much as the other results.

__İstanbul__ (with topn 20)
Here, we see a dramatic improvement.

**enhanced**
* First six results:
  * Avrupa Yakası (meaning European side of Istanbul)
  * 1982-1983 Federasyon Kupası
  * 1962-63 Türkiye Kupası
  * İstanbul'da 1989 Türkiye yerel seçimleri (Local elections of İstanbul in 1989)
  * İstanbul'un ilçeleri
  * Kâğıthane İçmesuyu Arıtma Tesisleri (Kâğıthane is a district of İstanbul)
  
**default**
* First six results:
  * 1971-1972 sezonunda Türkiye'de sahnelenen tiyatro oyunları
  * Cansen Ercan
  * Selim Güneş
  * Celal Türkgeldi
  * İsmet Doğan
  * İstanbul alt bölgesi

Here, in the default results, there are bunch of famous people who were born in İstanbul, which does not really have any relevancy at all. In contrast, enhanced results show some very relevant results, in the sense of geography and politics, along with sports.

## Conclusion

Word2vec and FastText are both algorithms that captures some semantic relations. However, Turkish being a highly agglutinative language, it is safe to say that FastText is better at morphologically modeling Turkish words, especially the inflectioned ones.

## Restrictions

I had some memory problems on my 8 core machine. I managed to tackle them by trading off cpu by memory, and only using the most 1 million frequent tokens of the model. I also wanted to handle the out-of-vocabulary words (which is another advantage of using a FastText model), however that was not possible since it needed a full load of a model, which my memory did not support.

## TODO

* Handle out-of-vocab words
* Improve the search results
* Multi-word support

## References

* https://github.com/attardi/wikiextractor
* https://fasttext.cc/docs/en/pretrained-vectors.html
* https://dumps.wikimedia.org/