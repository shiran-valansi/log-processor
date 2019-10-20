from decimal import Decimal, InvalidOperation
from collections import defaultdict
import sys
import time

TIMESTAMP = 0
USER_ID = 1
EVENT = 2
TIME_DELTA = 0.001

logs_by_user_id = defaultdict(list)
visited = defaultdict(list)


def detect_sequence(user_id, logs):
    """
        Detects the consecutive sequence 'A', 'B', 'C' in user logs list
        Input: user id and list of their logs
        Output: print statement noting that the sequence A B C is detected

        >>> detect_sequence(10, [(Decimal('1'), 10, 'A'), (Decimal('2'), 10, 'B'), (Decimal('3'), 10, 'C')])
        sequence detected for user: 10, timestamp: 3

        >>> detect_sequence(10, [(Decimal('1'), 10, 'A'), (Decimal('2'), 10, 'B'), (Decimal('3'), 10, 'C')])

        >>> detect_sequence(10, [(Decimal('1'), 10, 'A'), (Decimal('2'), 10, 'B'), (Decimal('3'), 10, 'A')])

        >>> detect_sequence(10, [])

        >>> detect_sequence(10, [(Decimal('1'), 10, 'A'), (Decimal('2'), 10, 'B'), (Decimal('3'), 10, 'A'), (Decimal('4'), 10, 'B'), (Decimal('5'), 10, 'C')])
        sequence detected for user: 10, timestamp: 5

        >>> detect_sequence(10, [(Decimal('5'), 10, 'A'), (Decimal('6'), 10, 'B'), (Decimal('7'), 10, 'C'), (Decimal('8'), 10, 'A'), (Decimal('9'), 10, 'B'), (Decimal('10'), 10, 'C')])
        sequence detected for user: 10, timestamp: 7
        sequence detected for user: 10, timestamp: 10

    """
    n = len(logs)
    i = 0

    while i < n - 2:
        if (logs[i][EVENT] == 'A' and
            logs[i][TIMESTAMP] not in visited[user_id] and
            logs[i + 1][EVENT] == 'B' and
            logs[i + 2][EVENT] == 'C'):

            visited[user_id].append(logs[i][TIMESTAMP])
            print('sequence detected for user: {}, timestamp: {}'.format(
                user_id, logs[i + 2][TIMESTAMP]))
            i += 3

        else:
            i += 1
    return


def binary_search(lst, target, start, end):
    """ Binary search for where the target number should be placed
        INPUT: a list of logs, target number, start index, end index
        OUTPUT: the index in which the target should be placed in the list

        >>> binary_search([(Decimal('1'), 10, 'A'), (Decimal('2'), 10, 'B'), (Decimal('3'), 10, 'C')], Decimal('2.5'), 0, 2)
        2
        >>> binary_search([], Decimal('2.5'), 0, 0)
        0
        >>> binary_search([(Decimal('1'), 10, 'A'), (Decimal('2'), 10, 'B'), (Decimal('3'), 10, 'C')], Decimal('4'), 0, 2)
        3
        >>> binary_search([(Decimal('1'), 10, 'A'), (Decimal('2'), 10, 'B'), (Decimal('3'), 10, 'C')], Decimal('0'), 0, 2)
        0
        >>> binary_search([(Decimal('1'), 10, 'A'), (Decimal('2'), 10, 'B'), (Decimal('3'), 10, 'C')], Decimal('2'), 0, 2)
        1

    """

    if len(lst) == 0:
        return 0

    if start == end:
        if target < lst[start][TIMESTAMP]:
            return start
        else:
            return start + 1

    if start > end:
        return start

    mid = (start + end) // 2

    if lst[mid][TIMESTAMP] < target:
        return binary_search(lst, target, mid + 1, end)

    if lst[mid][TIMESTAMP] > target:
        return binary_search(lst, target, start, mid - 1)

    return mid


def parse_line(line):
    """
        Parses the input line into a tuple of 3 items:
        timestamp, user_id, event type
        For input errors and exeptions we return None

        >>> parse_line('')
        ()

        >>> parse_line('123')
        ()

        >>> parse_line('||')
        ()

        >>> parse_line('1|2|3|A')
        ()

        >>> parse_line('*|2|A')
        ()

        >>> parse_line('1|*|A')
        ()

        >>> parse_line('1|2|*')
        ()

        >>> parse_line('1|2|A')
        (Decimal('1'), 2, 'A')

    """

    try:
        log_line = line.strip().split('|')

        if len(log_line) != 3:
            return ()

        log_line[TIMESTAMP] = Decimal(log_line[TIMESTAMP])

        log_line[USER_ID] = int(log_line[USER_ID])

        if not log_line[EVENT].isalpha():
            return ()

        return tuple(log_line)

    except InvalidOperation:
        return ()

    except ValueError:
        return ()


def print_logs(user_id, logs):
    print('--user_id--', user_id)
    for log in logs:
        print('{}, {}, {}'.format(log[TIMESTAMP], log[USER_ID], log[EVENT]))


###############################################################################


def main():
    """ Given a set of log files that encode user event streams
        (information about events that occur for users using e.g a web product)
        we record whenever a given user triggers a specific sequence of events.
        The program will identify users that trigger the sequence `A, B, C`
        at some point during their use (without intervening events).
        It prints the `user_id` and `timestamp` of the last element in the
        completed sequence for each occurrence.
    """
    try:
        files = [open(filename) for filename in sys.argv[1:]]

        if not files:
            print('error: no input files given')
            return

        start_time = time.time()

        while True:

            for file in files:
                # Read the files line by line
                where = file.tell()
                line = file.readline()
                if not line:
                    file.seek(where)
                else:
                    log_line = parse_line(line)
                    if not log_line:
                        continue

                    user_id = log_line[USER_ID]
                    
                    # put in dictionary by user id
                    index = binary_search(logs_by_user_id[user_id], log_line[
                        TIMESTAMP], 0, len(logs_by_user_id[user_id]) - 1)

                    logs_by_user_id[user_id].insert(index, log_line)

                    curr_time = time.time()

                    if curr_time - start_time > TIME_DELTA:
                        detect_sequence(user_id, logs_by_user_id[user_id])
                        start_time = curr_time

            # sleep to avoid excessive cpu consumption
            time.sleep(0.001)

    finally:
        for file in files:
            file.close()


if __name__ == "__main__":
    main()
