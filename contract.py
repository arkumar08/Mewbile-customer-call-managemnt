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
import datetime
from math import ceil
from typing import Optional
from bill import Bill
from call import Call

# Constants for the month-to-month contract monthly fee and term deposit
MTM_MONTHLY_FEE = 50.00
TERM_MONTHLY_FEE = 20.00
TERM_DEPOSIT = 300.00

# Constants for the included minutes and SMSs in the term contracts (per month)
TERM_MINS = 100

# Cost per minute and per SMS in the month-to-month contract
MTM_MINS_COST = 0.05

# Cost per minute and per SMS in the term contract
TERM_MINS_COST = 0.1

# Cost per minute and per SMS in the prepaid contract
PREPAID_MINS_COST = 0.025


class Contract:
    """ A contract for a phone line

    This is an abstract class and should not be directly instantiated.

    Only subclasses should be instantiated.

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    start: datetime.date
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        self.start = start
        self.bill = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.

        DO NOT CHANGE THIS METHOD
        """
        raise NotImplementedError

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        return self.bill.get_cost()


class TermContract(Contract):
    """ Represents a term contract for a phone line, which inherits
    the Contract class. Lasts for a fixed term.

    start:
         starting date for the contract
    end:
         ending date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    current_month:
        current month of the billing year
    current_year:
        current year of the billing year
    """

    end: datetime.date
    current_month: int
    current_year: int
    bill: Optional[Bill]

    def __init__(self, start: datetime.date, end: datetime.date) -> None:
        """ Create a new Contract with the <start> date and <end>
        """
        Contract.__init__(self, start)
        self.end = end
        self.current_month = start.month
        self.current_year = start.year

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.

        """
        self.bill = bill
        self.current_month = month
        self.current_year = year
        if self.start.month == month and self.start.year == year:
            # add deposit if this is the start of the month
            self.bill.add_fixed_cost(TERM_DEPOSIT)

        # set rate for bills
        self.bill.set_rates("TermContract", TERM_MINS_COST)
        # add monthly cost to bill
        self.bill.add_fixed_cost(TERM_MONTHLY_FEE)
        # add free mins to bill
        self.bill.add_free_minutes(TERM_MINS)

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

       Precondition:
       - a bill has already been created for the month+year when the <call>
       was made. In other words, you can safely assume that self.bill has been
       already advanced to the right month+year.
       """

        # calculate the length of the call
        call_length = ceil(call.duration / 60.0)
        # calculate how many free minutes are left after call
        time_left = self.bill.free_min - call_length

        if time_left > 0:
            # take away free minutes if customer has enough
            self.bill.free_min -= time_left
        else:
            # user has no free minds left, so charge them
            self.bill.add_billed_minutes(abs(time_left))
            self.bill.free_min = 0

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancellation is requested.
        """

        # if contract is closed prematurely, user does not receive refund
        if self.current_year < self.end.year:
            return self.bill.get_cost()
        if (self.current_year == self.end.year
                and self.current_month < self.end.month):
            return self.bill.get_cost()
        else:
            # refund calculated returns the cost of the bill minus the deposit
            refund = self.bill.get_cost() - TERM_DEPOSIT
            return refund


class MTMContract(Contract):
    """ Represents an MTM contract for a phone line, which inherits
    the Contract class

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """

    def __init__(self, start: datetime.date) -> None:
        """ Create a new Contract with the <start> date
        """
        Contract.__init__(self, start)

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        self.bill = bill
        self.bill.set_rates("MTMContract", MTM_MINS_COST)
        self.bill.add_fixed_cost(MTM_MONTHLY_FEE)

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

       Precondition:
       - a bill has already been created for the month+year when the <call>
       was made. In other words, you can safely assume that self.bill has been
       already advanced to the right month+year.
       """
        call_length = ceil(call.duration / 60.0)
        # charge user for entire duration of call
        self.bill.add_billed_minutes(call_length)


class PrepaidContract(Contract):
    """ Represents a prepaid contract for a phone line,
    which inherits the Contract class

    === Public Attributes ===
    start:
         starting date for the contract
    balance:
        float amount of money that the customer owes
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """

    balance: float

    def __init__(self, start: datetime.date, balance: float) -> None:
        """ Create a new Contact with the <start> date.
        """
        Contract.__init__(self, start)
        self.balance = -balance

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        self.bill = bill
        self.bill.set_rates("PrepaidContract", PREPAID_MINS_COST)

        # if balance has less than $10 in credit (-10 balance), add
        # $25 in credit (-25)
        if self.balance > -10:
            self.balance -= 25

        # add balance as a fixed cost to the bill
        self.bill.add_fixed_cost(self.balance)

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

       Precondition:
       - a bill has already been created for the month+year when the <call>
       was made. In other words, you can safely assume that self.bill has been
       already advanced to the right month+year.
       """
        # add billed minutes to call
        call_length = ceil(call.duration / 60.0)
        self.bill.add_billed_minutes(call_length)

        # increase balance based on cost of call
        call_cost = call_length * PREPAID_MINS_COST
        self.balance += call_cost

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancellation is requested.
        """
        # return the balance owed by customer
        if self.balance <= 0.0:
            return 0.0
        else:
            return self.balance


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'datetime', 'bill', 'call', 'math'
        ],
        'disable': ['R0902', 'R0913'],
        'generated-members': 'pygame.*'
    })
