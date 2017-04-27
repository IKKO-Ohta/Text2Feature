```
import sys
import pdb
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from text2feature.dep2feature import Dep2Feature
from text2feature.text2dep import Text2dep


m = Text2dep()
input_list = ['input1.txt', 'input2.txt']
```
text2Featureは主に平文からかかり受け関係を求めるdep2featureと、かかり受け関係から素性を作成するtext2depという二つのクラスによってなっています。
```
input_kytea = m.kytea(input_list, kytea_model='model/model.bin')
input_eda1 = m.eda(input_kytea, eda_model='model/bccwj-20140727.etm')
```
入力として、まず、コーパスを形態素解析、構文解析します。コーパスは複数のファイルからなり、一つ一つのファイルは記事などの意味ある区切りを想定しています。
kyteaで形態素解析、edaで構文解析を行いますが、その時にモデルが必要です。
- KyTea: http://www.phontron.com/kytea/index-ja.html
- EDA: http://www.ar.media.kyoto-u.ac.jp/tool/EDA/
にそれぞれモデルが存在しているので利用すると良いでしょう。アノテーション済みのデータがあれば学習を行うこともできますが、ここでは深く説明しません。
構文解析は、モデルの読み込みに時間がかかるので、できれば結果をシリアライズするのが望ましいです
```
input_list = ['input3.txt']
input_eda2 = m.t2f(input_list, kytea_model='model/model.bin', eda_model='model/bccwj-20140727.etm')
```
また、t2fとまとめて書くこともできます

```
input_eda3 = m.load_eda(['input4.eda'])
```
かかり受け解析が住んでいるテキストファイルをそのまま読むことも出来ます。
```
input_eda4 = m.kytea2eda(input_kytea)
```
かかり受け関係を利用しない場合、kyteaの出力をEDAの出力のように書き換えられます。
かかり受けには時間がかかるため、unigram, bigram, trigramしか利用しない場合はkytea2edaを利用することをおすすめします
```
D2F = Dep2Feature([input_eda1, input_eda2, input_eda3], unigram = 1, bigram = 1, vectorizer = CountVectorizer())  # 辞書作成

vectors = D2F.vectorize([input_eda1, input_eda2])
input_vector1 = vectors[0]
input_vector2 = vectors[1]
```
インスタンスを作成しますが、引数として、辞書を作成するためのcorpusのリストを与えます。 この場合はinput_eda1~3の、unigramとbigramから辞書を生成しています
このインスタンスで、vectorizeメソッドを実行することで、引数のリストをそれぞれベクトルにします.
unigram~dep_trigramに関しては、0 or 1の値、vectorizerに関しては、scikit-learnのCountVectorizer(), TfIdfVectorizer()が利用できます。(importしておいてください) unigram, bigram、trigramに関しては、連続する、1単語、2単語、3単語をそれぞれ素性にします。(なお、1単語に関しては、1文字の単語はVectorizerの初期設定では捨てています)
dep_bigramは、構文解析による結果を利用し、かかり元とかかり先のつながりを連続する単語として素性にしています。dep_trigram に関しても、同様でかかり先のさらにかかり先までを含めて、連続する3単語と見て素性にしています。
これらの素性はそれぞれ、同時に利用することができます。
kytea2edaを使って、eda形式にしている場合は、dep_bigram、dep_trigramはそれぞれbigram, trigramと等価です。
```
sim_matrix_cos = D2F.sim_example_cos(input_vector1, input_vector2)
sim_matrix_dic = D2F.sim_example_dic(input_vector1, input_vector2)
sim_matrix_sim = D2F.sim_example_sim(input_vector1, input_vector2)
sim_matrix_jac = D2F.sim_example_jac(input_vector1, input_vector2)

print('cos類似度')
D2F.sim_print(D2F.eda2unigram(input_eda1), D2F.eda2unigram(input_eda2), sim_matrix_cos, number = 2)
```
vec同士の類似度を計算できます。ただし、類似度のmatrixを作るため計算量は多めです
