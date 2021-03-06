#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import re
import math
import datetime
import glob
import itertools
import numpy as np
from collections import OrderedDict
from scipy.spatial.distance import cosine
from index import Index
from parse import Parser



class Vectorizer:
    '''
    Indexを読み込んで、Vectorizeする
    '''
    def __init__(self, file_path,t=0,list=[]):
        self.file_list = []  # 読み込んだファイルの名前のリスト
        self._load_index(file_path,t,list)

    def _load_index(self, file_path,t=0,list=[]):
        '''
        Index().saveで保存したfile_pathからindexを読み込む。
        tは閾値。tより多く出た単語を追加する。
        listはホワイトリスト。もしこのリストの単語が出現したら、それは閾値に関係なく素性として採用する。
        '''
        self.index = OrderedDict()
        self.index['UNKNOWN'] = 0  # UNKNOWNは例外
        count = 1
        try:
            file = open(file_path, 'r')
        except:
            sys.stderr.write(file_path + 'が開けませんでした。 存在してるIndexかを確認してください')
            return 0
        first_line_flag = 1  # 一行目の設定を読み込むためのflag
        for unit in file:
            if first_line_flag == 1:
                feature_type_flags = unit.split(':')[1].split(' ')  # どの素性を使うか..?
                self.unigram = int(feature_type_flags[0])
                self.bigram = int(feature_type_flags[1])
                self.trigram = int(feature_type_flags[2])
                self.dep_bigram = int(feature_type_flags[3])
                self.dep_trigram = int(feature_type_flags[4])
                first_line_flag = 0
            else:   # 目的の要素の処理
                unit = str(unit).split(',')
                unit[1] = int(unit[1])
                if  'TBI' in unit[0]:
                    continue
                if (self._iswhite(unit[0],list)) or unit[1] >= t:  # しきい値を超えたものを登録する
                    self.index[unit[0]] = count
                    count += 1
        return 0


    def save(self, vectors, file_path_list):
        '''
        vectorsをfile_pathに表記する. 読み込んだファイルA.edaからA.vectorとして保存する
        例)
        index:freq\n
        index:freq\n
        index:freq\n
        index:freq\n
        ・・・・
        \n
        '''
        if not len(vectors) == len(file_path_list):
            sys.stderr.write("vectorは、" + len(vectors) + "のファイルを、保存先は、" + len(file_path_list) + "のファイルをしています。 引数のfile_path_listを調整してください\n")
            return 0
        for vector, file_path in zip(vectors, file_path_list):
            f = open(file_path, 'w')
            number = 0
            for unit in vector:
                if unit > 0:
                    f.write(str(number) + ':' + str(unit) + '\n')  # index:freq
                number+= 1
            f.write('\n')
            f.close()
        return 0


    def load(self, file_path_list):
        '''
        vectorファイルのリストからからndarrayを生成する
        '''
        vector_path_list = sorted(file_path_list)
        self.file_list = vector_path_list
        vectors = np.zeros([len(vector_path_list), len(self.index)])  # 行: 各テキスト, 列: 各素性
        number = 0  # 何行目か
        for vector_path in vector_path_list:
            f = open(vector_path, 'r')  
            for units in f:
                index_value = units.strip().split(':')
                if index_value == ['']:  # 末尾
                    continue
                vectors[number][int(index_value[0])] = index_value[1]
            number += 1
        return vectors

    def calculate_IDF(self,X):
        '''
        X => n_vector => IDF_vectorの順で計算する。
        '''
        N = X.shape[0] #  総記事数
        words = X.shape[1] #  素性単語の数
        n_vector = [0 for i in range(words)]  # 単語の数だけリストを静的確保、初期値はゼロ
        for article in X:
            for i in range(len(article)):
                if article[i] >= 1:  # もしその文書がその語を含むなら
                    n_vector[i] += 1
        
        IDF_vector = [0 for i in range(words)]
        for i in range(len(n_vector)):
            try:
                IDF_vector[i] = 1 + math.log10(N / n_vector[i])
            except:
                IDF_vector[i] = 1.0
        return (IDF_vector)

    def get_vector(self, file_path_list, filter=0,list = []):
        '''
        treeのファイルのリストを受け取って、indexに従ってvectorizeする.
        vectorsの形はndarray, 横は素性の次元数, 縦は文章の数
        filterは、indexそれぞれに重みを掛ける部分: とりあえずの実装は、
        filter:0 -> 全てそのまま
        filter:1 -> 名詞のみで構成されているものは使う
        filter:2 -> ひとつでも名詞が入っていれば使う
        例えば、 努力/名詞_する/動詞 などは、filter = 0, 2ならそのままCountされ, 1の時はCountされない。
        注) Countされないだけで、Indexで作った次元は保たれる(すなわち、努力/名詞_する/動詞 の次元は残る(ただし値は0))

        01/17 by ikko
        filter:3を追加.
        filter:3 -> 名詞,動詞,形容詞が入っていれば使う

        02/14 by ikko
        ホワイトリスト処理を追加.第四引数に’どうしても素性にしたい’単語をリストとして入れておく
        もしシソーラス・ファイルにホワイトリスト項目が記載されていれば、それは閾値に関わらず素性としてカウントする
        '''
        for number in [0, 1, 2, 3]:  # filterが正しいか判定
            if filter == number:
                correct_flag=True
        if not correct_flag:
            print('filterの値は0,1,2のいずれかに指定してください')  # error messageに
            sys.exit(1)

        try:
            self.unigram  # Indexをロードしているかをチェック
        except:
            sys.stderr.write('Indexを読み込んでいません .load(index_path)でIndexを読んでください')
            return 0
        PARSER = Parser()
        tree_list = [PARSER.load(file_path_list)]  # かかり受けの結果を読み出す
        self.file_list = PARSER.file_list  # ファイルリストを受け取り
        text_list = []
        if self.unigram == 1:
            text = [0]
            for tree in tree_list:
                text.extend(Index().tree2unigram(tree))
            text.pop(0)
            text_list.append(text)
            print("unigram...done")

        if self.bigram == 1:
            text = [0]
            for tree in tree_list:
                text.extend(Index()._tree2bigram(tree))
            text.pop(0)
            text_list.append(text)
            print("bigram...done")

        if self.trigram == 1:
            text = [0]
            for tree in tree_list:
                text.extend(Index()._tree2trigram(tree))
            text.pop(0)
            text_list.append(text)
            print("trigram...done")

        if self.dep_bigram == 1:
            text = [0]
            for tree in tree_list:
                text.extend(Index()._tree2dep_bigram(tree))
            text.pop(0)
            text_list.append(text)
            print("dep-bigram...done")

        if self.dep_trigram == 1:
            text = [0]
            for tree in tree_list:
                text.extend(Index()._tree2dep_trigram(tree))
            text.pop(0)
            text_list.append(text)
            print("dep-trigram...done")
        if text_list == []:
            sys.stderr.write('Error: 追加すべき素性が存在しません。 文書が空か、一つも使う素性種を選択していない可能性があります\n')
            return 0
 
        text_mixed = []  # 上記のtext_listは、unigram, bigram...とそれぞれが独立したリストになっているため、各articleごとにまとめる
        for number in range(0, len(text_list[0])):
            article = ''
            for feature_type in text_list:
                article = article + ' ' + feature_type[number]
            article = article.replace('UNK','名詞')
            text_mixed.append(article) 
            article = ''
        number = 0  # 行列のどのテキストを指すか
        vectors = np.zeros([len(text_mixed), len(self.index)])  # 行: 各テキスト, 列: 各素性
        for article in text_mixed:
            for unit in article.split():
                # ここからfilter
                if self._decision_use(unit, filter):  # filterにひっかかたら加算しない
                    continue
                # ここまでfilter
                if unit in self.index:
                    vectors[number][self.index[unit]] += 1  # Index番号のところを+1
                else:
                    vectors[number][self.index['UNKNOWN']] += 1
            number += 1
        return vectors

    def _iswhite(self,unit,list):
        '''
        その語はホワイトリストに登録されている？
        '''
        for elem in list:
            if elem in unit:
                return True
        return False

    def _decision_use(self, unit, filter):
        '''
        get_vectorでfilterにそのunitがかかるかを判定する. 利用しない時は1を返す
        '''
        if filter==0:  # 無条件で通す
            return 0
        if filter==1:  # 名詞のみを通す
            unit.replace('__', '_')  # 正規化
            word_poss = unit.split('_')
            for word_pos in word_poss:
#                if not re.search(u'/名詞', word_pos):  # 一つでも名詞が入っていなかったら
                if (not re.search(u'/名詞', word_pos)) and (not re.search(u'/形容詞', word_pos)) and (not re.search(u'/動詞', word_pos)) and (not re.search(u'/形容動詞', word_pos)): # 名詞、形容詞、動詞がなかったら
                    return 1
#                elif (re.search(u'/助動詞', word_pos)) or (re.search(u'/感動詞', word_pos)):
#                    return 1
                    
            return 0
        if filter==2:  # 名詞が一つでもあれば通す
            if re.search(u'/名詞', unit):  # 名詞という言葉が入っていたら(厳密には品詞をみないといけないけどとりあえず)
                return 0
            else:
                return 1
        if filter==3: #名詞/動詞/形容詞モード
            if re.search(u'/名詞', unit) or re.search(u'/動詞', unit) or re.search(u'/形容詞', unit) or re.search(u'/形容動詞', unit):
                return 0
            else:
                return 1

    def tfidf_transform(self, vectors):
        '''
        vectorsをtfidfに変換する
        '''
        list_for_count = [0] * len(vectors[0])  
        for document in vectors:
            number = 0  # 今アクセスしている要素番号
            for word_score in document:
                if word_score > 0:  # count
                    list_for_count[number] += 1
                number += 1
        if list_for_count[0] == 0:  # UNKNOWNは存在しない可能性がある
            list_for_count[0] = 1
        idf_list = []
        for count in list_for_count:
            try:
                idf_list.append(math.log(len(vectors)/count))
            except:  # zero割の時 
                idf_list.append(0)
        idf_array = np.array(idf_list)
        tfidf_array = np.zeros(len(vectors[0]))  # vstack用に一時的にゼロベクトルをおく
        col_sum = np.sum(vectors, axis=1)  # 行 方向のsum
        for vector, vector_sum in zip(vectors, col_sum):
            if vector_sum == 0:  # 一つもベクトルが立っていない時は、tfがzero割になってしまいnanになってしまうので、回避
                vector_sum = 1
            tf = vector / vector_sum  # tf
            vector = tf * idf_array  # tf_idf計算
            tfidf_array = np.vstack((tfidf_array, vector))
        return tfidf_array[1:]  # vstack用のzeroベクトルを削除

    def save_IDF(self,vector,path):
        '''
        IDFベクトルを保存するためのもの。
        save関数と同じような動作だが、条件分岐が複雑になるため切り出している。
        '''
        f = open(path, 'w')
        number = 0
        for unit in vector:
            if unit > 0:
                f.write(str(number) + ':' + str(unit) + '\n')
            number += 1
        f.write('\n')
        f.close()
        return 0

    def load_IDF(self, IDF_path):
        '''
        IDF.indexを読むためのもの。
        '''
        IDF = []
        f = open(IDF_path, 'r')
        for units in f:
            if units == '\n': # 終点
                continue
            index_value = units.strip().split(':')
            IDF.append(index_value[1])
        vectors = np.asarray(IDF,dtype = np.float64)
        return vectors

    def tfidf_save(self,vector,path):
        '''
        tfidf化されたクエリのベクトルを既定の場所に保存する
        '''
        f = open(path, 'w')
        number = 0
        vector = vector.flatten()
        for unit in vector:
            if unit > 0:
                f.write(str(number) + ':' + str(unit) + '\n')  # index:freq
        number+= 1
        f.write('\n')
        f.close()
        return 0

    def get_cos_sim(self, input_vectors, corpus_vectors):
        '''
        input_vectorsのcorpus_vectorsとの類似度を返す(cos_simmirarity)
        返り値はsim_matrix
        '''
        sim_matrix = []
        for input_vector in input_vectors:
            sim_vector = []
            sim_list = []
            for corpus_vector in corpus_vectors:
                if not input_vector.size == corpus_vector.size:
                    print('Error:次元が違います:input_vector=', input_vector.size, 'corpus_vector=', corpus_vector.size)
                    return 0
                corpus_vector = np.squeeze(np.asarray(corpus_vector))
                sim_vector.append(1-cosine(input_vector, corpus_vector))  # ここcosineが1-cosine距離で定式している?
            np.set_printoptions(precision=8)
            sim_vector = np.nan_to_num(sim_vector)
            sim_matrix.append(sim_vector)
        return sim_matrix
