#!/home/ushiku/.pyenv/shims/python
# -*- coding: utf-8 -*-
#=====================================================================================
#                           Vectorize.py
#                           by Atsushi Ushiku, Ikko Ota
#                           Last change : 2/7 2017
#=====================================================================================

# 機  能 : textファイルをvectorに変換する
#
# 使用法 : python Vectorize.py
#
# 実  例 : python  Vectorize.py ../corpus/newtext/1.txt  ../auto/test.index ../auto/newvector/2.vector ../auto/TFIDF_vector/2.vector
#
# 注意点 : 第一引数は、textファイルのある場所, 第二引数は読み出すindex, 第三引数はvectorの保存先, 第四引数はTFIDF化したvectorの保存先


#-------------------------------------------------------------------------------------
#                       import
#-------------------------------------------------------------------------------------

import os
import sys
import glob
import numpy as np
import datetime
sys.path.insert(1, "../lib/python")  # モジュールの読み込む先を追加している
from preprocess import Preprocessor
from parse import Parser
from vectorizer import Vectorizer

#-------------------------------------------------------------------------------------
#                       set constant
#-------------------------------------------------------------------------------------

text_path = sys.argv[1]
index_path = sys.argv[2]
vector_path = sys.argv[3]
tfidf_vector_path = sys.argv[4]

auto_text_path = '../auto/newtext'
tree_path = '../auto/newtree'

kytea_path = '../model/Train+Test-2017-03-19.kbm'
eda_path = '../model/0303.ebm'

thesaurus_path = '../corpus/thesaurus/thesaurus.txt'
IDF_path = '../auto/IDF.index'
tfidf_DB_path = '../auto/TFIDF_vectors_DB'

base_name = os.path.basename(text_path)  # A.text
root = os.path.splitext(base_name)[0]  # A

#-------------------------------------------------------------------------------------
#                       main
#-------------------------------------------------------------------------------------

PREPROCESSOR = Preprocessor(thesaurus_path)  # シソーラス・パスを渡さなければ置換をしません。
print('前処理を行います')
PREPROCESSOR.load_text([text_path])
whitelist = PREPROCESSOR.investigate_whitelist(thesaurus_path)
print('保存します')
PREPROCESSOR.save(auto_text_path)
PARSER = Parser() 
print('かかり受け解析を行います..')
PARSER.t2f([auto_text_path + '/' + root + '.text'], kytea_model=kytea_path, eda_model=eda_path)
print('結果を保存します')
PARSER.save(tree_path)  # かかり受け解析したものをファイルに保存
print("Indexを読み込みます...")
VECTORIZER = Vectorizer(index_path, t=1,list = whitelist)  # Indexの読み込み
print('Treeを読み込みます')
vectors = VECTORIZER.get_vector([tree_path + '/' + root + '.eda'], filter=3)  # ベクトルを生成
print(vectors)
print('Vectorを保存します')
VECTORIZER.save(vectors, [vector_path])  # ベクトルを保存

#-----
# いまもっているTFIDFコーパスベクトル群と、クエリベクトルtfidf_vectorsを比較
#----

print('TFIDF corpus Vectorsを読み込みます')
tfidf_corpus_vectors = VECTORIZER.load(sorted(glob.glob(tfidf_DB_path + '/*.vector')))
print(tfidf_corpus_vectors)

print('IDF Vectorを読み込みます')
IDF_vector = VECTORIZER.load_IDF(IDF_path)
print(IDF_vector)

print('クエリをTFIDF化します...')
tfidf_vectors = vectors * IDF_vector
print(tfidf_vectors)

print('クエリのTFIDF Vectorを保存します:保存先は')
print(tfidf_vector_path)
VECTORIZER.save(tfidf_vectors,[tfidf_vector_path])

print('類似度')
print(VECTORIZER.get_cos_sim(tfidf_vectors, tfidf_corpus_vectors))

#=====================================================================================
#                       END
#=====================================================================================
