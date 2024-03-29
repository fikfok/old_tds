from threading import local, current_thread
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from itertools import islice, chain
import pandas as pd
from joblib import Parallel, delayed
from time import time


thread_local = local()


def documents_from_file(file_name, index_name, read_chunk_size, delimiter = '\t'):
    """
    Return a generator for pulling rows from a given delimited file.

    :param filename: the name of the file to read from or '-' if stdin
    :param index_name: the name of just created index
    :param delimiter: the delimiter to use
    :return: generator returning document-indexing operations
    """
    def all_docs():
        reader = pd.read_table(file_name, header = None, iterator = True, chunksize = read_chunk_size, delimiter = delimiter)
        for i, df in enumerate(reader):
            df.rename(columns={col: 'col_' + str(col) for col in df.columns}, inplace=True)
            df['row_num'] = df.index

            for row_num, row in enumerate(list(df.transpose().to_dict().values())):
                yield \
                        (
                            {
                                '_index': index_name,
                                '_type': index_name,
                                '_source': row
                            }
                        )
    return all_docs

def chunks(iterable, size):
    iterator = iter(iterable)
    for first in iterator:
        yield list(chain([first], islice(iterator, size - 1)))

def es_bulk(host, docs, index_name):
    if not hasattr(thread_local, 'es_local'):
        thread_local.es_local = Elasticsearch(host)
    bulk(thread_local.es_local, docs)
    # thread_local.es_local.indices.refresh(index = index_name)

def upload_file_into_es(file_path, index_name, read_chunk_size, parallel_jobs_count, index_chunk_size, delimeter = '\t', host = 'http://localhost:9200'):
    t0 = time()
    current_thread().name = 'MainThread'
    documents = documents_from_file(file_name = file_path, index_name = index_name, read_chunk_size = read_chunk_size, delimiter = delimeter)
    Parallel(n_jobs = parallel_jobs_count)(delayed(es_bulk)(host = host, docs = chunk, index_name = index_name) for chunk in chunks(documents(), index_chunk_size))
    print('Done in %s sec.' % (time()-t0))
