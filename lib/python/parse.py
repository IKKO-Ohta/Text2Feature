#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob
import os.path
import re
import sys
import shutil
import subprocess
import codecs
from collections import Counter

class Parser:

    def __init__(self):  # 初期化とKyTea,EDAのコマンドがインストールされているか確認
        '''
        kytea,edaのインストールしているかの確認 
        以下の2つのコマンドだと終了ステータスが0ではないのでエラーが返ってくる
        終了ステータス1のときは成功としたが、環境によって異なるのかは分からん
        '''
        self.parsed = []  # parsingの結果  # .load or .eda で更新
        self.text_list = []  # 読み込んだファイル名のリスト  # load or kyteaで更新 
 
        if shutil.which('kytea'):
            pass
        else:
            sys.stderr.write('"kytea"のコマンドが使えません' + '\n')
            sys.stderr.write('正しくインストールされているか確認してください' + '\n')
            sys.stderr.write('http://www.phontron.com/kytea/index-ja.html' + '\n')
            sys.exit(1)

        try:
            output_test = subprocess.check_output('eda', shell=True)
        except subprocess.CalledProcessError as e:
            returncode = e.returncode
            if returncode == 1:
                pass
            else:
                sys.stderr.write('"eda"のコマンドが使えません')
                sys.stderr.write('正しくインストールされているか確認してください')
                sys.stderr.write('http://www.ar.media.kyoto-u.ac.jp/tool/EDA/')


    def kytea(self, file_path_list, kytea_model=None, pipe_eda=False):        
        '''
        KyTeaコマンド実行部分
        '''

        def check_UNK(line):
            '''
            kyteaがUNKを吐く場合への対応 3/19
            '''
            if 'UNK/UNK/UNK' in line:
                counter = Counter(line)
                sys.stderr.write('Warning:')
                sys.stderr.write(str(counter['UNK/UNK/UNK']))
                sys.stderr.write('UNK replaced ...' + '\n')
                line = line.replace('UNK/UNK/UNK','名詞/UNK/UNK/')
            return line

        input_f = sorted(file_path_list)
#        input_f = sorted(glob.glob(folder_path + '/*'))
        self.file_list = input_f

        if kytea_model is None:  # コマンドの定義、モデルを何にするかを決定
            cmd_kytea = 'kytea'
        else:
            cmd_kytea = 'kytea -model ' + kytea_model

        input = ""  # 複数ファイルをつなげる。ファイル終端にはEOFを追加
        for file_iter in input_f:
            input = input + open(file_iter, 'r').read()
            input = input + 'EOF\n'

        process_kytea = subprocess.Popen(cmd_kytea.strip().split(" "), stdin=subprocess.PIPE, stdout=subprocess.PIPE)  # kytea実行部分
        output_kytea = process_kytea.communicate(input.encode('utf-8'))[0]
        output_kytea = check_UNK(codecs.decode(output_kytea)).encode('UTF-8')  # 3/18 UNK対応
        if pipe_eda == False:   # False ならEOFごとに区切って、UTF-8にしてリスト型で返す
            kytea_line_list = output_kytea.decode('utf-8').split("\n")  # kyteaの出力を整形、EOFで区切ってlistに追加するために
            EOF_kytea = kytea_line_list[output_kytea.decode('utf-8').count('\n') - 1]
            EOF_kytea = EOF_kytea + '\n'  # kyteaのEOFの出力を取得したり、それで分割したり、文字コード考慮したり
            output_kytea_list = output_kytea.split(EOF_kytea.encode('utf-8'))
            for i in range(len(output_kytea_list)):
                output_kytea_list[i] = output_kytea_list[i].decode('utf-8')

            output_kytea_list.pop()
            return output_kytea_list
        else:  # True ならEDAに渡すためにそのまま返す
            return output_kytea


    def eda(self, input_kytea, eda_model='', pipe_kytea=False):
        '''
        EDAコマンド実行部分
        '''
        cmd_eda = 'eda -m ' + eda_model + '  -i kytea'  # コマンドの定義、モデルを何にするかを決定

        process_eda = subprocess.Popen(cmd_eda.strip().split(" "), stdin=subprocess.PIPE, stdout=subprocess.PIPE)  # eda実行部分
        if pipe_kytea == False:
            input = ''
            for line in input_kytea:
                input += line
                input += 'EOF/名詞/いーおーえふ\n'
                
            output_eda = process_eda.communicate(input.encode('utf-8'))[0]
        else:
            output_eda = process_eda.communicate(input_kytea)[0]

        eda_line_list = output_eda.decode('utf-8').split("\n")  # EDAの出力を整形、EOFで区切ってlistに追加するために
        EOF_eda = eda_line_list[output_eda.decode('utf-8').count('\n') - 2]  # EDAのEOFの出力を取得したり、それで分割したり、文字コード考慮したり

        EOF_eda = EOF_eda + '\n'
        output_eda_list = output_eda.split(EOF_eda.encode('utf-8'))
        for i in range(len(output_eda_list)):
            output_eda_list[i] = output_eda_list[i].decode('utf-8')

        output_eda_list.pop()
        
        new_article = []
        parsed = []
        for article in output_eda_list:  # parsingの結果をリストにする
            if article == b'\n':
                continue
            sentences = article.split('ID=')
            sentences.pop(0)
            for sentence in sentences:
                units = sentence.split('\n')
                units.pop(-1)
                units.pop(-1)
                try:
                    units.pop(0)
                    new_article.append(units)
                except:
                    pass
            parsed.append(new_article)
            new_article = []
        self.parsed = parsed  # parsingの結果を更新
        assert parsed,'Error:EDAs are Empty' 
        return parsed

    def t2f(self, file_path_list, kytea_model=None, eda_model=''):
        '''
        KyTeaの出力をEDAに渡しただけ
        '''
        return self.eda(self.kytea(file_path_list, kytea_model, pipe_eda=True), eda_model, pipe_kytea=True)


    def save(self, folder_path):
        '''
        folder_pathにかかり受けの結果self.parsedをA.edaというファイル名で書き込む。
        '''
        for file_name, line in zip(self.file_list, self.parsed):
            base_name = os.path.basename(file_name)  # A.text
            root = os.path.splitext(base_name)[0]  # A
            id_count = 0
            f = open(folder_path + '/' + root + '.eda', 'w')  # A.eda
            for sentence in line:  # 各ファイルに書き込む
                id_count += 1
                f.write('ID=' + str(id_count) + '\n')  # parsingの結果は、IDで区切っている
                for units in sentence:  # unitsは　"1 2 私 名詞 0"のような各要素 
                    f.write(units + '\n')
                f.write('\n')
            f.close()
        return 0


    def load(self, file_path_list):  
        '''
        指定したフォルダ以下のかかり受けの結果のファイルを、受け取る。
        '''
        eda_file_path_list = sorted(file_path_list) 
#        eda_file_path_list = sorted(glob.glob(folder_path + '/*'))
        self.file_list = eda_file_path_list  # 読み込んだファイルのリストを更新
        parsed, article, units = [], [], []
        for eda_file_path in eda_file_path_list:
            for unit in open(eda_file_path, 'r'):
                unit = unit.strip()
                if re.match('ID', unit):
                    continue
                if unit == '':
                    article.append(units)
                    units = []
                    continue
                units.append(unit)
            parsed.append(article)
            article = []
        self.parsed = parsed  # かかり受け解析の結果を保持する
        return parsed
