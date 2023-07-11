#!/usr/bin/python3
# Threader3000 - Multi-threader Port Scanner
# A project by The Mayor
# v1.0.7
# https://github.com/dievus/threader3000
# Licensed under GNU GPLv3 Standards.  https://www.gnu.org/licenses/gpl-3.0.en.html


import socket
import os
import signal
import time
import threading
import sys
import subprocess
from queue import Queue
from datetime import datetime

# Start Threader3000 with clear terminal
# subprocess.call('clear', shell=True)

# Main Function
def main():
    print_lock = threading.Lock()
    discovered_ports = []

   # Welcome Banner
    print("-" * 60)
    print("        Threader 3000 - Multi-threaded Port Scanner          ")
    print("                       Version 1.1.0                    ")
    print("-" * 60)
    time.sleep(1)

   # Default time out
    default_timeout = input("Set default timeout (press Enter for 0.3): ")
    if default_timeout:
        try:
            default_timeout = float(default_timeout)
        except ValueError:
            print("Invalid timeout value. Defaulting to 0.3 seconds.")
            default_timeout = 0.3
    else:
        default_timeout = 0.3
        
    socket.setdefaulttimeout(default_timeout) 
   
   # IP
    target = os.getenv("TARGET_IP", "")
    if not target:
      target = input("Enter your target IP address or URL here: ")
    error = ("Invalid Input")
    try:
        t_ip = socket.gethostbyname(target)
    except (UnboundLocalError, socket.gaierror):
        print("\n[-]Invalid format. Please use a correct IP or web address[-]\n")
        sys.exit()

    #Summary
    print("-" * 60)
    print("Settings Summary:")
    print("-" * 60)
    print(f"Target: {target}")
    print(f"Default Timeout: {socket.getdefaulttimeout()} seconds")
    print(f"Address Family: {socket.AF_INET}, Socket Type: {socket.SOCK_STREAM}")
    print("-" * 60)
    confirm = input("Start scanning with these settings? (y/n): ")
    if confirm.lower() != "y":
        main()
    print("Time started: "+ str(datetime.now()))
    print("-" * 60)


    t1 = datetime.now()

    def portscan(port):
       with print_lock:
         progress = (1 - (q.unfinished_tasks / 65535)) * 100
         print(f"\{progress:.1f}% scanned", end='\r', flush=True)

       s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       try:
          portx = s.connect((t_ip, port))
          with print_lock:
             print("Port {} is open".format(port))
             discovered_ports.append(str(port))
          portx.close()

       except (ConnectionRefusedError, AttributeError, OSError):
          pass

    def threader():
       while True:
          worker = q.get()
          portscan(worker)
          q.task_done()
      
    q = Queue()
     
    #startTime = time.time()
     
    for x in range(200):
       t = threading.Thread(target = threader)
       t.daemon = True
       t.start()

    for worker in range(1, 65536):
       q.put(worker)

    q.join()

    t2 = datetime.now()
    total = t2 - t1
    print("Port scan completed in "+str(total))
    print("-" * 60)
    print("Threader3000 recommends the following Nmap scan:")
    print("*" * 60)
    print("nmap -p{ports} -sV -sC -T4 -Pn -oA {ip} {ip}".format(ports=",".join(discovered_ports), ip=target))
    print("*" * 60)
    nmap = "nmap -p{ports} -sV -sC -T4 -Pn -oA {ip} {ip}".format(ports=",".join(discovered_ports), ip=target)
    t3 = datetime.now()
    total1 = t3 - t1

#Nmap Integration (in progress)

    def automate():
       choice = '0'
       while choice =='0':
          print("Would you like to run Nmap or quit to terminal?")
          print("-" * 60)
          print("1 = Run suggested Nmap scan")
          print("2 = Run another Threader3000 scan")
          print("3 = Exit to terminal")
          print("-" * 60)
          choice = input("Option Selection: ")
          if choice == "1":
             try:
                print(nmap)
                os.mkdir(target)
                os.chdir(target)
                os.system(nmap)
                #convert = "xsltproc "+target+".xml -o "+target+".html"
                #os.system(convert)
                t3 = datetime.now()
                total1 = t3 - t1
                print("-" * 60)
                print("Combined scan completed in "+str(total1))
                print("Press enter to quit...")
                input()
             except FileExistsError as e:
                print(e)
                exit()
          elif choice =="2":
             main()
          elif choice =="3":
             sys.exit()
          else:
             print("Please make a valid selection")
             automate()
    automate()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        quit()
