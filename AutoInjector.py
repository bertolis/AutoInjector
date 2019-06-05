from sql import *
from xss import *   # Comment for linux

while True:
    print "\n\n<--!=========================!-->AutoInjector<--!=========================!-->\n\n\n"
    print "1. SQL Injection"
    print "2. XSS Injection"
    ch = (raw_input()).strip()
    print ""
    if ch == "1" or ch == "2":
        break

if ch == "1":
    sql()
if ch == "2":
    xss()

# Uncomment for linux
# raw_input('')
