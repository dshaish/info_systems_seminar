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
QUERY_TERMS='fq=body:("obama")+AND+body:("democrats")+AND+body:("republicans")+AND+body:("elections")'
TIME_LIMIT='&begin_date=20120601&end_date=20131115'
FIELDS='&fl=headline,lead_paragraph,web_url,pub_date,news_desk,source'
SORT='&sort=newest'  
PAGE='&page=0'
PAGE_TEXT='page='
IGNORE_STRING="Corrections:"
KEY='&api-key=ab3f971cf65466f158af0756aff34fe5:16:67528541'
API_URL='http://api.nytimes.com/svc/search/v2/articlesearch.json?'

'''
    * Get the number of offset/pages
'''
def get_number_of_queries():
    
    ' Create HTML link address for query '
    request_url= API_URL + QUERY_TERMS + TIME_LIMIT + FIELDS + SORT + KEY
    print("Search Query URL for NY Times is  " + request_url)

    'Send URL request and convert response to JSON'
    url_resp=urllib.request.urlopen(request_url)
    response = url_resp.read()
    json_response = json.loads(response.decode('utf-8'))
    
    'Get total number of search results'
    num_items=json_response['response']['meta']['hits']
    print("Total number of search results: " + str(num_items))
    print ("\n")
    
    'Get total number of page requests needed '
    range_size = (int(num_items/10))
    if ((num_items - range_size) > 0):
        range_size += 1        

    return ([range_size, num_items])

'''
    * Prepare the CSV file and Headline 
'''
def prepare_csv_file(file, num_items):
    csv_writer = csv.writer(file,delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow((""))
    csv_writer.writerow((""))
    csv_writer.writerow((""))
    csv_writer.writerow(("", "NY TIMES Section"))
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
        author = str(article_author[0])
        author_stripped = Scraper.string_cleaner(author)
    else :
        author_stripped = "Unknown"
    
    article_file.write("<author>" + author_stripped + '</author>\n\n')
    
    'Get all paragraphs + clean redundant chars'
    article_file.write("<content>" + "\n")
    try:
        for paragraph in soup.findAll('p', attrs={"itemprop": "articleBody"}):
            stripped_p = Scraper.string_cleaner(paragraph)
            article_file.write(stripped_p + "\n")
        
        article_body=soup.findAll('div', {'class':'entry-content'})
        for paragraph in article_body:
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
    print ("***        NY Times Module       ***")
    print ("************************************")
    
    ''' 
     Returns the number of search queries we need to send - 
     each query is limited to 10 search results.'''
    res = get_number_of_queries()
    offsets=res[0]
    num_items=res[1]
    
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
    for i in range(offsets):
        
        'Build New search string'
        cur_page= "&" + PAGE_TEXT + str(i)
        #req_urls= API_URL + QUERY_TERMS + TIME_LIMIT + SORT + FIELDS + cur_page + KEY
        req_url= API_URL + QUERY_TERMS + TIME_LIMIT + FIELDS + SORT + cur_page  + KEY
        print("Getting first page with query: " + req_url)
        
        'Get search results JSON object'
        with urllib.request.urlopen(req_url) as url:
            response = url.read()
        json_response = json.loads(response.decode('utf-8').strip('()'))
        
        'Iterate the results per article and print to file '
        num_result = json_response['response']['docs']
        article_id = (i * 10)
        for article in num_result:
            
            'Extract csv file headers '
            title=article['headline']['main']
            date=article['pub_date']
            article_url=article['web_url']
            news_desk=article['news_desk']
            source=article['source']
            lead_p=article['lead_paragraph']
            
            'Write to CSV file'
            if IGNORE_STRING in title: continue
            print(str(article_id) + ":   " + "TITLE:" + "\t" + title)
            csv_writer.writerow((article_id, date, article_url, re.sub(r'\,', '', title), news_desk, source))
            
            'Open File with article id as the name'
            article_file = open("NY_Times\\"+str(article_id),'w+', newline="\n")
            
            'Write text file headline'
            try:
                article_file.write("TITLE: " + title + "\n")
            except:
                print("Failed to GET Title !")
            
            try:    
                article_file.write("DATE: " + date + "\n")
            except:
                print("Failed to GET Date !")
            try:    
                article_file.write("LINK:: " + article_url + "\n")
            except:
                print("Failed to GET Link !")
            try:    
                str_lead_p = re.sub(r'(b\'|\\n\')', '', str(lead_p.encode(encoding='utf_8')))
                article_file.write("LEAD PARAGRAPH: " + "\n" + str_lead_p + "\n\n")
            except:
                print("Failed to GET Lead Paragraph !")
                
                'Get the full HTML text'
            try:          
                get_HTML_article(url_opener, article_file, article_url)
            except:
                print("Failed to GET article !")
                
            article_file.close()
            article_id += 1
            
    print ("***        NY Times Module: DONE       ***")
    print ("")
    print ("")