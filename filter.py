"""
CSC148, Winter 2025
Assignment 1

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2025 Bogdan Simion, Diane Horton, Jacqueline Smith
"""
import time
import datetime
from call import Call
from customer import Customer


class Filter:
    """ A class for filtering customer data on some criterion. A filter is
    applied to a set of calls.

    This is an abstract class. Only subclasses should be instantiated.
    """

    def __init__(self) -> None:
        pass

    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        """ Return a list of all calls from <data>, which match the filter
        specified in <filter_string>.

        The <filter_string> is provided by the user through the visual prompt,
        after selecting this filter.
        The <customers> is a list of all customers from the input dataset.

         If the filter has
        no effect or the <filter_string> is invalid then return the same calls
        from the <data> input.

        Note that the order of the output matters, and the output of a filter
        should have calls ordered in the same manner as they were given, except
        for calls which have been removed.

        Precondition:
        - <customers> contains the list of all customers from the input dataset
        - all calls included in <data> are valid calls from the input dataset
        """
        raise NotImplementedError

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        raise NotImplementedError


class ResetFilter(Filter):
    """
    A class for resetting all previously applied filters, if any.
    """

    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        """ Reset all of the applied filters. Return a List containing all the
        calls corresponding to <customers>.
        The <data> and <filter_string> arguments for this type of filter are
        ignored.

        Precondition:
        - <customers> contains the list of all customers from the input dataset
        """
        filtered_calls = []
        for c in customers:
            customer_history = c.get_history()
            # only take outgoing calls, we don't want to include calls twice
            filtered_calls.extend(customer_history[0])
        return filtered_calls

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Reset all of the filters applied so far, if any"


class CustomerFilter(Filter):
    """
    A class for selecting only the calls from a given customer.
    """

    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        """ Return a list of all unique calls from <data> made or
        received by the customer with the id specified in <filter_string>.

        The <customers> list contains all customers from the input dataset.

        The filter string is valid if and only if it contains a valid
        customer ID.
        - If the filter string is invalid, return the original list <data>
        - If the filter string is invalid, your code must not crash, as
        specified in the handout.

        Do not mutate any of the function arguments!
        """

        # make sure the filter string has no trailing whitespaces
        if filter_string != filter_string.strip():
            return data
        try:
            # given filter_string must be a four digit int
            customer_id = int(filter_string)
            if customer_id <= 0:
                return data
        except ValueError:
            # returns original list if the filter string is invalid
            return data

        target_customer = None
        for customer in customers:
            # find if given filter_string id exists in customers list
            if customer.get_id() == customer_id:
                target_customer = customer
                break

        if target_customer is None:
            # if no match is found return original data
            return data

        unique_calls = []
        customer_lines = target_customer.get_phone_numbers()

        for call in data:

            # if any matching number is found, add to the set of unique calls
            if (call.dst_number in customer_lines or call.src_number
                    in customer_lines):
                unique_calls.append(call)

        # if no calls matched, return data, otherwise return the matched calls
        if not unique_calls:
            return []
        else:
            return unique_calls

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Filter events based on customer ID"


class DurationFilter(Filter):
    """
    A class for selecting only the calls lasting either over or under a
    specified duration.
    """

    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        """ Return a list of all unique calls from <data> with a duration
        of under or over the time indicated in the <filter_string>.

        The <customers> list contains all customers from the input dataset.

        The filter string is valid if and only if it contains the following
        input format: either "Lxxx" or "Gxxx", indicating to filter calls less
        than xxx or greater than xxx seconds, respectively.
        - If the filter string is invalid, return the original list <data>
        - If the filter string is invalid, your code must not crash, as
        specified in the handout.

        Do not mutate any of the function arguments!
        """

        filter_string = filter_string.strip()
        if (not filter_string or filter_string[0] not in ['L', 'G']
                or len(filter_string[1:]) != 3):
            # filter_string must match exact format required
            return data

        try:
            # last three digits must be numbers for duration
            call_length = int(filter_string[1:])
        except ValueError:
            return data

        if call_length == 0:
            return []

        calls = []
        # track unique calls to prevent duplicates
        unique_calls = set()

        for call in data:
            call_id = None
            # return calls less than given duration

            if filter_string[0] == 'L' and call.duration < call_length:
                call_id = (call.src_number, call.dst_number,
                           call.duration, call.time)

            # return calls greater than given duration
            elif filter_string[0] == 'G' and call.duration > call_length:
                call_id = (call.src_number, call.dst_number,
                           call.duration, call.time)

            if call_id:
                if call not in unique_calls:
                    # add call id if its valid and is not a repeat
                    calls.append(call)
                    unique_calls.add(call_id)
        return calls

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Filter calls based on duration; " \
               "L### returns calls less than specified length, G### for greater"


class LocationFilter(Filter):
    """
    A class for selecting only the calls that took place within a specific area
    """

    def apply(self, customers: list[Customer],
              data: list[Call],
              filter_string: str) \
            -> list[Call]:
        """ Return a list of all unique calls from <data>, which took
        place within a location specified by the <filter_string>
        (at least the source or the destination of the event was
        in the range of coordinates from the <filter_string>).

        The <customers> list contains all customers from the input dataset.

        The filter string is valid if and only if it contains four valid
        coordinates within the map boundaries.
        These coordinates represent the location of the lower left corner
        and the upper right corner of the search location rectangle,
        as 2 pairs of longitude/latitude coordinates, each separated by
        a comma and a space:
          lowerLong, lowerLat, upperLong, upperLat
        Calls that fall exactly on the boundary of this rectangle are
        considered a match as well.
        - If the filter string is invalid, return the original list <data>
        - If the filter string is invalid, your code must not crash, as
        specified in the handout.

        Do not mutate any of the function arguments!
        """

        try:
            coordinates = [c.strip() for c in filter_string.split(",")]
            # ensure exactly four coordinates are given
            if len(coordinates) != 4:
                return data

            lower_long = float(coordinates[0])
            lower_lat = float(coordinates[1])
            upper_long = float(coordinates[2])
            upper_lat = float(coordinates[3])

            if not (
                    -79.697878 <= lower_long <= upper_long <= -79.196382
                    and 43.576959 <= lower_lat <= upper_lat <= 43.799568):
                return data
            # ensure lower cord always less than upper cords
        except ValueError:
            return data

        filter_calls = []

        for call in data:
            if call.src_loc and call.dst_loc:
                # assign coordinates for each call, making sure they are valid
                src_long, src_lat = call.src_loc
                dst_long, dst_lat = call.dst_loc

                if (lower_lat <= src_lat <= upper_lat
                    and lower_long <= src_long <= upper_long) or (
                        lower_lat <= dst_lat <= upper_lat
                        and lower_long <= dst_long <= upper_long):
                    # add call to list if it falls under boundary
                    filter_calls.append(call)

        return filter_calls

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Filter calls made or received in a given rectangular area. " \
               "Format: \"lowerLong, lowerLat, " \
               "upperLong, upperLat\" (e.g., -79.6, 43.6, -79.3, 43.7)"


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'time', 'datetime', 'call', 'customer'
        ],
        'max-nested-blocks': 4,
        'allowed-io': ['apply', '__str__'],
        'disable': ['W0611', 'W0703'],
        'generated-members': 'pygame.*'
    })
