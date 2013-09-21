import os
import json
import urllib.request
import csv
import re
import http.cookiejar
from bs4 import BeautifulSoup

'''
 * Default parameters for the module search queries
'''   
#QUERY_SEARCH='q=Obama+Syria+-Corrections'
QUERY_TERMS='&fq=body:("Obama")+AND+body:("Syria")'
TIME_LIMIT='begin_date=20130901&end_date=20130921'
ARCHIVE_FIELDS='fl=headline,lead_paragraph,web_url,pub_date,news_desk,source'
FIELDS='fl=headline,lead_paragraph,web_url,pub_date,news_desk,source'
SORT='sort=newest'  
PAGE='page=0'
PAGE_TEXT='page='
KEY='api-key=ab3f971cf65466f158af0756aff34fe5:16:67528541'
API_URL='http://api.nytimes.com/svc/search/v2/articlesearch.json?'

'''
    * Get the number of offset/pages
'''
def get_number_of_queries():
    
    ' Create HTML link address for query '
    LINK=[API_URL, QUERY_TERMS, TIME_LIMIT, FIELDS, SORT, KEY]
    request_url='&'.join(LINK)
    print("Search Query URL for NY Times is  " + request_url)

    'Send URL request and convert response to JSON'
    url_resp=urllib.request.urlopen(request_url)
    response = url_resp.read()
    json_response = json.loads(response.decode('utf-8'))
    
    ' Get total number of search results'
    num_items=json_response['response']['meta']['hits']
    print("Total number of search results: " + str(num_items))
    print ("\n")
    
    ' Get total number of page requests needed '
    range_size = (int(num_items/10))
    if ((num_items - range_size) > 0):
        range_size += 1        
    
    'TEMP: Override the number of articles fetching '
    # [DS]:   return ([range_size, num_items])
    return ([range(2), num_items])

'''
    * Prepare the CSV file and Headline 
'''
def prepare_csv_file(file, num_items):
    csv_writer = csv.writer(file,delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(("", "NY TIMES Section"))
    csv_writer.writerow(("", "Total number of listings", num_items))
    csv_writer.writerow(('ID', 'Date', 'URL','Title', 'News Desk', 'Source'))
    return csv_writer

def get_HTML_article(url_opener, article_file, article_url):
    
    'Get URL HTML'
    print ("Getting HTML article from URL:   " + article_url)
    html_response=url_opener.open(article_url)
    
    'Build HTML parser'     
    soup = BeautifulSoup(html_response)
    
    'Get all paragraphs + clean redundant chars'
    article_file.write("PARAGRAPH BODY:" + "\n")
    for paragraph in soup.findAll('p', attrs={"itemprop": "articleBody"}):
        stripped_p = re.sub('<[^<]+?>', '', str(str(paragraph).encode(encoding='utf_8', errors='ignore')))
        stripped_p = re.sub(r'(b\'|\\n\')', '', stripped_p)
        stripped_p = re.sub(r'\\n', '', stripped_p)
        stripped_p = re.sub(r'\\x..', '', stripped_p)
        article_file.write(stripped_p + "\n")
        
    'Get next page - Currently disabled '
    #for link in soup.findAll('a', attrs={"class": "next"}):
    #    if (link.get('title') == 'Next Page'):
    #        get_HTML_article(article_file, url_opener, (page_num+1), article_url)
    
'''
 * Fetch the search results according to the search parameters.
'''
def fetch(file):
    
    print ("************************************")
    print ("***        NY Times Module       ***")
    print ("************************************")
    
    ''' 
     Returns the number of search queries we need to send - 
     each query is limited to 10 search results.'''
    res = get_number_of_queries()
    offsets = res[0]
    num_items = res[1]
    
    ' Get the CSV file ready and write headline'
    csv_writer = prepare_csv_file(file, num_items)
    
    ' Prepare the scraper objects'
    if not os.path.exists("NY_Times"):
        os.makedirs("NY_Times")
    cj = http.cookiejar.CookieJar()
    url_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    
    '''
     * Crawl the data and dump into a CSV file
    '''
    for i in offsets:
        'Build New search string'
        cur_page=''.join([PAGE_TEXT, str(i)])
        cur_link=[API_URL, QUERY_TERMS, TIME_LIMIT, SORT, ARCHIVE_FIELDS, cur_page, KEY]
        req_urls='&'.join(cur_link)

        'Get search results JSON object'
        with urllib.request.urlopen(req_urls) as url:
            response = url.read()
        json_response = json.loads(response.decode('utf-8').strip('()'))
        
        'Iterate the results per article and print to file '
        result = json_response['response']['docs']
        article_id = (i * 10)
        for article in result:
            date=article['pub_date']
            article_url=article['web_url']
            title=article['headline']['main']  
            lead_p=article['lead_paragraph']
            news_desk=article['news_desk']
            print(str(article_id) + ":   " + "TITLE:" + "\t" + title)
            'Write to CSV file'
            csv_writer.writerow((article_id, date, article_url, re.sub(r'\,', '', title), news_desk))
            
            'Get the Article text from the URL address in HTML'
            article_file = open("NY_Times\\"+str(article_id),'w+', newline="\n")
            
            'Write text file headline'
            article_file.write("TITLE: " + title + "\n")
            article_file.write("DATE: " + date + "\n")
            str_lead_p = re.sub(r'(b\'|\\n\')', '', str(lead_p.encode(encoding='utf_8')))
            article_file.write("LEAD PARAGRAPH: " + "\n" + str_lead_p + "\n\n")
            
            'Get the full HTML text'
            get_HTML_article(url_opener, article_file, article_url)
                
            article_file.close()
            article_id += 1
            
    print ("***        NY Times Module: DONE       ***")