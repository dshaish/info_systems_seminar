import re
from bs4 import BeautifulSoup

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
    article_body=soup.findAll('article')
    
    'Get all paragraphs + clean redundant chars'
    article_file.write("ARTICLE:" + "\n")
    if (article_body is None):
        return
    
    for article in article_body:
        for paragraph in article.findAll('p'):
            stripped_p = re.sub('<[^<]+?>', '', str(str(paragraph).encode(encoding='utf_8', errors='ignore')))
            stripped_p = re.sub(r'(b\'|\\n\')', '', stripped_p)
            stripped_p = re.sub(r'\\n', '', stripped_p)
            stripped_p = re.sub(r'\\x..', '', stripped_p)
            article_file.write(stripped_p + "\n")
            
    'Get next page - Currently disabled '
    #for link in soup.findAll('a', attrs={"class": "next"}):
    #    if (link.get('title') == 'Next Page'):
    #        get_HTML_article(article_file, url_opener, (page_num+1), article_url)
