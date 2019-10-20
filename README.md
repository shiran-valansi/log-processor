Online log aggregator and processor
===================================


Objective:
-----------------------------------
Given a set of log files that encode user event streams (information about events that occur for users using e.g a web product), we want to record whenever a given user triggers a specific sequence of events.

Each log file is a sequence of lines of the form `<timestamp>|<user_id>|<event_type>`, where `timestamp` is the unix timestamp (including fractional seconds), `user_id` is a numeric unique user identifier, and `event_type` is a character identifying the type of event that took place, e.g. “A”, “B”, “C”, “D” etc.

Events for a given user may span multiple log files (consider for example the case of a load-balanced set of web-servers recording user event streams).

The program identifies users that trigger the sequence `A, B, C` at some point during their use (without intervening events). It outputs the `user_id` and `timestamp` of the last element in the completed sequence for each occurrence.

The log files are streams, and as such can be actively appended to while the program is running, so **the program should continue to report matches in an online fashion as new logs are generated.** The program should continue to run until interrupted by the user by e.g. ctrl-C.

To clear the log files and start over, run:
```
sh clear-logs.sh
```


Example:
----------------------------------------
Input:
log-0.log:

```
1471485412.464435|85423|O
1471485479.4937239|85423|B
1471485574.7656903|21259|I
1471485627.1087866|85423|N
1471485720.874477|21259|B
1471485761.9205022|13320|A
1471485790.539749|85423|H
1471485833.8451884|13320|B
1471485839.870293|85423|B
1471485931.753138|13320|G
1471485992.004184|13320|B
1471485992.004184|85423|F
1471486101.962343|13320|N
1471486201.0|21259|P
```

log-1.log

```
1471485342.046025|21259|O
1471485369.1589959|13320|C
1471485383.8451884|21259|G
1471485503.5941422|13320|O
1471485548.7824268|21259|D
1471485634.6401675|13320|P
1471485692.2552302|21259|B
1471485769.4518828|85423|K
1471485806.3556485|85423|O
1471485860.58159|13320|C
1471486038.6987448|21259|L
1471486106.8577406|85423|F
1471486157.6945608|21259|P
```

Output:
`sequence detected for user: 13320, timestamp: 1471485860.58159`


Testing and Invocation
----------------------
Run `log_processor.py` with the log filenames as arguments: 

```python log_processor.py log-0.log log-1.log log-2.log log-3.log```

In another session run ```ruby log-gen.rb``` to generate a set of log files for testing. 

DocTests are triggered by running the `log_processor_tests.py` file


Code Description:
---------------------
We run through the log files line by line.
We split each line into a tuple of 3 cells: timestamp, user id and event type.
Each tuple `log_line` is placed into the dictionary `logs_by_user_id`.
Each key of the dictionary is a user id, and each value a list of logs matching that user id. 
The `log_line` is placed in the dictionary in a sorted manner by the timestamp,
using binary search to find the index in which it should be placed.
Every `TIME_DELTA` time we call on the function `detect_sequence`,
which checks to see if the current user's logs have generated the sequence A,B,C.
We keep a `visited` dictionary which keeps the desired sequences we have already found,
in order to not record (print) them more than once.

Comments and Future Work:
---------
In order to be space efficient, we can erase logs we've kept in `logs_by_user_id` 
every certain amount of time, or keep track of the number of logs recorded for each user 
and erase logs after a certain amount of logs.

Assumption: For the case of getting a duplicate sequence within a sequence, we will not record the sequence again. 
For example: let's say for user X we get the following list of logs: [['1', 'X', 'A'], ['2', 'X', 'B'], ['3', 'X', 'C']], and so we print a matching statement. 
If after that we read and add the log ['2.5', 'X', 'C'], we will not trigger aother print statement.
