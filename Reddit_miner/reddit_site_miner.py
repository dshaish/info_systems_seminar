import csv
import os
import http.cookiejar
import urllib.request
import Scraper
import traceback
import time
from bs4 import BeautifulSoup

REDDIT_URL= "http://www.reddit.com/search?q="
SITE_Q="site:"
SUBREDDIT_Q="subreddit:"
SORT_Q="&sort="
RESTRICT_Q="restrict_sr=off"
TIME_Q="&t=all"
AFTER_Q='&after='

REP_SUB_REDDIT={"republicans", "Republican", "Romney"}
DEM_SUB_REDDIT={"democrats", "Democrat", "obama"}
CENTER_SUB_REDDIT={"ModerateRepublican", "ModerateDemocrate"}
SUB_REDDIT= set(list(DEM_SUB_REDDIT) + list(REP_SUB_REDDIT))
SUPPORTED_NEWS_SITES=["nytimes.com", "usatoday.com","washingtonpost.com"]
VOTE_TRESHHOLD=0

' Limit of number of results pages'
SEARCH_RESULTS_PAGES = 50

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
    csv_writer.writerow(('ID', 'REDDIT_ID', 'SCORE', 'Title', 'URL', 'SOURCE'))
    return csv_writer

if __name__ == '__main__':
    
    'Create Filw for reddit data base '
    target_file_name="reddit.csv"
    file = open(target_file_name,'w+', newline="\n")

    'Prepare URL handlers'
    cj = http.cookiejar.CookieJar()
    url_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    ' Clear global counter '
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
        search_results = 0
        
        for newspaper in SUPPORTED_NEWS_SITES:
            
            print (" ****** Getting Posts from: " + sub_reddit + " From Newspaper: " + newspaper + " ******")
            
            ' Clear newspaper limit '
            search_results_pages_count = 0
             
            'Clear Place holder'
            place_holder = None
            
            'Limit the articles found'        
            while (search_results_pages_count < SEARCH_RESULTS_PAGES):
                
                'First results page'
                search_results_pages_count += 1
                
                "Send HTTP search query"
                retry_url = True
                while (retry_url): 
                    try:
                        if (place_holder == None):
                            query_url= REDDIT_URL + SITE_Q + newspaper + "+" + SUBREDDIT_Q + sub_reddit + SORT_Q + "top" + RESTRICT_Q + TIME_Q
                        else:
                            query_url= REDDIT_URL + SITE_Q + newspaper + "+" + SUBREDDIT_Q + sub_reddit + SORT_Q + "top" + RESTRICT_Q + TIME_Q + AFTER_Q + str(place_holder)
                        
                        print("Search Query URL for REDDIT is  " + query_url)
                        url_resp=urllib.request.urlopen(query_url)
                        html_response = url_resp.read()
                        retry_url = False
                    except:
                        print("Failed to get URL")
                        time.sleep(5)
                        
                'Build HTML parser'     
                soup = BeautifulSoup(html_response)
                
                results_obj=soup.find('div', attrs={"class": "sitetable linklisting"})
                for result in results_obj:
                    try:
                        'Get ID'
                        try:
                            res_id = result['data-fullname']
                        except:
                            continue
                        
                        'Get Entry'
                        entry_obj = result.find('div', attrs={"class": "entry unvoted"})
                        
                        'Get title'
                        title_obj = (entry_obj.find('p', attrs={"class": "title"})).find('a', attrs={"class": "title "})
                        title_parsed = title_obj.contents
                        url= title_obj['href']
                        title = Scraper.string_cleaner(str(title_parsed[0]))
                                          
                        'Get Domain'
                        domain_obj = entry_obj.find('p', attrs={"class": "title"})
                        span_obj = domain_obj.find('span', attrs={"class": "domain"})
                        domain_parsed = span_obj.find('a').contents
                        domain = Scraper.string_cleaner(str(domain_parsed[0]))
                        
                        'Subreddit'
                        tagline = entry_obj.find('p', attrs={"class": "tagline"})
                        hover = tagline.find('a', attrs={"class": "subreddit hover"})
                        subredd_parsed = hover.contents
                        subredd = Scraper.string_cleaner(str(subredd_parsed[0]))
                        subredd = subredd[:-1]    
                        
                        'Score'
                        midcol_entry = result.find('div', attrs={"class": "midcol unvoted"})
                        score_entry = midcol_entry.find('div', attrs={"class": "score unvoted"})
                        score = int(score_entry.contents[0])
        
                        'Search reults counter'
                        search_results += 1
                            
                        'Accept only posts with comments'                  
                        if (score < VOTE_TRESHHOLD):
                            continue
                        
                        'Open File with article id as the name'
                        article_file = open(str(sub_reddit) + "\\" + str(article_id), 'w+', newline="\n")
                        article_file.write("<article>\n")
                        article_file.write("<sub-reddit>" + sub_reddit + "</sub-reddit>\n")
                        article_file.write("<news-paper>" + domain[:-1] + "</news-paper>\n")
                        article_file.write("\n")         
                        article_file.write("<title>" + title[:-1]  + "</title>\n")
                            
                        'Get the article content'
                        if (SUPPORTED_NEWS_SITES[0] in domain):
                            success = Scraper.ny_times.get_HTML_article(url_opener, article_file, url)
                        elif (SUPPORTED_NEWS_SITES[1] in domain):
                            success = Scraper.usa_today.get_HTML_article(url_opener, article_file, url)
                        elif (SUPPORTED_NEWS_SITES[2] in domain):
                            success = Scraper.washington_post.get_HTML_article(url_opener, article_file, url)
                        else:
                            print ("### Un-supported newspaper: " + domain) 
                            success = False 
                            
                        'Close the XML file'
                        article_file.write("</article>\n")
                        
                        'Found articles counter'
                        if (success == True) :
                                     
                            'Total units counter '
                            counter += 1
                            
                            ' Print to screen and to CSV the reults'
                            print(str(counter) + ': FOUND' +'('+ str(article_id) +'): ' + title + "(" + domain + ")")
                            csv_writer.writerow((article_id, res_id, score, title, url, domain))
                        
                            'increment counters'
                            article_id += 1
                                
                            ' Close single article file'
                            article_file.close()
                            
                        place_holder = res_id
                    except:
                            print(traceback.format_exc())
                            print("ERROR: Failed to get: " + title)
                        
        print ("@@@ Total results for " + sub_reddit + " : " + str(search_results))              
        search_results = 0
        
    file.close()
    print("Completed REDDIT mining successfully")