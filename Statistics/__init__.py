import os
import re
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

if __name__ == '__main__':
    
    'Get current path'
    current_path = os.getcwd()

    'Get directory list from the Reddit miner'
    for sub_reddit_dir in REDDIT_DIRS:
        print ("Files in SUB_Reddit: " + sub_reddit_dir)
        reddit_dir=re.sub(CURRENT_MODULE_DIR, '', current_path) + REDDIT_MINER_DIR_NAME + sub_reddit_dir
        for reddit_file in os.listdir(reddit_dir):
            print("Working on File: " + reddit_file)
            xmldoc = minidom.parse(reddit_dir + "\\" + reddit_file)

            'General Newspaper statistics'
            news_paper = xmldoc.getElementsByTagName('news-paper')[0].firstChild.nodeValue 
            news_papers_stat[news_paper] = news_papers_stat.get(news_paper, 0) + 1
       
            'Bias per Newspapers '
            if sub_reddit_dir in DEM_SUB_REDDIT:
                bias_news_paper["Democrats"][news_paper] = bias_news_paper["Democrats"].get(news_paper, 0) + 1
            else:
                bias_news_paper["Republicans"][news_paper] = bias_news_paper["Republicans"].get(news_paper, 0) + 1    
            
            'Get Author Names'
            author_name = xmldoc.getElementsByTagName('author')[0].firstChild.nodeValue 
            authors_stat[news_paper] = authors_stat.get(news_paper, 0) + 1
            
            'Bias per Authors'
            if sub_reddit_dir in DEM_SUB_REDDIT:
                bias_authors["Democrats"][author_name] = bias_authors["Democrats"].get(author_name, 0) + 1
            else:
                bias_authors["Republicans"][author_name] = bias_authors["Republicans"].get(author_name, 0) + 1    
            

            print ("****** Completed Statistics Calculation ******")
    
    'Print General News Papers statistics'
    for key, value in news_papers_stat.items():
        print('{} : {}'.format(key, value))
        
    'Print Bias News Papers statistics'
    for party in bias_news_paper.items():
        print ("---" + party[0] + ": ")
        for key, value in party[1].items():
            print('{} : {}'.format(key, value))
            
    'Print General Authors statistics'
    for key, value in authors_stat.items():
        print('{} : {}'.format(key, value))
           
    'Print Bias Authors statistics'
    for party in bias_authors.items():
        print ("---" + party[0] + ": ")
        for key, value in party[1].items():
            print('{} : {}'.format(key, value))