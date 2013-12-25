import os
import json
import urllib.request
import csv
import re
import http.cookiejar
from bs4 import BeautifulSoup
import Scraper

'''
 * Default parameters for the module search queries
'''   
QUERY_TERMS='&keyword=obama+AND+democrats+AND+republicans+AND+elections'
TIME_LIMIT='&todate=2012-11-15&days=250'
COUNT_TIMES=50
COUNT_LIMIT='&count=50'
SORT='&most=commented'  
NEWS_SECTION='&section=news' # or Washington
KEY='&api_key=3s27rj4acsr38zqtrvn2zusc'
API_URL='http://api.usatoday.com/open/articles?encoding=json'


'''
 * Prepare the CSV file and Headline 
'''
def prepare_csv_file(file, num_items):
    csv_writer = csv.writer(file,delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow((""))
    csv_writer.writerow((""))
    csv_writer.writerow((""))
    csv_writer.writerow(("", "USA TODAY Section"))
    csv_writer.writerow(("", "Total number of listings", num_items))
    csv_writer.writerow(('ID', 'Date', 'URL','Title', 'News Desk', 'Source'))
    return csv_writer

'''
 * GET's the article from the search result link and extracts the article body.
 * The article body is written to the article_file. 
'''
def get_HTML_article(url_opener, article_file, article_url):    
    
    'Get URL HTML'
    print ("Getting HTML article from URL:   " + article_url)
    html_response=url_opener.open(article_url)
    
    'Build HTML parser'     
    soup = BeautifulSoup(html_response)
    
    'Get the Author'
    article_author_obj=soup.find('span', attrs={"itemprop": "name"})
    if (article_author_obj != None):
        article_author= article_author_obj.contents
        author_to_parse = article_author[0].split(",", 1)
        author = re.sub(r'\\n', '', str(author_to_parse[0])).strip()
        author_stripped = Scraper.string_cleaner(author)
    else :
        author_stripped = "Unknown"
  
    article_file.write("<author>" + author_stripped +'</author>\n\n')
         
    'Get The Article body'
    article_body=soup.find(attrs={"itemprop": "articleBody"})
    
    'Get all paragraphs + clean redundant chars'
    article_file.write("<content>" + "\n")
    try:
        for paragraph in article_body.findAll('p'):
            stripped_p = Scraper.string_cleaner(paragraph)
            article_file.write(stripped_p + "\n")
    except:
        return False
                  
    article_file.write("</content>" + "\n")
    
    return True

    'Get next page - Currently disabled '
    #for link in soup.findAll('a', attrs={"class": "next"}):
    #    if (link.get('title') == 'Next Page'):
    #        get_HTML_article(article_file, url_opener, (page_num+1), article_url)
    
'''
 * Fetch the search results according to the search parameters.
'''
def fetch(file):
    
    print ("************************************")
    print ("***       USA TODAY Module       ***")
    print ("************************************")
    
    ' Get the CSV file ready and write headline'
    csv_writer = prepare_csv_file(file, COUNT_TIMES)
    
    ' Prepare the scraper objects'
    if not os.path.exists("USA_Today"):
        os.makedirs("USA_Today")
    cj = http.cookiejar.CookieJar()
    url_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    
    '''
     * Crawl the data and dump into a CSV file
    '''
    'Build New search string'
    search_url= API_URL + QUERY_TERMS + TIME_LIMIT + COUNT_LIMIT + SORT + KEY
    print("Search Query URL for USA Today is  " + search_url)
    
    'Get search results JSON object'
    with urllib.request.urlopen(search_url) as url:
            response = url.read()
    json_response = json.loads(response.decode('utf-8').strip('()'))
        
    'Iterate the results per article and print to file '
    result = json_response['stories']
    article_id = 0
    for article in result:
        try:
            'Extract csv file headers '
            title= re.sub(r'\,', '', article['description'])
            date= re.sub(r'\,', '', article['pubDate'])
            article_url=article['link']
            news_desk='news'
                
            'Write to CSV file'
            print(str(article_id) + ":   " + "TITLE:" + "\t" + title)
            csv_writer.writerow((article_id, date, article_url, title, news_desk, " "))
            
            'Open File with article id as the name'
            article_file = open("USA_Today\\"+str(article_id),'w+', newline="\n")
                
            'Write text file headline'
            article_file.write("TITLE: " + title + "\n")
            article_file.write("DATE: " + date + "\n")
            article_file.write("LINK: " + article_url + "\n")    
            
            'Get the full HTML text'
            get_HTML_article(url_opener, article_file, article_url)
        except:
            print("Failed to GET article !")
            
        article_file.close()
        article_id += 1
            
    print ("***        US Today Module: DONE       ***")
