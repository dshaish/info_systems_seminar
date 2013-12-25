import praw
import csv
import re
import os
import http.cookiejar
import urllib.request
from pprint import pprint
import Scraper
import traceback


REP_SUB_REDDIT={"republicans", "Republican", "Romney"}
DEM_SUB_REDDIT={"democrats", "Democrat", "obama"}
CENTER_SUB_REDDIT={"ModerateRepublican", "ModerateDemocrate"}
SUB_REDDIT= set(list(DEM_SUB_REDDIT) + list(REP_SUB_REDDIT))
SUPPORTED_NEWS_SITES=["nytimes.com", "usatoday.com","washingtonpost.com"]
BAD_USERS=[""]
VOTE_TRESHHOLD=0

' Limit of number of articles per newspaper'
ARTICLE_LIMIT_NP = 1000

'Users to disregard'
IGNORED_USERS={}

'''
    * Prepare the CSV file and Headline 
'''
def prepare_csv_file(file, section_name):
    csv_writer = csv.writer(file,delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow((""))
    csv_writer.writerow((""))
    csv_writer.writerow((""))
    csv_writer.writerow(("", "Section :", section_name))
    csv_writer.writerow(('ID', 'REDDIT_ID', 'SCORE', 'Title', 'URL', 'PERMALINK', 'SOURCE'))
    return csv_writer

if __name__ == '__main__':
    
    ' Create Filw for reddit data base '
    target_file_name="reddit.csv"
    file = open(target_file_name,'w+', newline="\n")

    ' PRAW library preparations'
    r = praw.Reddit(user_agent='iss_reddit_miner v0.2 /u/dshaish')
    r.login("dshaish", "lc6tX23x")
    cj = http.cookiejar.CookieJar()
    url_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    counter = 0
    
    'Iterate sub reddits :'
    for sub_reddit in SUB_REDDIT:
        
        ' Prepare the directory per sub_reddit'
        if not os.path.exists(str(sub_reddit)):
            os.makedirs(str(sub_reddit))
                
        ' Get the CSV file ready and write headline'
        csv_writer = prepare_csv_file(file, sub_reddit)
        
        ' Clear internal IDs '
        article_id = 1
         
        ' Iterate over all news supported newspapers '
        for newspaper in SUPPORTED_NEWS_SITES:
            
            print (" ****** Getting Posts from: " + sub_reddit + " From Newspaper: " + newspaper + " ******")
            
            ' Clear newspaper limit '
            newspaper_limit = 0
            
            'Query the data base ' 
            query_string = str("site:" + newspaper)
            submissions = r.search(query = query_string, subreddit = sub_reddit)
        
            ' Iterate the submissions '
            for sub in submissions:
                try:
                    
                    'Accept only posts with comments'                  
                    if (sub.score < VOTE_TRESHHOLD):
                        continue
                    
                    'Open File with article id as the name'
                    article_file = open(str(sub_reddit) + "\\" + str(article_id), 'w+', newline="\n")
                    article_file.write("<article>\n")
                    article_file.write("<sub-reddit>" + sub_reddit + "</sub-reddit>\n")
                    article_file.write("<news-paper>" + sub.domain + "</news-paper>\n")
                    article_file.write("\n")         
                    stripped_title = Scraper.string_cleaner(sub.title)
                    article_file.write("<title>" + stripped_title  + "</title>\n")
                    
                    'Get the article content'
                    if (SUPPORTED_NEWS_SITES[0] in sub.domain):
                        success = Scraper.ny_times.get_HTML_article(url_opener, article_file, sub.url)
                    elif (SUPPORTED_NEWS_SITES[1] in sub.domain):
                        success = Scraper.usa_today.get_HTML_article(url_opener, article_file, sub.url)
                    elif (SUPPORTED_NEWS_SITES[2] in sub.domain):
                        success = Scraper.washington_post.get_HTML_article(url_opener, article_file, sub.url)
                    else:
                        success = False 
                    'Close the XML file'
                    article_file.write("</article>\n")
                    
                    'Found articles counter'
                    if success :
                        
                        'Total units counter '
                        counter += 1
                    
                        ' Print to screen and to CSV the reults'
                        print(str(counter) + ': FOUND' +'('+ str(article_id) +'): ' + str(sub) + "(" + str(sub.domain) + ")")
                        csv_writer.writerow((article_id, sub.id, sub.score, re.sub(r'\,', '', sub.title), sub.url, sub.permalink, sub.domain))
                    
                        'increment counters'
                        article_id +=1
                        newspaper_limit += 1
                        
                    ' Close single article file'
                    article_file.close()
                    
                    'Limit the articles found'
                    if (newspaper_limit == ARTICLE_LIMIT_NP) :
                        break
                except:
                    try:
                        print(traceback.format_exc())
                        print("ERROR: Failed to get: " + print(str(sub)))
                    except:
                        print("ERROR: Failed to get number: " + str(counter))

    file.close()
    print("Completed REDDIT mining successfully")