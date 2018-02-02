import requests
import json


def prompt_choose_from_list(lst):
    if not lst:
        return

    if len(lst) == 1:
        return lst[0]

    print 'Choose from the following:'
    for i, val in enumerate(lst):
        print '{0} - {1}'.format(i + 1, val.encode('utf-8'))
    choice = raw_input('Enter your choice: ')
    print choice
    while not (choice.isdigit() and (0 < int(choice) < len(lst) + 1)):
        print 'Wrong. Possible choice range: ',
        print '{0} - {1}'.format(1, len(lst))
        choice = raw_input('Try again: ')

    return lst[int(choice) - 1]



class AirportFinder(object):
    url = 'https://raw.githubusercontent.com/ram-nadella/airport-codes/master/airports.json'

    def __init__(self):
        self.airpots_dict = json.loads(requests.get(AirportFinder.url).text)

    def find_airport_code_by_string(self, search_string):
        def filter_airport(airpot):
            possible_fields = ['name', 'city', 'country', 'iata']
            possible_strings = [airpot[field] for field in possible_fields]

            for pos_str in possible_strings:
                if search_string.lower() in pos_str.lower():
                    return True
            return False

        airports = filter(lambda x: filter_airport(x[1]), self.airpots_dict.items())

        if not airports:
            return None

        name_code_dict = {'{0} - {1}'.format(code, airport['name'].encode('utf-8')):code for code, airport in airports}
        return name_code_dict[prompt_choose_from_list(name_code_dict.keys())]
