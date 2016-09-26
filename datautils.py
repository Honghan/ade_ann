import pyodbc
import codecs
from os.path import join
import datetime


# SQL db setting
db_conn = {
    'dsn': 'sqlserverdatasource',
    'user':  '',
    'password':  '',
    'database':  ''
}

# sql query template
sql_template = 'select CN_Doc_ID + \'-{table}-{col}\' fn, {col} txt from {table} where CN_Doc_ID in ({ids})'

def query_sqlsvr(query, db_conf):
    patients = {}
    medicatons = []
    ADEs = {}
    drugs = {}
    con_string = 'DSN=%s;UID=%s;PWD=%s;DATABASE=%s;' % (db_conf['db_conndsn'],
                                                        db_conf['user'],
                                                        db_conf['password'],
                                                        db_conf['database'])
    cnxn = pyodbc.connect(con_string)
    cursor = cnxn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows


# extract cris text files
def extract_cris_texts(out_path):
    q_txt_list = 'select * from ( select top 500 CN_Doc_ID, src_table, src_col ' \
                 'from sqlcris_user.[13_025].EXPERT_ADR_Data ) a ' \
                 'order by src_table, CN_Doc_ID'

    txt_list = query_sqlsvr(q_txt_list, db_conn)
    table = ''
    col = ''
    ids = ''
    sqls = []
    for txt in txt_list:
        if txt['src_table'] != table:
            if table.strip() != '':
                sqls.append(sql_template.format({'table': table, 'col':col, 'ids': ids}))
            table = txt['src_table']
            col = txt['src_col']
            ids = ''
        ids += (',' if len(ids) > 0 else '') + "'" + txt['CN_Doc_ID'] + "'"
    sqls.append(sql_template.format({'table': table, 'col': col, 'ids': ids}))

    q_data = ' union '.join(sqls)
    print 'query [\n%s\n]...' % q_data
    rows = query_sqlsvr(q_txt_list, db_conn)
    for r in rows:
        with codecs.open(join(out_path, r['fn']), 'w', encoding='utf-8') as wf:
            wf.write(r['txt'])
    print '{} files saved to {}'.format(len(rows), out_path)


if __name__ == "__main__":
    extract_cris_texts('./cris_docs/')

