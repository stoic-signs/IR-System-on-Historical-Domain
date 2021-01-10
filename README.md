_______________________________________________________________________________________________________

I N F O R M A T I O N  &nbsp;  R E T R I E V A L  &nbsp;  S Y S T E M  &nbsp;  O N  &nbsp;  H I S T O R I C A L  &nbsp;  D O M A I N
_______________________________________________________________________________________________________

Contributors
------------------------------

Aditi Verma - S20180010006 / aditi.v@18iiits.in
Nethra Gunti - S20180010061 / nethra.g18@iiits.in

------------------------------
GitHub Repo Link
------------------------------

https://github.com/NethraGunti/IR-System-on-Historical-Domain

------------------------------
Drive Link For the Dataset
------------------------------

https://drive.google.com/drive/folders/1rexOv4GayD3v2CEqbDinUqHhqOx869a6?usp=sharing

------------------------------
KEY POINTS TO REMEMBER
------------------------------

>  This project has been done in PYTHON 3.8.
   (look at REQUIREMENTS.TXT for detailed list of requirements)

>  The database used is SQLITE

>  The outputs of the parts including crawling, indexing and databse creation have been included in this project already.
   The dataset being huge fails to run these parts on an ordinary computer so they have been ran and saved with the help of online virtual environments like Google Colab.
   So please do not attempt to rebuild the database unless you have atleast 15GB of RAM. Otherwise, your computer might crash.

>  The steps to test the remaining features have been mentioned below.

_______________________________________________________________________________________________________

INTRODUCTION
------------------------------

This project contains the implementation of a domain specific IR system for the historical domain. The dataset consists of
about 260,000 documents all of them crawled using 'Wikipedia-API'.
In this implementation several IR concepts like Indexing, Boolean Retrieval, Term Weighting etc. have been applied.


_______________________________________________________________________________________________________

COMPONENTS
------------------------------

Following are the comoponents of this IR system:

1.  Web Crawling
2.  Indexing (Positional & Inverted)
3.  Boolean Retrieval (AND retrieval)
4.  Ranked Retrieval  (Term Weighting)
5.  Search
6.  Query Spell Checker
7.  Categorical Search
8.  Key Figures
9.  Recommended Articles


------------------------------
DATABASE SCHEMA
------------------------------

DOCTABLE -> < DOCID, DOCTITLE, WORDCOUNT >
	description: table containing all the docids, their filenames and the number of words in the said file
TERMSTABLE-> < TERMID, TERM, DOCCOUNT >
	description: table containing all the termids, the terms themselves and the number of documents they occur in
POSITIONALINDEX -> < TERMID, DOCID, POSITIONS, TERMCOUNT >
	description: table containing the positional and inverted indices of the terms in detail.
TAGSTABLE -> < TAGID, TAG, DOCIDS >
	description: table containing all the tags and their documents


------------------------------
DATAFILE FORMAT
------------------------------


file = 	{
		'title' : Document Title,
		'url' : Document URL,
		'tags' : Document Tags,
		'text' : Document Text/Body
	}


_______________________________________________________________________________________________________

INDIVIDUAL FILE/FOLDER DESCRIPTION
------------------------------

1. main.py    : The running point for the searches

2. dataset/   : The folder containing 260,000+ data documents

3. index/     : The folder where all the indices including the temporary and the final one go to

4. db_init.py : The database initializer which creates all the required tables.

5. db_write.py: The file that writes to the database after creation of the indices

6. inverted_index.py: The file that creates the inverted indices for every document.

7. merge.py   : The file that iteratively merges the created indices into one single big index

8. spell.py   : The file that checks spelling errors in the query phrase

9. crawl.py   : The file which crawls from the web

10. key_figures.py   : The file which uses NER to find key figures in the fetched document.

11. doc_titles.txt : File with all the document titles that are retrieved

12. exclude_cats.txt : File with the list of categories that are to be excluded during crawling


_______________________________________________________________________________________________________

STEPS TO RUN A SEARCH
------------------------------

> pip install requirements.txt

> python main.py

> select one of the four options: Query, Category, Fetch and Exit.

> Query: enter your search query. All results will be displayed in the descending order of their cosine similarity score with the query.

> Tag: search for all the documents in a given tag. Enter your tag. The query will be treated as a single entity (tag), instead of its comprising tokens.

> Fetch: enter a DocID for the document you wish to fetch. It will display all relevant details, key figures and simillar docs.

> Exit: exits the program.
