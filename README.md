Text2Feature
====

Overview
Text2Featureは京都大学 情報学研究科の学生によって開発された文書検索エンジンです。
大量の日本語文書をプログラムに扱いやすいよう変換し、指定された文書と似た文書をデータベースから探し出します。
## Description
よりエンジニア向けにいうと、Text2Featureは、日本語の文書を受け取り、形態素解析や依存構造解析をおこなった後にTF-IDF法によりベクトル化するプログラムです。クエリ文書に対しても同様の処理をおこない、cosine類似度によって類似文書を検索します。 
Text2FeatureはUNIX環境でお使いいただけます。

## Beautiful points

Text2Featureの特色として、依存構造を加味したn-gramのトークンを素性としてカウントすることができます。  
これをDep-Ngramと呼び、Unigram,Bigram,Trigram,に加え、Dep-Bigram,Dep-Trigramを素性として設定することができます。

## solution
SHARP CLOUD LABSの「QAコミュニケーションシステム」にT2Fが採用されました。  
詳細は[公式ホームページ]()をご覧ください。

## Requirement
 EDA
 KyTea
 のセットアップが必要です。 導入にあたっては  
[公式ホームページ](http://plata.ar.media.kyoto-u.ac.jp/tool/Text2Feature/t2fdoc/_build/html/Tutorial.html)
 も参考にしてください。

## Usage
`$cd Text2Feature/bin`
`$csh MakeIndex.csh`
`$csh Vectorize.csh [target.txt]`

## Install
ダウンロードにはGitHubを利用します。  
`$ git clone t2f`

T2Fの利用にはKyTea,EDAのモデルが必要です。  
[モデル](http://www.ar.media.kyoto-u.ac.jp/tool/Text2Feature/models.zip)より、ふたつのモデルファイルをダウンロードしてください。  
モデルファイルはmodel/に配置してください。

## Licence

[MIT](https://github.com/tcnksm/tool/blob/master/LICENCE)

## Author
Atsushi Ushiku(初代リーダー)  
Ikko Ohta(現リーダー)  
Ryo Tomori(開発)  

Shinsuke Mori（指導）
