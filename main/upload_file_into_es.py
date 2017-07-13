from threading import local, current_thread
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from itertools import islice, chain
import pandas as pd
from joblib import Parallel, delayed
from time import time


thread_local = local()


def documents_from_file(file_name, index_name, delimiter = '\t'):
    """
    Return a generator for pulling rows from a given delimited file.

    :param filename: the name of the file to read from or '-' if stdin
    :param index_name: the name of just created index
    :param delimiter: the delimiter to use
    :return: generator returning document-indexing operations
    """
    def all_docs():
        chunksize = 10000
        reader = pd.read_table(file_name, header = None, iterator = True, chunksize = chunksize)
        for i, df in enumerate(reader):
            records = df.to_dict()
            list_records = [records[item] for item in records]
            for col_num, row in enumerate(list_records):
                for row_num, cell in row.items():
                    yield \
                        (
                            {
                                '_index': index_name,
                                '_type': index_name,
                                '_source': {'row': int(row_num), 'col': int(col_num), 'orig_value': str(cell)}
                            }
                        )
    return all_docs

def chunks(iterable, size):
    iterator = iter(iterable)
    for first in iterator:
        yield list(chain([first], islice(iterator, size - 1)))

def es_bulk(host, docs):
    if not hasattr(thread_local, 'es_local'):
        thread_local.es_local = Elasticsearch(host)
    bulk(thread_local.es_local, docs)

def upload_file_into_es(file_path, index_name, delimeter = '\t', host = 'http://localhost:9200'):
    t0 = time()
    current_thread().name = 'MainThread'
    documents = documents_from_file(file_name = file_path, index_name = index_name, delimiter = delimeter)
    Parallel(n_jobs=12)(delayed(es_bulk)(host = host, docs = chunk) for chunk in chunks(documents(), 50000))
    print('Done in %s sec.' % (time()-t0))
