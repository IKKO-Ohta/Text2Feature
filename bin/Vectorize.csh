
#set PATH = $argv[1]
#echo $PATH
#given /corpus/newtext
#given /auto/indexpath
#mkdir /auto/ newtext,newtree,newvector
#set TEXTPATH = ../corpus/newtext/*.txt
set TEXTPATH = $argv[1]
set INDEXPATH = ../auto/makeIndex/test.index
set AUTOTEXTPATH = ../auto/newtext
set TREEPATH = ../auto/newtree
set VECTORPATH = ../auto/newvector/q.vector
set TFIDFPATH = ../auto/tfidf_newvector/query.vector
set CORPUSPATH = ../auto/vector


#-------------------------------------------------------------------------------------
#                        main
#-------------------------------------------------------------------------------------
echo '初期化中です'
#rm -r $AUTOTEXTPATH
#rm -r $TREEPATH
#rm -r $VECTORPATH
#mkdir $AUTOTEXTPATH
#mkdir $TREEPATH  
#mkdir $VECTORPATH

python -i  Vectorize.py $TEXTPATH $INDEXPATH $VECTORPATH $TFIDFPATH 

#-------------------------------------------------------------------------------------
#                        end
#-------------------------------------------------------------------------------------
