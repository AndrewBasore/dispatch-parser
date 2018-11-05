# This file is a complete hack of the AccessPoint's dispatch system
# This file takes the cleaned csv file and generates the text messages to send to the flaggers
# that will be copy-pasted into messenger, and copy-pasted from messenger on the phone to the cellular
# device

import pprint
import csv
import json
import datetime
from datetime import date
import calendar

tomorrow = (date.today() + datetime.timedelta(days=1))
texts = []

pp = pprint.PrettyPrinter(indent=4)

def get_company(order):
    result = ""
    for line in order:
        if line[0] == "Division:":
            return result
        if line[0] == "Company:":
            continue
        result = result + " " + line[0]

def get_supervisor(order):
    result = ""
    for line in order:
        if line[1] == "Supervisor" or line[0] == "":
            continue
        if line[1] == "":
            return result
        result = result + " " + line[1]

def get_cell_num(order):
    return order[3][2]

def get_num_flaggers(order):
    return order[3][3]

def get_location(order):
    result = ""
    for idx, line in enumerate(order):
        if idx == 8:
            return result
        result = result + " " + line[4]

def get_start_time(order):
    return order[3][5]
        
def get_job_code(order):
    return order[3][8]   

def get_lead(order):
    return order[9][1]


def process_order(order):
    # pp.pprint(order)
    weekday = calendar.day_name[tomorrow.weekday()] # This value sets to tomorrow
    company = get_company(order)
    supervisor = get_supervisor(order)
    cell_number = get_cell_num(order)
    num_flaggers = get_num_flaggers(order)
    location = get_location(order)
    start_time = get_start_time(order)
    job_code = get_job_code(order)
    lead = get_lead(order)

   

    
    # Everything up to this works, just have to make template and return the value to functions call
    result = {
        'weekday' : weekday,
        'company' : company,
        'supervisor' : supervisor,
        'cell_number' : cell_number,
        'location': location,
        'start_time' : start_time,
        'job_code' : job_code,
        'lead' : lead
    }

    # Id num_flaggers = 0, site is canceled
    if num_flaggers == "0":
        return ""
    else:
        texts.append(
            "{} Flagging site with {} and {} as the supervisor. Phone Number: {}. {}. Start time: {}. Job code is {}. {} is the lead. Please respond with confirmation".format(
                weekday,
                company,
                supervisor,
                cell_number,
                location,
                start_time,
                job_code,
                lead
            )
        )
        return result 



with open('sites.csv', 'r') as sites_csv:
    csv_reader = csv.reader(sites_csv)
    # Make an array of arrays, each element in orders is an array of lines making up an order
    orders = []
    order = []
    results = []

    # Parse sites out into JSON
    with open('sites/{}.json'.format(tomorrow), 'w') as outfile:
        ro_counter = 0
        for line in csv_reader:
            #Skip first 5 lines, it is the requests off
            if ro_counter < 5:
                ro_counter = ro_counter + 1
                continue

            # If we reach "Taken By: "  Line, order has ended. Append the order thus far and reset field
            if line[0].find("Taken By:") != -1:
                orders.append(order)
                order = []
                continue
            order.append(line)
        for order in orders:
            # if this index has 1 flagger, the site has a flagger on it.
            if order[9][0] == '1':
                results.append(process_order(order))
        json.dump(results, outfile)

    with open('texts/{}.txt'.format(tomorrow), 'w') as outfile:
        for text in texts:
            outfile.write(text + '\n')
    