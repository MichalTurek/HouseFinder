import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from google_docs_service import *
END_OF_LISTINGS =0
PHRASES_NEEDED = ["studen","wrześ","wrzesn","paździer","pazdzier","wrzesi","gumed","politech"]
SCOPES = ['https://www.googleapis.com/auth/documents']
# Set up the Selenium WebDriver
def search_page_trojmiasto(driver,page):
    print("looking for listings on page:"+str(page))
    url = "https://ogloszenia.trojmiasto.pl/nieruchomosci-mam-do-wynajecia/e1i,81_33_3_5_2_7,ri,3_3,o1,1.html"+"?strona="+str(page)
    print(url)
    
    driver.get(url)

    # Wait for the listings to load
    wait = WebDriverWait(driver, 1)
    try:
        listings = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.list__item__content__title__name.link')))
    except Exception as e:
        print("no listings on  this page")
        return END_OF_LISTINGS
    # Extract the hrefs from the listings
    hrefs = [listing.get_attribute('href') for listing in listings]

    print("found "+str(len(hrefs)) +" home links")
    links_list = []
    for href in hrefs:
        driver.get(href)
        try:
            # Wait for the description div to load
            description_div = WebDriverWait(driver,1).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ogl__description"))
            )
            description_text = description_div.text.lower()

            # Check if any of the PHRASES_NEEDED are present
            if  any(phrase.lower() in description_text.lower() for phrase in PHRASES_NEEDED):
                #print(f"Match found in: {href}")
                links_list.append(href) 

                #print(f"No match in: {href}")

        except Exception as e:
            print(f"Error accessing {href}: {e}")
    return links_list
def search_page_otodom(driver,page):
    print("looking for listings on page:"+str(page))
    url = "https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie%2C3-pokoje/pomorskie/gdansk/gdansk/gdansk?limit=36&by=LATEST&direction=DESC&viewType=listing&mapBounds=54.417380736616224%3B18.68621423920789%3B54.26976661502202%3B18.450988167731968"+"&page="+str(page)
    print(url)
    driver.get(url)

    # Wait for the listings to load
    wait = WebDriverWait(driver, 5)
    try:
        listings = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[data-cy="listing-item-link"]')))
    except Exception as e:
        print("no listings on  this page")
        return END_OF_LISTINGS
    # Extract the hrefs from the listings 
    hrefs=[]
    for listing in listings:
        try: 
            hrefs.append(listing.get_attribute('href')) 
        except Exception as e: 
            continue

    print("found "+str(len(hrefs)) +" home links")

    links_list = []
    for href in hrefs:
        driver.get(href)
        try:
            # Wait for the description div to load
            description_div = WebDriverWait(driver,1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-cy="adPageAdDescription"]'))
            )
            description_text = description_div.text.lower()

            # Check if any of the PHRASES_NEEDED are present

            if any(phrase.lower() in description_text.lower() for phrase in PHRASES_NEEDED):
               # print(f"Match found in: {href}")
                links_list.append(href) 

               # print(f"No match in: {href}")

        except Exception as e:
            print(f"Error accessing {href}: {e}")
    
    return links_list
def search_page_olx(driver,page):
    print("looking for listings on page:"+str(page))
    url = str("https://www.olx.pl/nieruchomosci/mieszkania/wynajem/gdansk/?page="+str(page)+ "&search%5Bfilter_enum_rooms%5D%5B0%5D=three&search%5Border%5D=created_at%3Adesc")
    print(url)
    driver.get(url)

    # Wait for the listings to load
    wait = WebDriverWait(driver, 5)
    try:
        listings = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-cy="ad-card-title"]')))
    except Exception as e:
        print("no listings on  this page")
        return END_OF_LISTINGS,True
    hrefs=[]
    print("found "+str(len(listings)) +" home links")

    if (len(listings) <32):
        Is_last_page = True
    else:
        Is_last_page = False
    for listing in listings:
        a_tag = listing.find_element(By.CSS_SELECTOR, 'a')
        href = a_tag.get_attribute('href')
        if 'olx' in href: 
            hrefs.append(href)
    
   
    links_list = []

    for href in hrefs:
        driver.get(href)
        try:
            # Wait for the description div to load
            description_div = WebDriverWait(driver,1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-cy="ad_description"]'))
            )
            description_text = description_div.text.lower()

            # Check if any of the PHRASES_NEEDED are present
            if any(phrase.lower() in description_text.lower() for phrase in PHRASES_NEEDED):
               # print(f"Match found in: {href}")
                links_list.append(href)
               # print(f"No match in: {href}")

        except Exception as e:
            print(f"Error accessing {href}: {e}")
    return links_list,Is_last_page
if __name__ =="__main__":
    ChromeDriverManager().install()
    driver = webdriver.Chrome()
    links_list =[]


    for i in range(1,2):
        matching_house_links,Is_last_page  = search_page_olx(driver,i)
        if matching_house_links == END_OF_LISTINGS or Is_last_page:
            break
        links_list.append(matching_house_links)
    for i in range(0,1):
        matching_house_links  = search_page_trojmiasto(driver,i)
        if matching_house_links == END_OF_LISTINGS:
            break
        links_list.append(matching_house_links)
    for i in range(1,2):
        matching_house_links  = search_page_otodom(driver,i)
        if matching_house_links == END_OF_LISTINGS:
            break
        links_list.append(matching_house_links)
    final_matching_house_links = []
    for page_matching_house_links in links_list:
        final_matching_house_links.extend(page_matching_house_links)
    print("found " +str(len(final_matching_house_links)) + " potential house links")
    # Close the browser
    driver.quit()
    service = create_google_docs_service()
    document_id = "1pC4VVSUMP2ABTb3lqb2xfHaUEZVctQRDMj1nxVuHuAc" 

    # Create a new Google Docs document
    existing_house_links = get_document_content(service,document_id)

    new_house_links = [final_matching_house_link for final_matching_house_link in final_matching_house_links if final_matching_house_link not in existing_house_links]
    print(new_house_links)
    print()
    new_house_links =list(set(new_house_links))
    print(new_house_links)
    if len(new_house_links)==0:
        print("found no new house links")
        exit()
    print("Found " + str(len(new_house_links))+ " new house links")
    combined_links = ["linki do mieszkań "+str(datetime.now().strftime("%Y-%m-%d %H:%M"))+":"]
    combined_links.extend(new_house_links)
    print(combined_links)
    # Write the extracted hrefs to the document
    write_to_document(service, document_id, combined_links)