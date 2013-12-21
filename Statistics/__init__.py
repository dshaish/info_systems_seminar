import os
import re
import csv
from xml.dom import minidom

REP_SUB_REDDIT={"republicans", "Republican", "Romney"}
DEM_SUB_REDDIT={"democrats", "Democrat", "obama"}

REDDIT_DIRS={"republicans", "Republican", "Romney", "democrats", "Democrat", "obama"}

REDDIT_MINER_DIR_NAME="Reddit_miner\\"
CURRENT_MODULE_DIR="Statistics"

'News papers statistics'
news_papers_stat = {}
bias_news_paper = {"Democrats":{}, "Republicans":{} }

'Authors statistics'
authors_stat = {}
bias_authors = {"Democrats":{}, "Republicans":{} }

'Words that must be contained in the article'
KEYWORD_TO_SEARCH=["Israel"]


'''
    General Newspaper statistics
    How many articles were received from each newspaper
'''
def get_general_newspaper_stat(xmldoc, news_paper):
            news_papers_stat[news_paper] = news_papers_stat.get(news_paper, 0) + 1

'''
    Bias Newspaper statistics
    How much times each newspaper was detected to have a republican or democrat article
'''
def get_bias_newspaper_stat(xmldoc, news_paper):
    'Bias per Newspapers '
    if sub_reddit_dir in DEM_SUB_REDDIT:
        bias_news_paper["Democrats"][news_paper] = bias_news_paper["Democrats"].get(news_paper, 0) + 1
    else:
        bias_news_paper["Republicans"][news_paper] = bias_news_paper["Republicans"].get(news_paper, 0) + 1  

'''
    General Author statistics
    How many articles were received from each author
'''
def get_general_author_stat(xmldoc, author_name):
    authors_stat[author_name] = authors_stat.get(author_name, 0) + 1

'''
    Bias Newspaper statistics
    How much times each newspaper was detected to have a republican or democrat article
'''
def get_bias_author_stat(xmldoc, author_name):
    if sub_reddit_dir in DEM_SUB_REDDIT:
        bias_authors["Democrats"][author_name] = bias_authors["Democrats"].get(author_name, 0) + 1
    else:
        bias_authors["Republicans"][author_name] = bias_authors["Republicans"].get(author_name, 0) + 1
          
'''
    
'''
def drop_stats_to_csv():
    
    ' Create File for statistics results'
    target_file_name="statistics.csv"
    file = open(target_file_name,'w+', newline="\n")
    
    ' Prepare the CSV file'
    csv_writer = csv.writer(file,delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(("","Statistical RESULTS:",))
    csv_writer.writerow((""))
    if len(KEYWORD_TO_SEARCH) !=0:
        csv_writer.writerow(("","Filtering for words:",))
        csv_writer.writerow(("",str(KEYWORD_TO_SEARCH),))
    csv_writer.writerow((""))
    csv_writer.writerow((""))
    
    'Print General News Papers statistics'
    csv_writer.writerow(("", "", "General Newspaper Statistics:"))
    csv_writer.writerow(("", "Newspaper", "# Appearances"))
    for key, value in news_papers_stat.items():
        csv_writer.writerow(("", key, value))
    csv_writer.writerow((""))
    csv_writer.writerow((""))
    
    'Print Bias News Papers statistics'
    csv_writer.writerow(("", "Bias Newspaper Statistics:"))
    csv_writer.writerow(("", "Newspaper", "# Appearances"))
    for party in bias_news_paper.items():
        csv_writer.writerow (("PARTY:", party[0]))
        for key, value in party[1].items():
            csv_writer.writerow(("", key, value))
            "print('{} : {}'.format(key, value))"
    csv_writer.writerow((""))
    csv_writer.writerow((""))
            
    'Print General Authors statistics'
    csv_writer.writerow(("", "General Author Statistics:"))
    csv_writer.writerow(("", "Author Name", "# Appearances"))
    for key, value in authors_stat.items():
        csv_writer.writerow(("", key, value))
    csv_writer.writerow((""))
    csv_writer.writerow((""))
    
    'Print Bias Authors statistics'
    csv_writer.writerow(("", "Bias Authors Statistics:"))
    csv_writer.writerow(("", "Author Name", "# Appearances"))
    for party in bias_authors.items():
        csv_writer.writerow (("PARTY:", party[0]))
        for key, value in party[1].items():
            csv_writer.writerow(("", key, value))
    csv_writer.writerow((""))
    csv_writer.writerow((""))
 

'''
    MAIN PROCESS
'''
if __name__ == '__main__':
    
    'Get current path'
    current_path = os.getcwd()

    'Get directory list from the Reddit miner'
    for sub_reddit_dir in REDDIT_DIRS:
        print ("Files in SUB_Reddit: " + sub_reddit_dir)
        reddit_dir=re.sub(CURRENT_MODULE_DIR, '', current_path) + REDDIT_MINER_DIR_NAME + sub_reddit_dir
        for reddit_file in os.listdir(reddit_dir):
            print("Working on File: " + reddit_file)
            
            'XML parse of the document'
            try:
                xmldoc = minidom.parse(reddit_dir + "\\" + reddit_file)
            except:
                continue
            
            'Get content of article'
            content = xmldoc.getElementsByTagName('content')[0].firstChild.nodeValue
            found_word=False
            for word in KEYWORD_TO_SEARCH:
                if word in content: 
                    print ("Found <" + word + "> in article - continuing with statistics")
                    found_word=True
                    break
                
            'Check if a word was found'
            if not(found_word) and (len (KEYWORD_TO_SEARCH)!=0) :
                print ("No word was found from search string - Do not run statistics on this article")
                continue
             
            ' Get newspaper name for this article'
            news_paper = xmldoc.getElementsByTagName('news-paper')[0].firstChild.nodeValue.lower() 
       
            'Get Statistics for newspapers'
            get_general_newspaper_stat(xmldoc, news_paper)
            get_bias_newspaper_stat(xmldoc, news_paper)
            
            
            'Get Author Names'
            author_name = xmldoc.getElementsByTagName('author')[0].firstChild.nodeValue.lower()
           
            'Get Statistics for author'
            get_general_author_stat(xmldoc, author_name)
            get_bias_author_stat(xmldoc, author_name)
            
            print ("****** Completed Statistics Calculation ******")
    
    'Print all results to CSV file'
    drop_stats_to_csv()