from bs4 import BeautifulSoup
import re
import sys

year_quarters = {"Spring": "Q1", "Summer": "Q2", "Fall": "Q3", "Winter": "Q4" }

def get_filter_dict(soup):
    attributes = {}
    FILTER_COUNT_RE = re.compile(r'[(][0-9]+[)]')
    
    all_divs     = soup.find_all("div")
    filter_divs = [ div for div in all_divs if "class" in div.attrs and 'flex-child' in div.attrs['class']  ]

    for filter_div in filter_divs:
        #Get the category. Like technology, region, status
        filter_category_name = filter_div.text.split("\n")[0]

        if filter_category_name == "Batch":
            filter_category_name = "Timeline"

        html_option_list = filter_div.find_all("option")

        #Get values for this category
        filtered_html_options = [ option for option in html_option_list if "value" in option.attrs and '.attr' in option.attrs['value']  ]
        
        for filtered_html_option in filtered_html_options:
            #Clean up the value of this category
            filtered_html_option_text = FILTER_COUNT_RE.sub('', filtered_html_option.text)
            filtered_html_option_text = filtered_html_option_text.replace("(", "")
            filtered_html_option_text = filtered_html_option_text.replace(")", "")

            #The class attribute has a leading . in the html. Removing the .
            filtered_html_class_keyword = filtered_html_option.attrs['value'].replace(".", "")

            attributes[filtered_html_class_keyword] = {}
            attributes[filtered_html_class_keyword]['filter_category_name'] = filter_category_name

            if filter_category_name == "Timeline":
                timeline = filtered_html_option_text.strip().split(" ")
                timeline_year    = timeline[2]
                timeline_quarter = year_quarters[timeline[1]]

                attributes[filtered_html_class_keyword]['filtered_option_text'] = "{}-{}".format(timeline_year, timeline_quarter)

            else:
                attributes[filtered_html_class_keyword]['filtered_option_text'] = filtered_html_option_text.strip()
    
    return attributes

file_name = "web.html"
startup_list = []

#OPEN FILE
with open(file_name) as f:
    content = f.read()
    soup = BeautifulSoup(content, 'html.parser')

#GET FILTERS
filter_dict = get_filter_dict(soup)

#READ STARTUP DIVS
all_divs     = soup.find_all("div")
startup_divs = [ div for div in all_divs if "class" in div.attrs and 'gallery-item' in div.attrs['class'] and 'mix' in div.attrs['class'] ]
TAG_RE = re.compile(r'<[^>]+>')

for startup_div in startup_divs:
    #The startup name is a the alt property in the img
    image_in_div = startup_div.find("img")
    startup_name = image_in_div.attrs['alt']
    
    #The startup description is under an html p tag
    raw_text  = startup_div.find("p").text
    startup_description = TAG_RE.sub('', raw_text)
    
    #The startup url is in an html anchor
    startup_url  = startup_div.find("a")["href"]

    #ADD COLLECTED STARTUP DATA TO DICT
    startup_info = {}
    startup_info['Name'] = startup_name
    startup_info['URL']  = startup_url

    #The startup div class has attributes used for filtering
    startup_div_class_elements = [ attribute for attribute in startup_div.attrs['class'] if 'attr-' in attribute]
    
    for startup_div_class_element in startup_div_class_elements:
        startup_filter = filter_dict[startup_div_class_element]
        startup_info[startup_filter['filter_category_name']] = startup_filter['filtered_option_text']
    
    startup_info['Description'] = startup_description

    #ADD STARTUP DATA TO STARTUP DICT
    startup_list.append(startup_info)

#PRINT EXCEL
startup_keys = startup_list[0].keys()
print(";".join(startup_keys))

for startup in startup_list:
    startup_output_text = ""
    for key in startup_keys:
        startup_output_text += startup[key] + ";"
    
    startup_output_text = startup_output_text[:-1]
    print(startup_output_text)
