#set PATH = $argv[1]
#echo $PATH
#given /corpus/newtext
#given /auto/indexpath
#mkdir /auto/ newtext,newtree,newvector
#set TEXTPATH = ../corpus/text
#set INDEXPATH = ../auto/test.index
#set AUTOTEXTPATH = ../auto/text
#set TREEPATH = ../auto/tree
#set VECTORPATH = ../auto/vector

set TEXTPATH = ../corpus/makeIndex
set INDEXPATH = ../auto/makeIndex/test.index
set AUTOTEXTPATH = ../auto/makeIndex/text
set TREEPATH = ../auto/makeIndex/tree
set VECTORPATH = ../auto/makeIndex/vector

#set TEXTPATH = /opt/text2feature/corpus/makeIndex
#set INDEXPATH = /opt/text2feature/auto/makeIndex/test.index
#set AUTOTEXTPATH = /opt/text2feature/auto/makeIndex/text
#set TREEPATH = /opt/text2feature/auto/makeIndex/tree
#set VECTORPATH = /opt/text2feature/auto/makeIndex/vector

#-------------------------------------------------------------------------------------
#                        main
#-------------------------------------------------------------------------------------
echo '初期化中です'
rm -r $AUTOTEXTPATH
rm $INDEXPATH
rm -r $TREEPATH
rm -r $VECTORPATH
mkdir $AUTOTEXTPATH
mkdir $TREEPATH  
mkdir $VECTORPATH

python MakeIndex.py $TEXTPATH $INDEXPATH $VECTORPATH $AUTOTEXTPATH $TREEPATH

#python /opt/text2feature/bin/MakeIndex.py $TEXTPATH $INDEXPATH $VECTORPATH $AUTOTEXTPATH $TREEPATH

#-------------------------------------------------------------------------------------
#                        end
#-------------------------------------------------------------------------------------
