from threading import local, current_thread
import pandas as pd
from joblib import Parallel, delayed
from pyelasticsearch import ElasticSearch
from pyelasticsearch import bulk_chunks
from time import time


thread_local = local()


def documents_from_file(es, filename, delimiter):
    """
    Return a generator for pulling rows from a given delimited file.

    :param es: an ElasticSearch client
    :param filename: the name of the file to read from or '-' if stdin
    :param delimiter: the delimiter to use
    :return: generator returning document-indexing operations
    """
    def all_docs():
        chunksize = 10000
        reader = pd.read_table(filename, header = None, iterator = True, chunksize = chunksize)
        for i, df in enumerate(reader):
            records = df.to_dict()
            list_records = [records[item] for item in records]
            for col_num, row in enumerate(list_records):
                for  row_num, cell in row.items():
                    yield es.index_op({'row': int(row_num), 'col': int(col_num), 'orig_value': str(cell)})
    return all_docs

def local_bulk(host, index_name, doc_type, chunk):
    """
    Bulk upload the given chunk, creating a thread local ElasticSearch instance
    for the target host if one does not already exist. Retry this function at
    least 10 times with exponential backoff.

    :param host: the target Elasticsearch host
    :param index_name: the index name
    :param doc_type: the document type
    :param chunk: the chunk of documents to bulk upload
    """
    if not hasattr(thread_local, 'es'):
        thread_local.es = ElasticSearch(host)

    thread_local.es.bulk(actions = chunk, index = index_name, doc_type = doc_type)

def perform_bulk_index(host, index_name, doc_type, doc_fetch, docs_per_chunk, bytes_per_chunk, parallel):
    """
    Chunk up documents and send them to Elasticsearch in bulk.

    :param host: the target Elasticsearch host
    :param index_name: the target index name
    :param doc_type: the target document type
    :param doc_fetch: a function to call to fetch documents
    :param docs_per_chunk: the number of documents per chunk to upload
    :param parallel: the number of bulk uploads to do at the same time
    """
    # from joblib import Parallel, delayed

    current_thread().name = 'MainThread'
    Parallel(n_jobs=parallel)(
        delayed(local_bulk)(host, index_name, doc_type, chunk)
        for chunk in bulk_chunks(doc_fetch(),
                                 docs_per_chunk=docs_per_chunk,
                                 bytes_per_chunk=bytes_per_chunk))

def upload_file_into_es(file_path, index_name, doc_type, delimeter='\t', host = 'http://localhost:9200'):
    t0 = time()
    es = ElasticSearch()
    documents = documents_from_file(es, file_path, delimiter = delimeter)
    perform_bulk_index(host = host, index_name = index_name, doc_type = doc_type, doc_fetch = documents, docs_per_chunk = 1000, bytes_per_chunk = 10000, parallel = 2)
    print('Done in %s sec.' % (time()-t0))
