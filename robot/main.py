# coding=utf-8

##### Robot Test Example #####

from robot import Robot
from time import sleep
import json

# Construct robot

robot = Robot('wellbet')


# Query & transaction

## Test Params
count = 0   ### Query count
do_transaction = True   ### If TRUE, a transaction will be triggered WITHOUT WARNING
loop_time = 10  ### How many times should queries be made
transaction_qty = 5   ### Unit: RMB, if qty = 0, transaction will not be made
refresh_interval = 5   ### Unit: Sec (s)

## Start looping
print('Starting loop...')

while count < loop_time:
    count = count + 1
    print('Entering Loop' + str(count) + "...")
    robot.query() ### So, in each loop one single query will be made

    ## Then we try to place a bet right after the 3rd query
    if count == 1 and do_transaction == True:
        print 'Transaction Start!'

        record3 = robot.container.book
        record3_obj = json.loads(record3)

        ### Bet on the the 1st available transaction of the 1st available match in record
        match_info = record3_obj['i-ots'][0]['egs'][0]['es'][0]
        match_id = match_info['k']
        transaction_id = match_info['o']['ou'][4]
        print transaction_id

        ### Finally, trigger the transation
        robot.transaction(transaction_id, transaction_qty)

    else:
        print 'Transaction aborted'
        print count
        
    print('Exiting loop...')


    ## Wait for next refresh
    sleep(refresh_interval)