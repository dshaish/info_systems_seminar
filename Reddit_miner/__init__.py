import praw
import csv
import re
import os
import http.cookiejar
import urllib.request
from pprint import pprint
import Scraper


REP_SUB_REDDIT={"republicans", "Republican", "Romney"}
DEM_SUB_REDDIT={"democrats", "Democrat", "obama"}
CENTER_SUB_REDDIT={"ModerateRepublican", "ModerateDemocrate"}
SUB_REDDIT= set(list(DEM_SUB_REDDIT) + list(REP_SUB_REDDIT))
SUPPORTED_NEWS_SITES=["nytimes.com", "usatoday.com","washingtonpost.com"]
BAD_USERS=[""]
VOTE_TRESHHOLD=0

' Limit of number of articles per news paper'
ARTICLE_LIMIT = 2

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
    target_file_name= "reddit.csv"
    file = open(target_file_name,'w+', newline="\n")

    ' PRAW library preparations'
    r = praw.Reddit(user_agent='iss_reddit_miner v0.1 /u/dshaish')
    cj = http.cookiejar.CookieJar()
    url_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    
    'Iterate sub reddits :'
    for sub_reddit in SUB_REDDIT:
        
        ' Prepare the directory per sub_reddit'
        if not os.path.exists(str(sub_reddit)):
            os.makedirs(str(sub_reddit))
            
        ' Get the CSV file ready and write headline'
        csv_writer = prepare_csv_file(file, sub_reddit)
    
        ' Clear internal IDs '
        article_id = 1
        place_anchor = 0
        counter = 0
        
        ' Iterate over all the articles as long as the limit was not reached '
        while (article_id <= ARTICLE_LIMIT):
        
            ' Get submissions for this sub-reddit from the last place holder: '
            if (place_anchor != 0 ):
                print("Getting new submissions starting from: " + place_anchor)
                submissions = r.get_subreddit(sub_reddit).get_hot(limit=None, 
                                                                      place_holder=place_anchor)
            else:
                print("\n\n************************************************************************")
                print("Getting new submissions - initial request from : " + sub_reddit)
                submissions = r.get_subreddit(sub_reddit).get_hot(limit=None)
                
            ' Iterate the submissions '
            for sub in submissions:
                try:
                    'Total units counter '
                    counter += 1
                          
                    ' Skip non supported sites'
                    if not (str(sub.domain) in SUPPORTED_NEWS_SITES): 
                        '''print (str(counter) + ": NOT SUPPORTED: " + str(sub.score) + ": "+ sub.title + "(" + str(sub.domain) + ")" )'''
                        print (str(counter) + ": NOT SUPPORTED: " + str(sub.score) + ": "+ str(sub.domain))
                        continue
                    
                    ' Print to screen and to CSV the reults'
                    print(str(counter) + ': FOUND' +'('+ str(article_id) +'): ' + str(sub) + "(" + str(sub.domain) + ")")
                    csv_writer.writerow((article_id, sub.id, sub.score, re.sub(r'\,', '', sub.title), sub.url, sub.permalink, sub.domain))
                    
                    'Open File with article id as the name'
                    article_file = open(str(sub_reddit) + "\\" + str(article_id), 'w+', newline="\n")
                    article_file.write("<article>\n")
                    article_file.write("<sub-reddit>" + sub_reddit + "</sub-reddit>\n")
                    article_file.write("<news-paper>" + sub.domain + "</news-paper>\n")
                    article_file.write("\n")
                    stripped_title = re.sub(r'<[^<]+?>', '', str(str(sub.title).encode(encoding='utf_8', errors='ignore')))
                    stripped_title = re.sub(r'(b\'|\\n\')', '', stripped_title)
                    stripped_title = re.sub(r'\\x..', '', stripped_title)
                    article_file.write("<title>" + stripped_title  + "</title>\n")
                    
                    'Get the article content'
                    if (sub.domain == SUPPORTED_NEWS_SITES[0]):
                        Scraper.ny_times.get_HTML_article(url_opener, article_file, sub.url)
                    elif (sub.domain == SUPPORTED_NEWS_SITES[1]):
                        Scraper.usa_today.get_HTML_article(url_opener, article_file, sub.url)
                    elif (sub.domain == SUPPORTED_NEWS_SITES[2]):
                        Scraper.washington_post.get_HTML_article(url_opener, article_file, sub.url)
                        
                    'Close the XML file'
                    article_file.write("</article>\n")
                    
                    ' Set new place holder '
                    place_anchor = sub.id
                    
                    'Found articles counter'
                    article_id +=1
                    
                    article_file.close()
                    'Limit the articles found'
                    if (article_id > ARTICLE_LIMIT) :
                        place_anchor = 0
                        break
                except:
                    try:
                        print("ERROR: Failed to get: " + print(str(sub)))
                    except:
                        print("ERROR: Failed to get number: " + str(counter))

    file.close()
    print("Completed REDDIT mining successfully")