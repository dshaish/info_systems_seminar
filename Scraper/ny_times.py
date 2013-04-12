import os
import json
import urllib
import csv
import http.cookiejar
from bs4 import BeautifulSoup

'''
 * Default parameters for the module search queries
'''
API_URL='http://api.nytimes.com/svc/search/v1/article?format=json'
QUERY='query=democrats' #+republicans'   
FACETS='desk_facet=[POLITICS]%2Cnytd_section_facet=[POLITICS]'                         
API_DATA='begin_date=20130101&end_date=20130408'   
FIELDS='fields=body%2Curl%2Ctitle%2Cdate%2Cdes_facet%2Cdesk_facet%2Cnytd_section_facet%2Cbyline'
OFFSET='offset=0'
KEY='api-key=ab3f971cf65466f158af0756aff34fe5:16:67528541'

'''
    * Get the number of offset/pages
'''
def get_number_of_offsets():
    
    LINK=[API_URL, QUERY, API_DATA, FACETS, FIELDS, OFFSET, KEY]
    request_url='&'.join(LINK)
    print("Search Query URL for NY Times is  " + request_url)

    'Send URL request and convert response to JSON'
    with urllib.request.urlopen(request_url) as url:
        response = url.read()
    json_response = json.loads(response.decode('utf-8'))
    
    'Total number of search results'
    num_items=json_response['total']
    print("Total number of search results: " + str(num_items))
    
    range_size = (int(num_items/10))
    if ((num_items - range_size) > 0):
        range_size += 1        
    
    'Override the number of articles fetching ' 
    #seq=range(range_size)
    return ([range(2), num_items])

'''
    * Prepare the CSV file and Headline 
'''
def prepare_csv_file(file, num_items):
    csv_writer = csv.writer(file,delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(("0", "NY TIMES Section"))
    csv_writer.writerow(("0", "Total number of listings", num_items))
    csv_writer.writerow(('ID', 'Date', 'URL','Title', 'Body', 'des_facet', 'desk_facet'))
    return csv_writer

def get_HTML_article(article_file, url_opener, page_num, article_url):
    'Get URL HTML'
    html_url = article_url+"?pagewanted="+str(page_num)
    print ("Getting HTML article from URL: " + html_url)
    html_resp = url_opener.open(html_url)
    
    'Build HTML parser'     
    soup = BeautifulSoup(html_resp)
    
    'Get all paragraphs'
    for paragraph in soup.findAll('p', attrs={"itemprop": "articleBody"}):
        article_file.write(str(str(paragraph).encode(encoding='utf_8', errors='ignore')))
        article_file.write("\n")
        
    'Get next link'
    for link in soup.findAll('a', attrs={"class": "next"}):
        if (link.get('title') == 'Next Page'):
            get_HTML_article(article_file, url_opener, (page_num+1), article_url)
    
    
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
    res = get_number_of_offsets()
    seq = res[0]
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
    for i in seq:
        'Build New search string'
        cur_offset=''.join(['offset=', str(i)])
        cur_link=[API_URL, QUERY, API_DATA, FACETS, FIELDS, cur_offset, KEY]
        req_urls='&'.join(cur_link)
        
        'Get search results JSON object'
        with urllib.request.urlopen(req_urls) as url:
            response = url.read()
        json_response = json.loads(response.decode('utf-8').strip('()'))
        
        'Iterate the results per article and print to file '
        result = json_response['results']
        article_id = 0
        for ob in result:
            date=ob['date']
            article_url=ob['url']
            title=ob['title']  
            body=ob['body']
            des_facet=ob['des_facet']
            desk_facet=ob['desk_facet']
            
            'Write to CSV file'
            csv_writer.writerow((article_id, date, article_url, title, body, des_facet, desk_facet))
            
            'Get the Article text from the URL address in HTML'
            article_file = open("NY_Times\\"+str(article_id),'w+', newline='')
            get_HTML_article(article_file, url_opener, 1, article_url)
            article_file.close()
            article_id += 1
    print ("***        NY Times Module: DONE       ***")