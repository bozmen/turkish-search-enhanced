import requests
import sys
import os
import os.path
import json

def esize_entries(path):
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in [f for f in filenames if f.startswith('wiki')]:
            filepath = os.path.join(dirpath, filename)
            subfolder = filepath.split('/')[-2]
            with open(filepath) as json_file:
                doc_json = ''
                for line in json_file:
                    doc = json.loads(line)
                    doc_json += json.dumps({"index": {"_type": "wiki_entry", "_id": doc['id'], "_index": "wiki_tr"}})
                    doc_json += '\n'
                    doc_json += json.dumps({'url': doc['url'], 'title': doc['title'], 'text': doc['text']})
                    doc_json += '\n'
                es_subfolder = './dataset/es/' + subfolder
                es_filename = filename + '.es.json'
                es_path = os.path.join(es_subfolder, es_filename)
                if not os.path.exists(es_subfolder):
                    os.makedirs(es_subfolder)
                with open(es_path, 'w+') as output_file:
                    output_file.write(doc_json)
                    output_file.write('\n')



def bulk_index(es_url):
    bulk_url = es_url + '/_bulk'
    headers = {'content-type': 'application/json'}
    for dirpath, dirnames, filenames in os.walk("./dataset/es"):
        for filename in [f for f in filenames if f.startswith('wiki')]:
            filepath = os.path.join(dirpath, filename)
            with open(filepath, 'r') as json_file:
                response = requests.post(bulk_url, data=json_file, headers=headers)

def main():
    entries_path = sys.argv[1]
    es_url = sys.argv[2]
    esize_entries(entries_path)
    bulk_index(es_url)
    print("Done!")
    return
    

if __name__ == "__main__":
    main()