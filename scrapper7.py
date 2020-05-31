from random import random
import wikipedia
import pandas as pd
import sqlite3
from bs4 import BeautifulSoup
import requests
import time
import urllib

from cashier import cache
from geopy.geocoders import Nominatim





@cache()
def geolocatorgeocode( location ):
    print( "--> Geolocation of : " + location )
    geolocator = Nominatim(user_agent="geoapi")
    return geolocator.geocode( location, timeout=75)

@cache()
def geolocatorreverse( x , y ):
    print("--> Geolocation of : " + str(x) + " , " + str(y) )
    geolocator = Nominatim(user_agent="geoapi", timeout=75)
    return geolocator.reverse('{},{}'.format( x, y ), language='en')









import requests_cache
requests_cache.install_cache('cachingrequests', backend='sqlite', expire_after=3600*24*30)

def requestsget( urlToGet ):
    PrefixUrlProxy = "http://api.scraperapi.com?api_key=dad34581503fe55a7106dd0a80cc1b7c&url="
    for AttempRequest in range( 100 ):
        HTTPresponse = None
        HTTPresponsecounthref=0
        HTTPresponsestatus_code=0
        try:
            HTTPresponse = requests.get( PrefixUrlProxy + urlToGet )
            HTTPresponsestatus_code = HTTPresponse.status_code
            HTTPresponsecounthref = HTTPresponse.text.lower().count('href=')
            if HTTPresponsestatus_code == 404:
                print(" requestsget : ARGGGGG a 404 !!! : " , urlToGet )
                return None
            if HTTPresponsestatus_code==200 and HTTPresponsecounthref > 25:
                if HTTPresponse.text.lower().find('</html>') <= 0:
                    print(" Warning the web page do not have </html> !!! HTTPresponsecounthref=" , HTTPresponsecounthref )
                return HTTPresponse

        except Exception as e:
            print("Error http : " , e )

        print( "Error http : Failed requests.get -- # " , AttempRequest , " , HTTPresponsecounthref=", HTTPresponsecounthref, "   HTTPresponsestatus_code=", HTTPresponsestatus_code, "   urlToGet=", urlToGet )
        time.sleep(5)

    return None





def requestsgetForAPI( urlToGet  ):
    PrefixUrlProxy = "http://api.scraperapi.com?api_key=dad34581503fe55a7106dd0a80cc1b7c&url="
    for AttempRequest in range( 100 ):
        HTTPresponse = None
        HTTPresponsestatus_code=0
        try:
            HTTPresponse = requests.get( PrefixUrlProxy + urlToGet )
            HTTPresponsestatus_code = HTTPresponse.status_code
            if HTTPresponsestatus_code == 404:
                print(" requestsget : ARGGGGG a 404 !!! : " , urlToGet )
                return None
            if HTTPresponsestatus_code==200:
                return HTTPresponse

        except Exception as e:
            print("Error http : " , e )

        print( "Error http : Failed requests.get -- # " , AttempRequest , " ,   HTTPresponsestatus_code=", HTTPresponsestatus_code, "   urlToGet=", urlToGet )
        time.sleep(5)

    return None




@cache()
def requestsgetImageURL( Query , MinimumWidth=0 , MinimumHeight=0 , TargetRatio=1.0 ):
    r = requestsgetForAPI("https://api.qwant.com/api/search/images?count=10&t=images&locale=en_US&uiv=4&q=" + Query )
    BestFound = None 
    BestScore = -1.0
    #try:
    AllItems = r.json().get('data').get('result').get('items')
    for i in AllItems:
            Url = i.get('media')
            W = int( i.get('width') )
            H = int( i.get('height') )
            if Url[-4:].lower()=='.jpg':
                Score = ( 1 if ( W > MinimumWidth ) else 0 )  + ( 1 if ( H > MinimumHeight ) else 0 ) - abs(  TargetRatio - (W/H) )
                if Score > BestScore:
                    BestFound = Url
                    BestScore = Score
    #except: 
        #pass
    if BestFound is None:
        print(" ARGGGGG unable to find any images for : " + Query )
    return BestFound





















# =============================================================================
#          Taking Champ 32 and diffrentiating it into museum, city,country
# 
#                   Run This code section First !! from line no 18-24
# =============================================================================
#dataframe = pd.read_excel('LIST PAINTINGS SAMPLE 500.xls')
dataframe = pd.read_csv('PAINTINGS-12.csv')
#dataframe = dataframe[0:250]      #Just to take some dataframe

city = pd.DataFrame(dataframe['Champ32'])
city = pd.DataFrame(city.Champ32.str.split('(',expand=True))
cit=city[1].str.split(',',expand =True)
city.insert(1,"City",cit[0],True)
city.insert(2,'Country',cit[1])
city = city.drop([1],axis =1)






# # =============================================================================
# try:
#     citloaded = pd.read_csv('cit.csv')
#     citloaded = citloaded.where(pd.notnull(citloaded), None)
# except:
#     pass
# else:
#     cit = citloaded
# =============================================================================








# =============================================================================
#                  Cleaning The Parsed Data i.e removing the ')' and white paces
# 
#                   2nd step is to run this code section from line no 33-46
# =============================================================================

for i in range (0,len(city['City'])):
    if city['Country'][i]!= None:
        if city.Country[i][0]== ' ':
            city['Country'][i] = city['Country'][i][1:-1]
        else:
            city['Country'][i] = city['Country'][i][:-1]
    else:
        if city['City'][i]!= None:
            if ')' in city['City'][i]:
                city['Country'][i] = city['City'][i][:-1]
                city['City'][i] = city['City'][i][:-1]
            else:
                city['Country'][i] = city['City'][i]
cit = pd.DataFrame()


# =============================================================================
#          Adding correct city,country,name,wiki url of the Museum
#
#          3rd step is to run this code section  from line no 55-153
# =============================================================================

name = []
def adding_city_state_country(museum,city):
    ci=[]
    co=[]
    st=[]
    lat_long=[]
    mus =[]
    mus_wiki_url = []
    test =[]
    
    for i,j in zip(museum,city):
        #*****Scrapping Wikipedia Url from google********
      
        print( " ---> ", i , " ,  " , j)
        urlsAlreadyDone=[]
        rectify = None
        text = '{}, {} wikipedia.org '.format(i,j)
        text = urllib.parse.quote_plus(text)
        google_url = "https://www.google.com/search?hl=en&num=10&cr=us&q={}".format(text)
        response = requestsget( google_url )
        soup = BeautifulSoup(response.text,'html.parser')
        try :
            error  =  soup.find('span',{'class':'gL9Hy d2IKib'}).text
            rectify = soup.find('a',{'class':'gL9Hy'}).text
            rectify = urllib.parse.quote_plus(rectify)
            google_url = "https://www.google.com/search?hl=en&num=10&cr=us&q={}".format(rectify)
            print("==>  REctified " + rectify)
            response = requestsget( google_url )
            soup = BeautifulSoup(response.text,'html.parser')
            url_from_google = soup.find_all('div',{'class':'r'})
            for k in url_from_google:
                    if k.a['href'][11:20]=='wikipedia' and  k.a['href'][30:34]!='File':
                        url = k.a['href']
                        break
        except:
            try:
                url_from_google = soup.find_all('div',{'class':'r'})
                for k in url_from_google:
                    if k.a['href'][11:20]=='wikipedia' and  k.a['href'][30:34]!='File':
                        url = k.a['href']
                        break

            except:
                try:
                     
                    url_from_google = soup.find_all('div',{'class':'BNeawe UPmit AP7Wnd'})
                    for k in url_from_google:
                        k = (k.text.replace(' › ','/'))
                        if k[11:20]=='wikipedia' and k[30:34]!='File':
                            url = k
                            break
                except:
                        url = None
        if url[11:20]=='wikipedia' and url not in urlsAlreadyDone:
            print("==> Wikilink : " + url )
            urlsAlreadyDone.append( url )
            r = requestsget( url )
            soup = BeautifulSoup(r.text,'html.parser')
            covers = soup.find("span", {'class': 'geo'})
            i = soup.find('h1',{'id':'firstHeading'}).text
            
            check = soup.find('table',{'class':'infobox biography vcard'})
            check2 = soup.find('div',{'id':'catlinks'})
             
            count_words = check2.text.lower().count('museum')
            
            #print('Name:',i)
            if i!=None:
                name.append(i)
            else:
                name.append(None)
            try:
                covers = covers.text.split('; ')
                if len(covers)<=1:
                    covers =None
            except:
                try:
                    location = geolocatorgeocode( '{}, {}'.format(i,j) )
                    covers=[location.latitude,location.longitude]
                except:
                    pass

            try:
                location = geolocatorreverse( covers[0], covers[1] )
            except:
                try:
                    location = geolocatorgeocode( i )
                    covers=[location.latitude,location.longitude]
                    location = geolocatorreverse( covers[0],covers[1] )
                except:
                    try:
                        covers = [soup.find("span", {'class': 'latitude'}).text,soup.find("span", {'class': 'longitude'}).text]
                        location = geolocatorreverse( covers[0],covers[1] )
                    except:
                        pass
            try:
                if check != None:
                    raise NameError("It's not a museum")
                
                if count_words < 2:
                    raise NameError("It's not a museum")
                    
                if '{},{}'.format(covers[0],covers[1]) not in lat_long :
                    try:
                        #print(location.raw['address']['state'])
                        st.append((location.raw['address']['state']))
                    except:
                        st.append(None)
                    try:
                        #print(location.raw['address']['city'])
                        if len(i.split(','))== 2:
                                ci.append(i.split(',')[1])
                        else:
                           ci.append(location.raw['address']['village'])
                           
                          
                            
                    except:
                        try:
                            try:
                                ci.append((location.raw['address']['county']).replace('County',''))
                            except:
                                try:
                                    ci.append((location.raw['address']['town']))
                                   
                                except:
                                     ci.append(location.raw['address']['city'])
                        except:
                            
                            print( "                 ---  NO : city ")
                            ci.append(None)
                    try:
                        #print(location.raw['address']['country'])
                        co.append((location.raw['address']['country']))
                        mus_wiki_url.append(url)
                        mus.append(i)
                        test.append(i)
                    except:
                        print( "                 ---  NO : country ")
                        mus_wiki_url.append(None)
                        mus.append(None)
                        test.append(i)
                        co.append(None)

                    
                    lat_long.append('{},{}'.format(covers[0],covers[1]))
                else:
                    pass
                    #print('Already')

            except:
                    print("                 ---  NO : ADDRESS AT ALL ")
                    st.append(None)
                    ci.append(None)
                    co.append(None)
                    mus_wiki_url.append(url)
                    test.append(i)
                    mus.append(None)
                    lat_long.append(None)
                    
    cit['city_new'] = ci
    cit['country_new'] = co
    cit['state'] = st
    print(len(test))
    #cit['lat_long'] = lat_long
    cit['test'] = test
    cit['name_en']= mus
    cit['url_en'] = mus_wiki_url

adding_city_state_country(city[0],city.City)
city['name'] = name


var = []
for i in range(0,len(cit.city_new)):
    if cit.city_new[i] == None and cit.country_new[i]==None and cit.state[i]==None and cit.name_en[i]==None:
        var.append(cit.test[i])
        cit = cit.drop([i])

for i in range(0,len(city.name)):
    if city.name[i] in var:
        city = city.drop([i])
        dataframe = dataframe.drop([i])

cit = cit.drop(['test'], axis =1)

cit = cit.reset_index(drop=True)
city = city.reset_index(drop = True)
dataframe = dataframe.reset_index(drop = True)
# =============================================================================
#       Adding multilanguage url from wikipedia
#
#        this is 4th step, run from line no 161-190
# =============================================================================

def add_multi_lang_url_name(url):
    for j in ['en','fr','de','it','es','ru','cn','pt','ja']:
        link=[]
        name =[]
        for i in url:
            try:
                print("==>add_multi_lang_url_name : wikipedia multilanguage : "+j+" : " + i )
                r  = requestsget( i )
                soup = BeautifulSoup(r.text,'html.parser')
                covers = soup.find('li',{'class':'interlanguage-link interwiki-'+str(j)})
                if covers == None:
                    covers = soup.find('li',{'class':'interlanguage-link interwiki-{} badge-Q17437796 badge-featuredarticle'.format(j)})
                if covers == None:
                    covers = soup.find('li',{'class':'interlanguage-link interwiki-{} badge-Q17437798 badge-goodarticle'.format(j)})
                
                l = covers.a['href']
                rq = requestsget( covers.a['href'])
                soup = BeautifulSoup(rq.text,'html.parser')
                n = soup.find('h1',{'class':'firstHeading'}).text
                name.append( n )
                link.append( l )
            except:
                link.append(None)
                name.append(None)

        cit['name_'+str(j)] = name
        cit['url_wiki'+str(j)] = link
		

add_multi_lang_url_name(cit.url_en)













# =============================================================================
#               Here We are Correcting some abnormalities
#                This is step 5, run from line 196-213
# =============================================================================


#*********Adding En Url*****************
for i in range(0,len(cit.url_en)):
    if cit.url_en[i] != None:
        n = cit.url_en[i][8:10]
        if n in ['en','fr','de','it','es','ru','cn','pt','ja']:
            cit['url_wiki'+str(n)][i] = cit.url_en[i]

def correct(url,lang):
    correction=[]
    for i in url:
        if i != None:
            print("==>City English name : " + i)
            rq = requestsget( i )
            soup = BeautifulSoup(rq.text,'html.parser')
            correction.append(soup.find('h1',{'class':'firstHeading'}).text)
        else:
            correction.append(None)
    cit['name_'+str(lang)] = correction


for i in  ['en','fr','de','it','es','ru','cn','pt','ja']:
    correct(cit['url_wiki'+str(i)],i)



# =============================================================================
#             Here we are adding description about museum directly from wikipedia
#               This is step 6,run from line 220-240
# =============================================================================


def add_description_in_multilanguage(name,lang):
    description= []
    print('==>add_description_in_multilanguage for :',lang)
    for i in name:
        #print('Name',i)
        try:
            wikipedia.set_lang(lang)
            d = wikipedia.summary(i)
            description.append(d)
        except:
            try:
                wikipedia.set_lang(lang)
                d = wikipedia.summary(wikipedia.suggest(i))
                description.append(d)
            except:
                description.append(None)
    cit['description_'+str(lang)] = description
    

for i in ['en','fr','de','it','es','ru','cn','pt','ja']:
        add_description_in_multilanguage(cit['name_'+i], i)














# =============================================================================
#            Here we are adding the url of pictures directly taken from wikipedia
#               This is step 7, run from line 246 - 271
# =============================================================================
print(" -------- Doing Museums images  -------- ")

def add_image_url(url_en,name):
    print("==>add_image_url : Search : " + name )
    img_url=[]
    for j,l in zip(url_en,name):
        response = requestsget(  j)
        soup = BeautifulSoup(response.text,'html.parser')
        url = soup.find_all('img')
        count = 0
        for i in url:
            count = count+1
            if i['src'][-3:].lower() == 'jpg' and i['src']!=None:
                img_url.append((i['src']))
                #print("       image=",l)
                break
            elif len(url)-count==0:
                img_url.append(None)

    cit['img_url'] = img_url


#add_image_url(cit.url_en,cit.name_en)

for i in cit.index:
    try:
        Q = cit.loc[ i , 'name_en'] + " , " + cit.loc[ i , 'city_new']+ " , " + cit.loc[ i , 'country_new']
        cit.loc[ i , 'PhotoURL'] = 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Icon-round-Question_mark.svg/200px-Icon-round-Question_mark.svg.png'
        cit.loc[ i , 'museum_image'  ] = requestsgetImageURL( Q , MinimumWidth=1200 , MinimumHeight=800 , TargetRatio=1.25 )
        cit.loc[ i , 'museum_thumb_image'  ] = requestsgetImageURL( Q , MinimumWidth=400 , MinimumHeight=200 , TargetRatio=1.5 )
    except:
        cit.loc[ i , 'PhotoURL'] = ''
        cit.loc[ i , 'museum_image'  ] = ''
        cit.loc[ i , 'museum_thumb_image'  ] = ''

print(" -------- Museums images done -------- ")






















# =============================================================================
#           Adding Official url  Of museum
#           This is step 8, run from line 289-325
# =============================================================================


def adding_official_url_of_museum(url,city):
    off_url=[]
    for i,j in zip(url,city): #**************Getting Info from Wikipedia**************
        print("==>adding_official_url_of_museum : 1 : Search official_url_of_museum : " + i )
        rq = requestsget( i)
        soup = BeautifulSoup(rq.text,'html.parser')
        name = soup.find('h1',{'class':'firstHeading'}).text
        
        #**********************Scrapping website from google************************
        
        if j==None  :
            text = '{} website'.format(name)
        else:
            text = '{} {} website'.format(name,j)
            
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
        text = urllib.parse.quote_plus(text)
        google_url = "https://www.google.com/search?hl=en&num=10&cr=us&q={}".format(text)
        response = requestsget( google_url )
        soup = BeautifulSoup(response.text,'html.parser')
        try:
            try:
               website = soup.find('div',{'class':'QqG1Sd'}).next_element['href']
            except:
                try:
                    website = soup.find('div',{'class':'r'}).next_element['href']
                except:
                    website =None
            print("==>adding_official_url_of_museum : 2 : Search official_url_of_museum : " + website )
            
        except:
            website = None

        off_url.append(website)

    cit['official_url'] = off_url


adding_official_url_of_museum(cit.url_en,cit.city_new)























# =============================================================================
#              Here we are filling other columns of museum
#                 This is step 9, run from line no 330- 363
# =============================================================================

cit['museum_official_visitor_count'] = None
cit['rank'] = None



for i in range (0,len(cit.city_new)):
    if cit.city_new[i]== float('nan') or cit.city_new[i]==None :
        if cit.state[i]==float('nan') or cit.state[i]==None:
            if cit.country_new[i] ==float('nan') or cit.country_new[i] == None:
                pass
            else:
                cit.state[i] = cit.country_new[i]
                cit.city_new[i] = cit.country_new[i]
        else:
            cit.city_new[i] = cit.state[i]
    else:
        pass
    

def add_name(url):
    var= []
    for i in url:
        print("==>add_name : Search name inside H1  : " + i )
        rq = requestsget( i)
        soup = BeautifulSoup(rq.text,'html.parser')
        name = soup.find('h1',{'class':'firstHeading'}).text
        var.append(name)
    cit['name'] = var

add_name(cit.url_en)

















# =============================================================================
#                 Here we are generating  the unique country,city and unique Id for them
#                   This is step 10,
# =============================================================================

#*************************Generating the unique id's for city and county***********

unique_city = []
unique_country= []



for i,j in zip (cit.city_new,cit.country_new):
    if i not in unique_city:
        unique_city.append(i)
        
    if j not in unique_country:
        unique_country.append(j)

#***********************Remove all the None from city and country ***************************
#unique_city.remove(None)
#unique_country.remove(None)

try:
    if unique_city.count(None) >0:
        for i in range(0, unique_city.count(None) +1):
            unique_city.remove(None)
    if unique_country.count(None) >0:
        for i in range(0,unique_country.count(None)+1):
            unique_country.remove(None)
except:
    pass



city_id = {}
country_id={}
for i in range(0, len(unique_city)):
               # city_id[unique_city[i]]='City '+str(i)
                city_id[unique_city[i]]=i+1

for i in range(0, len(unique_country)):
               # country_id[unique_country[i]]='Country '+str(i)
                country_id[unique_country[i]] = i+1

#************************Assigning Country and city id ****************************
for j in ['country_new','city_new']:
    id_co = []
    for i in range(0,len(cit[j])):
        try:
            if j == 'country_new':
                id_co.append(country_id[cit[j][i]])
            if j == 'city_new':
                id_co.append(city_id[cit[j][i]])
        except:
                id_co.append(None)
           
    cit[j+'_id'] = id_co
    
















# =============================================================================
#   Creating museum code name and unique museum id
#    This is step 11, run from line no 415-436
# =============================================================================

def museum_code_name_adc():
    var=[]
    for i,j,k in zip(cit.name,cit.city_new,cit.country_new):
            var.append(i + " " + "(" + j + "," +k+ ")")
     
           
    cit['museum_code_name_adc'] = var

museum_code_name_adc()



#******************************Creating Museum Id*****************

mus_id={}
j=0
for i in cit.name:
    j=j+1
    mus_id[i] = j
    # mus_id[i] = 'Museum '+str(j)




# =============================================================================
# 
# #--------------Mapping the name given with wikipedia's name-----------------------------
#
#                  This is step 12
# =============================================================================


var=[]
j=0
for i in city.name:
    try:
        var.append(mus_id[i])
    except:
        for j in range(0,len(city.name)):
               if city.name[j]==i:
                   city = city.drop([j])
        city = city.reset_index(drop = True)

city['Museum_Id'] = var
#----------------------------Mapping Done--------------------











#--------------------------------Saving and Retreving---------------------------
city.to_csv('city.csv',index = False)
cit.to_csv('cit.csv',index = False)
#cit = pd.read_csv('cit.csv')
#cit = cit.where(pd.notnull(cit), None)
# city = pd.read_csv('city.csv')
# city = cit.where(pd.notnull(city), None)














#-----------------------------converting index into museum index---------------

var=[]
for i in cit.name:
     var.append(mus_id[i]) 
cit['museum_id'] = var

#-----------------------------------------------------------------------------------------------------

# =============================================================================
#    Here we are done with museums and if you want to save it in database then
#                GO to line no 863 and run the function
#       
#        By that we are also done with all the data we need for paintings also
#                   If you  want to save paintings values in database then 833
#                    Go to line no 816 and run the function


# =============================================================================












# =============================================================================
#   To populate country table run from line no 521-651
#           TO send it to databse run the function on line 887

# =============================================================================

country = pd.DataFrame()

country['name'] = unique_country
country['Countrycodename'] = unique_country
country['country_code_name_slug'] = unique_country
country['Countrycodeiso3'] = None
country['Countrycommonname'] = unique_country
country['Countryformalname'] = unique_country
country['Countrycapital'] = None
country['Countrycurrency'] = None
country['Countrycurrencyname'] = None
country['Countrytelephonecode'] = None


def country_info(name):

    url_en=[]
    name_en=[]
 
    for i in name:
        
        text = '{}  wikipedia.org  '.format(i)
        #print('Started')
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
        text = urllib.parse.quote_plus(text)
        google_url = "https://www.google.com/search?hl=en&num=10&cr=us&q={}".format(text)
        response = requestsget(  google_url)
        soup = BeautifulSoup(response.text,'html.parser')
        temp =  soup.find('div',{'class':'r'})
        url_en.append(temp.a['href'])
        
        
        r = requestsget(  temp.a['href'] )
        soup = BeautifulSoup(r.text,'html.parser')
        name_en.append(soup.find('h1',{'id':'firstHeading'}).text)
        
        
       

    country['Wikipediaurl'] = url_en
    country['Name'] = name_en    
            

country_info(country.name)






# =============================================================================
# 
# =============================================================================

def country_url_name_multi_language(url):
    
     for j in ['en','fr','de','it','es','ru','cn','pt','ja']:
        link=[]
        name =[]
        for i in url:
            try:
                print("==>Search country_url_name_multi_language : " , j , "  " , i )
                r  = requestsget( i )
                soup = BeautifulSoup(r.text,'html.parser')
                covers = soup.find('li',{'class':'interlanguage-link interwiki-'+str(j)})
                if covers == None:
                    covers = soup.find('li',{'class':'interlanguage-link interwiki-{} badge-Q17437796 badge-featuredarticle'.format(j)})
                if covers == None:
                    covers = soup.find('li',{'class':'interlanguage-link interwiki-{} badge-Q17437798 badge-goodarticle'.format(j)})

                l = covers.a['href']
                rq = requestsget( covers.a['href'])
                soup = BeautifulSoup(rq.text,'html.parser')
                n = soup.find('h1',{'class':'firstHeading'}).text

                name.append( n )
                link.append( l )

            except:
                link.append(None)
                name.append(None)

        country['Wikipediaurl_'+str(j)] = link
        country['Name_'+str(j)] = name
        

country_url_name_multi_language(country.Wikipediaurl)


for i in range(0,len(country.Wikipediaurl)):
    if country.Wikipediaurl[i] != None:
        n = country.Wikipediaurl[i][8:10]
        if n in ['en','fr','de','it','es','ru','cn','pt','ja']:
            country['Wikipediaurl_'+str(n)][i] = country.Wikipediaurl[i]

def correct1(url,lang):
    correction=[]
    for i in url:
        if i != None:
            print("==>City English name : " + i)
            rq = requestsget( i )
            soup = BeautifulSoup(rq.text,'html.parser')
            correction.append(soup.find('h1',{'class':'firstHeading'}).text)
        else:
            correction.append(None)
    country['Name_'+str(lang)] = correction


for i in  ['en','fr','de','it','es','ru','cn','pt','ja']:
    correct1(country['Wikipediaurl_'+str(i)],i)






def country_description_in_multilanguage(name,lang):
    description= []
    print('==>country_description_in_multilanguage :',lang)
    for i in name:
        try:
            wikipedia.set_lang(lang)
            d = wikipedia.summary(i)
            description.append(d)
        except:
            try:
                wikipedia.set_lang(lang)
                d = wikipedia.summary(wikipedia.suggest(i))
                description.append(d)
            except:
                description.append(None)
    country['Description_'+str(lang)] = description
    

for i in ['en','fr','de','it','es','ru','cn','pt','ja']:
        country_description_in_multilanguage(country['Name_'+i], i)















print(" -------- doing countries images -------- ")

def country_add_image_url(url_en,name):
    print("==>country_add_image_url : " + name )
    img_url=[]
    for j,l in zip(url_en,name):
        response = requestsget( j )
        soup = BeautifulSoup(response.text,'html.parser')
        url = soup.find_all('img')
        count = 0
        for i in url:
            count = count+1
            if i['src'][-3:] == 'png' and i['src']!=None and count ==3:
                img_url.append((i['src']))
                #print(l)
                break
            elif len(url)-count==0:
                img_url.append(None)

    country['PhotoURL'] = img_url


#country_add_image_url(country.Wikipediaurl_en,country.name)
for i in country.index:
    try:
        country.loc[ i , 'PhotoURL'] = 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Icon-round-Question_mark.svg/200px-Icon-round-Question_mark.svg.png'
        country.loc[ i , 'country_image'  ] = requestsgetImageURL( country.loc[ i , 'name'] , MinimumWidth=1200 , MinimumHeight=300 , TargetRatio=2.5 )
        country.loc[ i , 'country_thumb_image'  ] = requestsgetImageURL( country.loc[ i , 'name'] , MinimumWidth=300 , MinimumHeight=300 , TargetRatio=1 )
    except:
        country.loc[ i , 'PhotoURL'] = ''
        country.loc[ i , 'country_image'  ] = ''
        country.loc[ i , 'country_thumb_image'  ] = ''

print(" -------- countries images done -------- ")





country['Rank'] = None
country['Allmuseumscount'] = None
country['Countrytype'] = None

var=[]
for i in country.name:
    var.append(country_id[i])

country['country_id'] = var

country.index.names = ['id']












# =============================================================================
#   To populate city table run from line no 655-826
#           TO send it to databse run the function on line 897
# =============================================================================

#-----------------------------------------------------for city--------------------------------------

co_ci = pd.DataFrame()

var=[]
temp=[]
for i in range(0,len(cit.city_new)):
    if cit.city_new[i] not in var:
        var.append(cit.city_new[i])
        temp.append(cit.country_new[i])

co_ci['city'] = var
co_ci['country'] = temp
co_ci['Cityalternatename'] = var









var=[]
for i,j in zip(co_ci.city,co_ci.country):
    var.append(i + "-" + j)
co_ci['Citycodename'] = var



def city_info(name,country):

    url_en=[]
    name_en=[]
    lat=[]
    long=[]
 
    for i,j in zip(name,country):
        text = '{} {}  wikipedia.org  '.format(i,j)
        #print('Started')
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
        text = urllib.parse.quote_plus(text)
        
        google_url = "https://www.google.com/search?hl=en&num=10&cr=us&q={}".format(text)
        print("==>city_info search google for : " + text )
        response = requestsget(  google_url )
        soup = BeautifulSoup(response.text,'html.parser')
        
        temp =  soup.find('div',{'class':'r'})
        try:
             ur = temp.a['href']
             url_en.append(ur)
        except:
            print('In except')
            temp = soup.find('div',{'class':'BNeawe UPmit AP7Wnd'}).text
            temp = temp.replace(' › ', '/')
            ur = temp
            url_en.append(ur)
        
        r = requestsget( ur)
        soup = BeautifulSoup(r.text,'html.parser')
        #print(soup.find('h1',{'id':'firstHeading'}).text)
        name_en.append(soup.find('h1',{'id':'firstHeading'}).text)
        try:
            covers = soup.find('span',{'class':'geo'}).text
            covers = covers.split(';')
            if len(covers)<=1:
                covers = soup.find('span',{'class':'geo'}).text
                covers = covers.split(',')
                
               
        except:
            try:
                covers = [soup.find("span", {'class': 'latitude'}).text,soup.find("span", {'class': 'longitude'}).text]
            except:
                location = geolocatorgeocode( 'Manhattan Community Board 5' )
                covers=[location.latitude,location.longitude]
                
        location = geolocatorreverse( covers[0],covers[1] )
        
        lat.append( location.raw['lat'])
        long.append(location.raw['lon'])

    co_ci['Wikipediaurl'] = url_en
    co_ci['Name'] = name_en    
    co_ci['lat'] = lat
    co_ci['long'] = long
            

city_info(co_ci.city,co_ci.country)






def city_url_name_multi_language(url):
    
     for j in ['en','fr','de','it','es','ru','cn','pt','ja']:
        link=[]
        name =[]
        for i in url:
            try:
                print("==>city_url_name_multi_language  : " , j , "    " ,  i)
                r  = requestsget( i )
                soup = BeautifulSoup(r.text,'html.parser')
                covers = soup.find('li',{'class':'interlanguage-link interwiki-'+str(j)})
                if covers == None:
                    covers = soup.find('li',{'class':'interlanguage-link interwiki-{} badge-Q17437796 badge-featuredarticle'.format(j)})
                if covers == None:
                    covers = soup.find('li',{'class':'interlanguage-link interwiki-{} badge-Q17437798 badge-goodarticle'.format(j)})
                    
                l = covers.a['href']
                rq = requestsget( covers.a['href'])
                soup = BeautifulSoup(rq.text,'html.parser')
                n = soup.find('h1',{'class':'firstHeading'}).text

                name.append( n )
                link.append( l )
            except:
                link.append(None)
                name.append(None)
            
        co_ci['Wikipediaurl_'+str(j)] = link
        co_ci['Name_'+str(j)] = name
		
        
city_url_name_multi_language(co_ci.Wikipediaurl)



for i in range(0,len(co_ci.Wikipediaurl)):
    if co_ci.Wikipediaurl[i] != None:
        n = co_ci.Wikipediaurl[i][8:10]
        if n in ['en','fr','de','it','es','ru','cn','pt','ja']:
            co_ci['Wikipediaurl_'+str(n)][i] = co_ci.Wikipediaurl[i]

def correct2(url,lang):
    correction=[]
    for i in url:
        if i != None:
            print("==>City English name : " + i)
            rq = requestsget( i )
            soup = BeautifulSoup(rq.text,'html.parser')
            correction.append(soup.find('h1',{'class':'firstHeading'}).text)
        else:
            correction.append(None)
    co_ci['Name_'+str(lang)] = correction


for i in  ['en','fr','de','it','es','ru','cn','pt','ja']:
    correct2(co_ci['Wikipediaurl_'+str(i)],i)







def city_description_in_multilanguage(name,lang):
    description= []
    print('===>city_description_in_multilanguage  for :',lang)
    for i in name:
        try:
            wikipedia.set_lang(lang)
            d = wikipedia.summary(i)
            description.append(d)
        except:
            try:
                wikipedia.set_lang(lang)
                d = wikipedia.summary(wikipedia.suggest(i))
                description.append(d)
            except:
                description.append(None)
    co_ci['Description_'+str(lang)] = description

for i in ['en','fr','de','it','es','ru','cn','pt','ja']:
        city_description_in_multilanguage(co_ci['Name_'+i], i)














print(" -------- doing cities images -------- ")


def city_add_image_url(url_en,name):
    print("==>city_add_image_url  : " + name )
    img_url=[]
    for j,l in zip(url_en,name):
        response = requestsget( j )
        soup = BeautifulSoup(response.text,'html.parser')
        url = soup.find_all('img')
        count = 0
        for i in url:
            count = count+1
            if i['src'][-3:] == 'jpg' and i['src']!=None:
                img_url.append((i['src']))
                #print(l)
                break
            elif len(url)-count==0:
                img_url.append(None)

    co_ci['PhotoURL'] = img_url


#city_add_image_url(co_ci.Wikipediaurl_en,co_ci.city)

for i  in co_ci.index:
    try:
        Q = co_ci.loc[ i , 'Name'] + " , " + co_ci.loc[ i , 'Name'] + " (" + co_ci.loc[ i , 'country'] + ")"
        co_ci.loc[ i , 'PhotoURL'] = requestsgetImageURL( Q , MinimumWidth=1200 , MinimumHeight=300 , TargetRatio=2.5 )
        co_ci.loc[ i , 'city_thumb_image'] = requestsgetImageURL( Q ,  MinimumWidth=300 , MinimumHeight=300 , TargetRatio=1 )
    except:
        co_ci.loc[i, 'PhotoURL'] = ''
        co_ci.loc[i, 'city_thumb_image'] = ''

print(" -------- cities images done -------- ")







print(" -------- Doing Ranks -------- ")

co_ci['Rank'] = None


def adding_id():
    var=[]
    for i in co_ci.country:
        var.append(country_id[i])
    co_ci['country_id'] = var
    
    var=[]
    for i in co_ci.city:
        var.append(city_id[i])
    co_ci['city_id']= var


adding_id()




co_ci.index.names = ['id']














rank_painting = dataframe.Champ51
#------------------------------------------------------------------------------
var=[]
for i in city.Museum_Id:
    var.append(i)
# -----------------------------------------------------------------------------
r =[]
for i in cit.museum_id:
    r.append(var.count(i))

# -----------------------------------------------------------------------------


rank_museum = pd.DataFrame({'mus_id':cit.museum_id,'rank':r})
var = []
for i in rank_museum.mus_id:
    for given,check in mus_id.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
        if check == i:
            var.append(given)
rank_museum['name'] = var 
            
rank = pd.DataFrame()
def adding_ranks():
    var_ci=[]
    var_co=[]
    for i in range(0,len(city.name)):
        tempo =cit[cit.name == city['name'][i]]
        tempo = list(tempo.loc[tempo.index[0]][:2])
        var_ci.append(tempo[0])
        var_co.append(tempo[1])
    rank['city'] = var_ci
    rank['country'] = var_co
    
    var=[]
    var_co=[]
    for i in range(0,len(rank.city)):
        var.append(city_id[rank.city[i]])
        var_co.append(country_id[rank.country[i]])
    rank['c_id'] = var
    rank['co_id'] = var_co
adding_ranks()
    
    
    

var =[]
for i in country_id.values():
    var.append(list(rank.co_id).count(i))

rank_country = pd.DataFrame({'name':unique_country, 'rank':var})

var =[]
for i in city_id.values():
    var.append(list(rank.c_id).count(i))
rank_city = pd.DataFrame({'name':unique_city,'rank':var})

print(" -------- Ranks Done -------- ")














#--------------------------------------------------Sending it to database--------------------------------------------------------

# *************************Inserting Into Table Painting************************
def insert_into_painting():
    df = pd.DataFrame()
    df['image_url'] = dataframe['Urlimagegrande']
    df['reference_code'] = dataframe['Refarticle']
    
    df['reference_code_slug'] = dataframe['Refarticle']
    
    df['artist_name'] =dataframe['Champ1']
    for i in ['EN','FR','DE','IT','ES','RU','CN','PT','JA']:
        df['painting_title_'+str(i)] = dataframe['Champ5_'+str(i).lower()]
    
    df['IsArtworkcopyrighted'] = dataframe['Isartworkcopyrighted']
    df['image_thumbnail'] = dataframe['Urlimagepetite']
    df['image_large'] =dataframe['Urlimagegrande']
    
    var =[]
    for i,j in zip(dataframe['Refarticle'],dataframe['Isartworkcopyrighted']):
        if j!=1:
            var.append("https://ArtsDot.com/ADC/Art.nsf/Buy?RA="+i)
        else:
            var.append(None)
    df['buy_button_url'] = var
    
    df['museum_id'] = city['Museum_Id']
    

# 
    df.index.names = ['id']
    df['rank'] = rank_painting
    try:
        con = sqlite3.connect('db.sqlite3')
        cur = con.cursor()
        cur.execute('delete from sqlite_sequence where name="app_museum_painting"')
        cur.execute('delete from app_museum_painting')
        for i in df.index:
            try:
                t = pd.DataFrame()
                t =t.append(df.loc[i])
                t.to_sql('app_museum_painting', con=con, if_exists='append', index =False )
            except Exception as e:
                print("This error can be skipped:",e)
        con.commit()
        con.close()
    except Exception as e:
        print("Database Error :",e)













#******************************Inserting Into Table Museums*****************************
def insert_into_museum():
    df=pd.DataFrame()
    df['PhotoURL'] = cit.PhotoURL
    df['museum_image'] = cit.museum_image
    df['museum_thumb_image'] = cit.museum_thumb_image
    df['Museumcodename'] = cit.name
    df['Museumfullcodenameadc'] = cit.museum_code_name_adc
    df['museum_code_name_adc_slug'] = cit.museum_code_name_adc
    df['Countrycodename'] = cit.country_new
    df['Museumurl_en'] = cit.official_url
    df['Museumofficialvisitorcount'] = 0

    for i in ['en','fr','de','it','es','ru','cn','pt','ja']:
        df['Wikipediaurl_'+i] = cit['url_wiki'+i]
        df['Description_'+i] = cit['description_'+i]
        df['Name_'+i] = cit['name_'+i]
        
    df['Museumpaintingscount'] = rank_museum['rank']
    df['Rank'] = rank_museum['rank']
    df['Museumfullcodenameduplicate'] = cit.museum_code_name_adc
    df['city_id'] = cit.city_new_id
    df['country_id'] = cit.country_new_id


    df.index = cit.index
    
    #****************Sending it to database***********************
    df.index.names = ['id']
    df.index += 1 
    try:
        con = sqlite3.connect('db.sqlite3')
        cur = con.cursor()
        cur.execute('delete from sqlite_sequence where name="app_museum_museum"')
        cur.execute('delete from app_museum_museum')
        for i in df.index:
            try:
                t = pd.DataFrame()
                t =t.append(df.loc[i])
                t.to_sql('app_museum_museum', con=con, if_exists='append',index=False )
        
            except Exception as e:
                print("This error can be skipped:",e)
        #df.to_sql('app_museum_museum', con=con, if_exists='append',index=False )
        con.commit()
        con.close()
    except Exception as e:
        print("Database Error :",e)








def insert_into_country():
    df = pd.DataFrame()
    df['PhotoURL'] = country['PhotoURL']
    df['Countrycodename'] = country['Countrycodename']
    df['country_code_name_slug'] = country['Countrycodename']
    df['Countrycodeiso3'] = None
    df['Countrycommonname'] = country['Countrycommonname']
    df['Countryformalname'] = country['Countryformalname']
    df['Countrytype'] =None
    df['Countrycapital'] = None
    df['Countrycurrency'] = None
    df['Countrycurrencyname'] = None
    df['Countrytelephonecode'] = None
    df['country_thumb_image'] = country['country_image']
    df['country_image'] = country['country_image']
    
    for i in ['en','fr','de','it','es','ru','cn','pt','ja']:
        df['Wikipediaurl_'+i] = country['Wikipediaurl_'+i]
        df['Description_'+i] = country['Description_'+i]
        df['Name_'+i] = country['Name_'+i]
        
    df['Allmuseumscount'] = rank_country['rank']
    df['Rank'] = rank_country['rank']
    
    
    try:
        con = sqlite3.connect('db.sqlite3')
        cur = con.cursor()
        cur.execute('delete from sqlite_sequence where name="app_museum_country"')
        cur.execute('delete from app_museum_country')
        for i in df.index:
                try:
                    t = pd.DataFrame()
                    t =t.append(df.loc[i])
                    t.to_sql('app_museum_country', con=con, if_exists='append', index =False )
                except Exception as e:
                    print("This error can be skipped :",e)
        con.commit()
        con.close()
    except Exception as e:
        print("Database Error :",e)






def insert_into_city():
    df = pd.DataFrame()
    df['PhotoURL'] = co_ci['city_thumb_image']
    df['Citycodename'] = co_ci['Citycodename']
    df['City_code_name_slug'] = co_ci['Citycodename']
    df['Citylatitude'] = co_ci['lat']
    df['Citylongitude'] = co_ci['long']
    df['Citypopulation'] =None
    df['Citytimezone'] = None
    df['Cityalternatename'] = co_ci['Cityalternatename']
    df['city_thumb_image'] = co_ci['city_thumb_image']
    df['city_image'] = co_ci['city_thumb_image']
    
    for i in ['en','fr','de','it','es','ru','cn','pt','ja']:
        df['Wikipediaurl_'+i] = co_ci['Wikipediaurl_'+i]
        df['Description_'+i] = co_ci['Description_'+i]
        df['Name_'+i] = co_ci['Name_'+i]
        
    df['Allmuseumscount'] = rank_city['rank']
    df['Rank'] = rank_city['rank']
    df['country_id'] = co_ci['country_id']
        
    try:
        con = sqlite3.connect('db.sqlite3')
        cur = con.cursor()
        cur.execute('delete from sqlite_sequence where name="app_museum_city"')
        cur.execute('delete from app_museum_city')
        for i in df.index:
                    try:
                        t = pd.DataFrame()
                        t =t.append(df.loc[i])
                        t.to_sql('app_museum_city', con=con, if_exists='append', index = False )
                    except Exception as e:
                            print("This error can be skipped:",e)
        con.commit()
        con.close()
    except Exception as e:
        print("Database Error :",e)








    
def SaveFullQuerySql():
    con = sqlite3.connect('db.sqlite3')
    df = pd.read_sql_query("""
    SELECT app_museum_painting.Reference_Code,
           app_museum_painting.artist_name,
           app_museum_painting.painting_title_EN,
           app_museum_painting.museum_id,
           app_museum_museum.Museumfullcodenameadc,
           app_museum_museum.city_id,
           app_museum_city.Citycodename,
           app_museum_museum.country_id,
           app_museum_country.Countrycodename
      FROM app_museum_painting

    left JOIN app_museum_museum ON app_museum_museum.id = app_museum_painting.museum_id
    left JOIN app_museum_city ON app_museum_city.id = app_museum_museum.city_id
    left JOIN app_museum_country ON  app_museum_country.id = app_museum_museum.country_id
    """, con)
    df.to_csv('DbFullQuerys.CSV', index = False )
    con.close()




# =============================================================================
# =============================================================================
print( "---------Writing in database SQL--------")
insert_into_country()
insert_into_city()
insert_into_museum()
insert_into_painting()
print( "---------Writing DbFullQuerys.XLS--------")
SaveFullQuerySql()
print ( " ------- wow finished ! -------")
# =============================================================================
# =============================================================================







