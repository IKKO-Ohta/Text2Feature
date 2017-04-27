#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import re
import itertools
import glob
from collections import OrderedDict 
import numpy as np


class Preprocessor:
    '''
    vectorizeするためのindexを扱うクラス
    '''
    def __init__(self,path = None):
        self.file_list = []  # inputのファイルネームのリスト
        self.preprocessed = [[]]  # [[sentenceA-1, sentenceA-2],[senctenceB-1,...][][] という構造
        self.thesaurus = OrderedDict()

        def check_th(path):
            '''
            一度集合を噛ませることでシソーラス重複をチェックする。
            '''
            f = open(path,'r')
            registed = []
            for words in f:
                if re.search(u'#', words):
                    continue
                words = words.rstrip().split(' ')
                for word in words:
                    registed.append(word)
            if sorted(registed) != sorted(list(set(registed))):
                print('warning:シソーラス内に重複があります。')
            f.close()

        if path != None:
            check_th(path)
            th_file = open(path,'r')
            TBIlist = []
            for words in th_file:
                if re.search(u'#', words):
                    continue
                synonym = []
                synonym = words.rstrip().split(' ')
                if synonym[0] != 'TBI':
                    self.thesaurus[synonym[0]] = synonym  # dict['孫づる'] = ['孫づる', '孫ヅル', '孫蔓', 'まごづる'] 
                else:
                    for elem in synonym[1:]:
                        TBIlist.append(elem)
            self.thesaurus['TBI'] = TBIlist
            th_file.close()

    def load_text(self, file_path_list):
        '''
        folder_pathにあるtextファイルを読み込む
        '''
        file_list = sorted(file_path_list)
#        file_list = sorted(glob.glob(folder_path + '/*'))
        self.preprocessed = []
        self.file_list = file_list
        for text_path in file_list:
            f = open(text_path, 'r')
            article = []
            for sentence in f:
                sentence = sentence.strip()  # 以下前処理部分
                if sentence == '':  # 空行は削除
                    continue
                for repr_word,synonym_list in self.thesaurus.items():  # synonym辞書を参照し、代表語に置換
                    for synonym_word in synonym_list:
                        sentence = sentence.replace(synonym_word,repr_word)
                sentence = sentence.replace('-', 'ー')  # - を変換
                sentence = sentence.replace('_', '＿')  # _(アンダースコア)を変換
                sentence = sentence.replace('UNK', 'Unk')  # UNKの重複を避けるため
                sentence = sentence.replace('UNKNOWN', 'Unknown')  # UNKNOWNの重複を避けるため
                
                article.append(sentence)
#            print('replaced',article)
            self.preprocessed.append(article)
        return 0

    def save(self, folder_path):
        '''
        folder_pathにファイルを保存する
        '''
        for file_name, sentences in zip(self.file_list, self.preprocessed):
            base_name = os.path.basename(file_name)  # A.text
            root = os.path.splitext(base_name)[0]  # A
            f = open(folder_path + '/' + root + '.text', 'w')  # A.text
            for sentence in sentences:  # 各ファイルに書き込む
                f.write(sentence + '\n')
            f.close()
        return 0

    def investigate_whitelist(self,path):
        '''
        02/14 by ikko
        ホワイトリスト機能の分割を目標に作成された。
        シソーラスファイルは、ホワイトリスト機能やブラックリスト機能もあわせもっている。
        ホワイトリスト機能は、シソーラスファイルに’１語’しか含まれていない行があったら、それを素性とするもの。
        :param path: シソーラスファイル
        :return: ホワイトリスト
        '''
        self.whitelist = []
        with open(path) as f:
            for line in f:
                if len(line.split(' ')) == 1:
                    self.whitelist.append(str(line))
        return self.whitelist
