import ny_times
import usa_today
import washington_post

'''
 * The Scraper Module
 * Iterates over the news paper modules and calls the FETCH method.
 * The result of a module call is:
 *  1. Update CSV file with the retrieved articles.
 *  2. A directory with the paper name and article text file with the article saved as file. 
'''
if __name__ == '__main__':
    
    'Create CSV file for articles'
    target_file_address= "articles.csv"
    file = open(target_file_address,'w+', newline="\n")
    
    ''' 
    *
    * RUN THE NEWS PAPER MODULES 
    *
    '''
    
    'NEW YORK TIMES'
    try:
        print ("Scraping NY TIMES:")
        ny_times.fetch(file)
    except:
        print ("Failed to scrape NY TIMES")
        
    
    'USA TODAY'
    try:
        print ("Scraping USA TODAY:")
        usa_today.fetch(file)
    except:
        print ("Failed to scrape USA TODAY")
        
    
    "Add More modules here ... "    
        
    file.close()
    
    print("==================      SCRAPER MODULE - Completed Sucessfully      ==================")
    pass