import csv
import io
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime

# current dade
current_date = str(datetime.now().day) + '/0' + str(datetime.now().month) + '/' + str(datetime.now().year)[2:4]

# current date for file name
date = str(datetime.now().date())
file_name = date

# create a csv file
file = io.open(file_name + ".csv", 'w', encoding='utf-16', newline='')
csv_writer = csv.writer(file, delimiter='\t')
csv_writer.writerow([' כותרת', 'מיקום', 'תיאור המשרה', 'דרישות', 'לינק למשרה'])

# get job master home page source
url = 'https://www.jobmaster.co.il/'
source = requests.get(url).text
soup = bs(source, "html.parser")

# get list of domains
domains_list = []
block_links = soup.find(class_="tabIndex1")
a_list = block_links.find_all('a')
for link in a_list:
    domains_list.append(link)


# return source page from a given url
def get_url(url):
    url = "https://www.jobmaster.co.il/" + url["href"]
    source = requests.get(url).text
    soup = bs(source, "html.parser")
    return soup


# check if the user input is a Number and bigger than 0 and smaller than arr length
def check_user_input_validation(arr, input_num):
    return input_num.isdigit() and (0 <= int(input_num) < len(arr))


# loop until the user input is valid
def enter_a_correct_number(arr, input_num):
    check = check_user_input_validation(arr, input_num)
    return_num = 0
    while not check:
        print('Please enter a valid Number!')
        return_num = input("Try again =  ")
        check = check_user_input_validation(arr, return_num)
    return return_num


def select_domain(domains):
    for num, job in enumerate(domains):
        print("job number = ", num, "title = ", job.text)
    index = enter_a_correct_number(domains, input("please select a domain number = "))
    index = int(index)
    return domains[index]


def select_sub_domain(sub_domain):
    domains_list = get_url(sub_domain)
    domain = domains_list.find(class_="SearchFilterList")
    sub_domain_links = domain.find_all('a')
    for num, job in enumerate(sub_domain_links):
        print("job number = ", num, "title = ", job.text)
    index = enter_a_correct_number(sub_domain_links, input("please select a sub domain number = "))
    index = int(index)
    return sub_domain_links[index]


# loop the list and remove any advertisement
def take_out_advertisement(job_list):
    for job in job_list:
        if 'Mekudam' in job['class']:
            job_list.remove(job)


# return a list of article from a gaven url page
def get_jobs_links(url):
    link = get_url(url)
    jobs = link.find(class_='misrotList')
    jobs = jobs.find_all('article')
    take_out_advertisement(jobs)
    return jobs


# return the next page
def get_next_page(url):
    for page in url:
        if page.text == "הבא»":
            return page


# loop through the pages and collect the jobs from the pages
def get_jobs_from_next_page(url):
    jobs_list = []
    jobs_list += get_jobs_links(url)
    sub_domain_page = url
    while True:
        try:
            link = get_url(sub_domain_page)
            pages = link.find("center")
            pages = pages.find_all('a')
            pages = get_next_page(pages)
            jobs_list += get_jobs_links(pages)
            sub_domain_page = pages
        except Exception:
            print("last page")
            break
    return jobs_list


def get_a_tag_from_jobs_list(job_list):
    a_list = []
    for job in job_list:
        if 'Mekudam' not in job['class']:
            url_job = job.find(class_='JobItemRight')
            a_list.append(url_job.find('a'))
    return a_list


# MAIN LOOP - writer data to csv file
def get_job_body(job_list):
    for job in job_list:
        article_link = get_url(job)

        artical = article_link.find("article")
        job_header = artical.find(class_='CardHeader')
        job_location = artical.find(class_='jobLocation')
        job_description = artical.find(class_='jobDescription')
        job_requirements = artical.find(class_='jobRequirements')
        jop_link = url + job['href']

        csv_writer.writerow([job_header.text,
                             job_location.text,
                             job_description.text,
                             job_requirements.text,
                             jop_link])

        print("Card Header = ", job_header.text)
        print("job Location = ", job_location.text)
        print("job Description = ", job_description.text)
        print("job Requirements = ", job_requirements.text)
        print('jop link = ', jop_link)
        print("-----------------------------------------------------------------")
    file.close()


# --------------------------------------------------------------------------------------------------------------
#  MAIN
# ---------------------------------------------------------------------------------------------------------------
try:
    selected_domain = select_sub_domain(select_domain(domains_list))

    job_list = get_jobs_from_next_page(selected_domain)
    job_list = get_a_tag_from_jobs_list(job_list)

    get_job_body(job_list)
except Exception:
    print('Try again')
