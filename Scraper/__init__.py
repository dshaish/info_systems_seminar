import ny_times

if __name__ == '__main__':
    target_file_address= "articles.csv"
    file = open(target_file_address,'w+', newline='')
    
    try:
        ny_times.fetch(file)
    except:
        print ("Failed to scrape NY Times")
        
    file.close()
    pass