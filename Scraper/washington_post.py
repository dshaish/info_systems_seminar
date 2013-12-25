import Scraper
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
    
    'Get the Author'
    article_author_obj=soup.find('a', attrs={"rel": "author"})
    if (article_author_obj != None):
        article_author= article_author_obj.contents
        author = str(article_author[0])
        author_stripped = Scraper.string_cleaner(author)
    else :
        author_stripped = "Unknown"
        
    article_file.write("<author>" + author_stripped  + '</author>\n\n')
    
    'Get the Author'
    article_body=soup.findAll('article')
    
    'Get all paragraphs + clean redundant chars'
    article_file.write("<content>" + "\n")
    
    try:
        for article in article_body:
            for paragraph in article.findAll('p'):
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
