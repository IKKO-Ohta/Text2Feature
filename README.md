# Text2Feature Documentation
-------------------
更新履歴
-------------------

-------------------
How to use.
-------------------

csh refresh.csh		
csh MakeIndex.csh
csh Vectorize.csh [任意のテキストファイル]

-------------------
ファイル構造
-------------------

Text2Feature
- auto/ : bin/test.cshによって生成される途中経過
  - test.index	MakeIndex.cshで作られる単語orN-gramなどのtf(頻度のみ)
  - text/ 　	MakeIndex.cshで作られる前処理済みのデータのテキスト
  - tree/ 	MakeIndex.cshで作られるparsedのデータのテキスト
  - vector/	MakeIndex.cshで作られるベクトル
  - newtext/	Vectorize.cshで作られる前処理済みのクエリテキスト
  - newtree/	Vectorize.cshで作られるparsedのテキスト
  - newvector/	Vectorize.cshで作られるベクトル
- bin/
  - MakeIndex.csh	検索されるデータ側の処理の実行ファイル。 auto/test.indexとauto/vectorをcorpus/text/から作り出す
  - MakeIndex.py	
  - Vectorize.csh	クエリ側の処理の実行ファイル。 test.indexを利用して、corpus/newtext/からauto/newvectorを作る
  - Vecotrize.py	クエリファイルをtest.indexを使ってベクトルにする
  - refresh.csh		中間ファイルを削除して初期状態にする	
- corpus/
  - text/	検索されるデータ側
  - newtext/	クエリ側
- lib/: bin/から呼び出すライブラリ群
  - perl/
  - python/
    - index.py		indexを作成する周り	
    - parse.py		parsing周り
    - preprocess.py	前処理周り
    - vectorizer.py	ベクトライズ周り
- model/
  - bccwj-20140727.etm: EDAモデル
  - model-OC-test.ebm :EDAモデル（軽量）
  - model.bin: KyTeaモデル


-------------------
関数など
-------------------

- index.Index(unigram=1, bigram=0, trigram=0, dep_bigram=0, dep_trigram=0)
  - methods
    - add_index(folder_path): 指定したフォルダ内にあるtreeから、Indexに追加する
    - save(file_path):  '''
        		self.indexをfile_pathの出現頻度降順で出力する.
		        また、一行目にどの素性を利用しているかを書く。
        		例)---------------------------------------
        		unigram, bigram, trigram, dep-bigram, dep-trigram:1 0 0 0 1
        		元気 10
        		いい 10
        		人 9
        		は 9
        		:
        		-------------------------------------------
        		'''
    - load(file_path): saveで保存したfile_pathからindexを読み込む。現在あるself.indexは上書きされる。

  - attribute	       
    - unigram: ungramを使うかどうかのフラグ
    - bigram: 同様
    - trigram: 同様
    - dep_bigram: 同様
    - dep_trigram: 同様
    - index: 現在のインスタンスの持つindex
    - dict: NKNOWNで潰す用の出現頻度のdict

- parse.Parser()
  - methods
    - kytea(folder_path, kytea_model=None, pipe_eda=False): kyteaの結果を返す
    - eda(input_kytea, eda_model='', pipe_kytea=False): edaの結果を返す
    - t2f(folder_path, kytea_model=None, eda_model=''): kytea->edaを行う
    - save(folder_path): folderにtreeを保存する
    - load(folder_path): folder以下のtreeを読み出す
  - attribute
    - parsed: edaの結果
    - text_list: 読み出したファイル名のリスト(tree or text)

- preprocess.Preprocessor()
  - methods
    - load_text(folder_path): folder以下にあるtextをpreprocessする
    - save(folder_path): folder_pathに保存する
  - attribute 
    - file_list: 読み出したファイル名のリスト
    - preprocessed: preprocessされたtext/ [sentenceA-1, sentenceA-2],[senctenceB-1,...][][] という構造

- vectorizer.Vectorizer(file_path, t=5): # tは閾値. 閾値以下の頻度はUNKNOWNに潰す
  - methods
    - _load_index(file_path, t=5):  indexを読み出す
    - save(vector, file_path_list): vectorizeしたものを保存する
    - load(file_path_list):	    vectorファイルからndarrayを生成する
    - get_vector(file_list): 	    treeのリストを受け取って、indexに従ってvectorizeする.
        		       	    vectorの形はndarray, 横は素性の次元数, 縦は文章の数
    - tfidf_transform(vectors):     vectorsの中でtfidfに変換する. 検索対象のベクトルと検索するベクトルをndarrayで固めて、変換した後にもう一度分割する。
    - sim_example_cos(input_vector, corpus_vector): input_vectors と corpus_vectorsのcos_simを計算して、matrixを返す.
  - attribute
    - file_list: 読み込んだファイル名のリスト
# Text2Feature
