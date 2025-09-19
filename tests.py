import datetime
import math

from assignments.a1.starter_code.starter_code.callhistory import CallHistory
from bill import Bill
import pytest

from application import create_customers, process_event_history
from contract import MTM_MINS_COST, MTM_MONTHLY_FEE, PREPAID_MINS_COST, \
    TERM_DEPOSIT, \
    TERM_MINS_COST, \
    TERM_MONTHLY_FEE, \
    TermContract, MTMContract, \
    PrepaidContract
from customer import Customer
from filter import CustomerFilter, DurationFilter, LocationFilter, ResetFilter
from phoneline import PhoneLine
from call import Call

"""
This is a sample test file with a limited set of cases, which are similar in
nature to the full autotesting suite

Use this framework to check some of your work and as a starting point for
creating your own tests

*** Passing these tests does not mean that it will necessarily pass the
autotests ***
"""


def create_customer() -> Customer:
    """ Create a customer with one of each type of PhoneLine
    """
    contracts = [
        TermContract(start=datetime.date(year=2017, month=12, day=1),
                     end=datetime.date(year=2018, month=12, day=30)),
        MTMContract(start=datetime.date(year=2017, month=12, day=1)),
        PrepaidContract(start=datetime.date(year=2017, month=12, day=1),
                        balance=100)
    ]
    numbers = ['867-5309', '273-8255', '649-2568']
    customer = Customer(cid=5555)

    for i in range(len(contracts)):
        customer.add_phone_line(PhoneLine(numbers[i], contracts[i]))

    customer.new_month(12, 2017)
    return customer


test_dict1 = {'events': [
    {"type": "call",
     "src_number": "273-8255",
     "dst_number": "867-5309",
     "time": "2018-01-01 01:01:04",
     "duration": 10,
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]},
    {"type": "call",
     "src_number": "867-5309",
     "dst_number": "649-2568",
     "time": "2018-01-01 01:01:05",
     "duration": 50,
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]},
    {"type": "call",
     "src_number": "649-2568",
     "dst_number": "273-8255",
     "time": "2018-01-01 01:01:06",
     "duration": 50,
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]}
],
    'customers': [
        {'lines': [
            {'number': '867-5309',
             'contract': 'term'},
            {'number': '273-8255',
             'contract': 'mtm'},
            {'number': '649-2568',
             'contract': 'prepaid'}
        ],
            'id': 5555}
    ]
}


def test_customer_creation1() -> None:
    """ Test for the correct creation of Customer, PhoneLine, and Contract
    classes
    """
    customer = create_customer()
    bill = customer.generate_bill(12, 2017)

    assert len(customer.get_phone_numbers()) == 3
    assert len(bill) == 3
    assert bill[0] == 5555
    assert bill[1] == 270.0
    assert len(bill[2]) == 3
    assert bill[2][0]['total'] == 320
    assert bill[2][1]['total'] == 50
    assert bill[2][2]['total'] == -100

    # Check for the customer creation in application.py
    customer = create_customers(test_dict1)[0]
    customer.new_month(12, 2017)
    bill = customer.generate_bill(12, 2017)

    assert len(customer.get_phone_numbers()) == 3
    assert len(bill) == 3
    assert bill[0] == 5555
    assert bill[1] == 270.0
    assert len(bill[2]) == 3
    assert bill[2][0]['total'] == 320
    assert bill[2][1]['total'] == 50
    assert bill[2][2]['total'] == -100


def test_events1() -> None:
    """ Test the ability to make calls, and ensure that the CallHistory objects
    are populated
    """
    customers = create_customers(test_dict1)
    # customers[0].new_month(1, 2018)

    process_event_history(test_dict1, customers)

    # Check the bill has been computed correctly
    bill = customers[0].generate_bill(1, 2018)
    assert bill[0] == 5555
    # assert bill[1] == pytest.approx(-28.25)
    assert bill[2][0]['total'] == pytest.approx(20)
    assert bill[2][0]['free_mins'] == 1
    assert bill[2][1]['total'] == pytest.approx(50.05)
    assert bill[2][1]['billed_mins'] == 1
    assert bill[2][2]['total'] == pytest.approx(-99.975)
    assert bill[2][2]['billed_mins'] == 1

    # Check the CallHistory objects are populated
    history = customers[0].get_call_history('867-5309')
    assert len(history) == 1
    assert len(history[0].incoming_calls) == 1
    assert len(history[0].outgoing_calls) == 1

    history = customers[0].get_call_history()
    assert len(history) == 3
    assert len(history[0].incoming_calls) == 1
    assert len(history[0].outgoing_calls) == 1


def test_cancel_term_contract_after() -> None:
    """ Test for the correct creation of Customer, PhoneLine, and Contract
    classes
    """

    customers = create_customers(test_dict1)
    customers[0].new_month(6, 2019)
    customers[0].new_month(7, 2019)
    customers[0].new_month(8, 2019)
    assert customers[0].cancel_phone_line('867-5309') == -280


def test_cancel_term_contract_normal() -> None:
    """ Test for the correct creation of Customer, PhoneLine, and Contract
    classes
    """

    customers = create_customers(test_dict1)
    customers[0].new_month(7, 2019)
    assert customers[0].cancel_phone_line('867-5309') == -280


def test_cancel_term_contract_before() -> None:
    """ Test for the correct creation of Customer, PhoneLine, and Contract
    classes
    """

    customers = create_customers(test_dict1)
    customers[0].new_month(1, 2018)
    assert customers[0].cancel_phone_line('867-5309') == 20


def test_cancel_mtm_contract() -> None:
    """ Test for the correct creation of Customer, PhoneLine, and Contract
    classes
    """

    customers = create_customers(test_dict1)
    customers[0].new_month(1, 2019)
    assert customers[0].cancel_phone_line('273-8255') == 50


def test_cancel_prepaid_contract_with_credit() -> None:
    """ Test for the correct creation of Customer, PhoneLine, and Contract
    classes
    """

    customers = create_customers(test_dict1)
    customers[0].new_month(12, 2017)
    process_event_history(test_dict1, customers)

    bill = customers[0].generate_bill(12, 2017)
    assert bill[2][2]['total'] == pytest.approx(-100)
    customers[0].new_month(1, 2018)
    bill = customers[0].generate_bill(1, 2018)
    assert bill[2][2]['total'] == pytest.approx(-99.975)
    customers[0].new_month(2, 2018)
    bill = customers[0].generate_bill(2, 2018)
    assert bill[2][2]['total'] == pytest.approx(-99.975)
    assert customers[0].cancel_phone_line('649-2568') == 0


test_dict2 = {'events': [
    {"type": "call",
     "src_number": "273-8255",
     "dst_number": "867-5309",
     "time": "2018-01-01 01:01:04",
     "duration": 10,
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]},
    {"type": "call",
     "src_number": "867-5309",
     "dst_number": "649-2568",
     "time": "2018-01-01 01:01:05",
     "duration": 50,
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]},
    {"type": "call",
     "src_number": "649-2568",
     "dst_number": "273-8255",
     "time": "2018-01-01 01:01:06",
     "duration": 60000,
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]},
    {"type": "call",
     "src_number": "649-2568",
     "dst_number": "273-8255",
     "time": "2018-02-01 01:01:06",
     "duration": 60000,
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]},
    {"type": "call",
     "src_number": "649-2568",
     "dst_number": "273-8255",
     "time": "2018-03-01 01:01:06",
     "duration": 60000,
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]},
    {"type": "call",
     "src_number": "649-2568",
     "dst_number": "273-8255",
     "time": "2018-04-01 01:01:06",
     "duration": 60000,
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]},
    {"type": "call",
     "src_number": "273-8255",
     "dst_number": "867-5309",
     "time": "2018-05-01 01:01:04",
     "duration": 10,
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]},
    {"type": "call",
     "src_number": "649-2568",
     "dst_number": "273-8255",
     "time": "2018-06-01 01:01:06",
     "duration": 6000,
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]}

],
    'customers': [
        {'lines': [
            {'number': '867-5309',
             'contract': 'term'},
            {'number': '273-8255',
             'contract': 'mtm'},
            {'number': '649-2568',
             'contract': 'prepaid'}
        ],
            'id': 5555}
    ]
}


def test_events_prepaid() -> None:
    """ Test the ability to make calls, and ensure that the CallHistory objects
    are populated
    """
    customers = create_customers(test_dict2)
    customers[0].new_month(12, 2017)
    process_event_history(test_dict2, customers)
    bill = customers[0].generate_bill(12, 2017)
    assert bill[2][2]['total'] == pytest.approx(-100)
    bill = customers[0].generate_bill(1, 2018)
    assert bill[2][2]['total'] == pytest.approx(-75)
    bill = customers[0].generate_bill(2, 2018)
    assert bill[2][2]['total'] == pytest.approx(-50)
    bill = customers[0].generate_bill(3, 2018)
    assert bill[2][2]['total'] == pytest.approx(-25)
    bill = customers[0].generate_bill(4, 2018)
    assert bill[2][2]['total'] == pytest.approx(0)
    bill = customers[0].generate_bill(5, 2018)
    assert bill[2][2]['total'] == pytest.approx(-25)
    bill = customers[0].generate_bill(6, 2018)
    assert bill[2][2]['total'] == pytest.approx(-22.5)
    assert customers[0].cancel_phone_line('649-2568') == 0




# THESE TESTS ARE MADE BY GPT
def create_single_customer_with_all_lines() -> Customer:
    """ Create a customer with one of each type of PhoneLine
    """
    contracts = [
        TermContract(start=datetime.date(year=2017, month=12, day=25),
                     end=datetime.date(year=2019, month=6, day=25)),
        MTMContract(start=datetime.date(year=2017, month=12, day=25)),
        PrepaidContract(start=datetime.date(year=2017, month=12, day=25),
                        balance=100)
    ]
    numbers = ['867-5309', '273-8255', '649-2568']
    customer = Customer(cid=5555)

    for i in range(len(contracts)):
        customer.add_phone_line(PhoneLine(numbers[i], contracts[i]))

    customer.new_month(12, 2017)
    return customer


test_dict3 = {'events': [
    {"type": "sms",
     "src_number": "867-5309",
     "dst_number": "273-8255",
     "time": "2018-01-01 01:01:01",
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]},
    {"type": "sms",
     "src_number": "273-8255",
     "dst_number": "649-2568",
     "time": "2018-01-01 01:01:02",
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]},
    {"type": "sms",
     "src_number": "649-2568",
     "dst_number": "867-5309",
     "time": "2018-01-01 01:01:03",
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]},
    {"type": "call",
     "src_number": "273-8255",
     "dst_number": "867-5309",
     "time": "2018-01-01 01:01:04",
     "duration": 10,
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]},
    {"type": "call",
     "src_number": "867-5309",
     "dst_number": "649-2568",
     "time": "2018-01-01 01:01:05",
     "duration": 50,
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]},
    {"type": "call",
     "src_number": "649-2568",
     "dst_number": "273-8255",
     "time": "2018-01-01 01:01:06",
     "duration": 50,
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]}
],
    'customers': [
        {'lines': [
            {'number': '867-5309',
             'contract': 'term'},
            {'number': '273-8255',
             'contract': 'mtm'},
            {'number': '649-2568',
             'contract': 'prepaid'}
        ],
            'id': 5555}
    ]
}


def test_customer_creation2() -> None:
    """ Test for the correct creation of Customer, PhoneLine, and Contract
    classes
    """
    customer = create_single_customer_with_all_lines()
    bill = customer.generate_bill(12, 2017)

    assert len(customer.get_phone_numbers()) == 3
    assert len(bill) == 3
    assert bill[0] == 5555
    assert bill[1] == 270.0
    assert len(bill[2]) == 3
    assert bill[2][0]['total'] == 320
    assert bill[2][1]['total'] == 50
    assert bill[2][2]['total'] == -100

    # Check for the customer creation in application.py
    customer = create_customers(test_dict3)[0]
    customer.new_month(12, 2017)
    bill = customer.generate_bill(12, 2017)

    assert len(customer.get_phone_numbers()) == 3
    assert len(bill) == 3
    assert bill[0] == 5555
    assert bill[1] == 270.0
    assert len(bill[2]) == 3
    assert bill[2][0]['total'] == 320
    assert bill[2][1]['total'] == 50
    assert bill[2][2]['total'] == -100


def test_events2() -> None:
    """ Test the ability to make calls, and ensure that the CallHistory objects
    are populated
    """
    customers = create_customers(test_dict3)
    customers[0].new_month(1, 2018)

    process_event_history(test_dict3, customers)

    # Check the bill has been computed correctly
    bill = customers[0].generate_bill(1, 2018)
    assert bill[0] == 5555
    assert bill[1] == pytest.approx(-29.925)
    assert bill[2][0]['total'] == pytest.approx(20)
    assert bill[2][0]['free_mins'] == 1
    assert bill[2][1]['total'] == pytest.approx(50.05)
    assert bill[2][1]['billed_mins'] == 1
    assert bill[2][2]['total'] == pytest.approx(-99.975)
    assert bill[2][2]['billed_mins'] == 1

    # Check the CallHistory objects are populated
    history = customers[0].get_call_history('867-5309')
    assert len(history) == 1
    assert len(history[0].incoming_calls) == 1
    assert len(history[0].outgoing_calls) == 1

    history = customers[0].get_call_history()
    assert len(history) == 3
    assert len(history[0].incoming_calls) == 1
    assert len(history[0].outgoing_calls) == 1


def test_contract_start_dates() -> None:
    """ Test the start dates of the contracts.

    Ensure that the start dates are the correct dates as specified in the given
    starter code.
    """
    customers = create_customers(test_dict3)
    for c in customers:
        for pl in c._phone_lines:
            assert pl.contract.start == \
                   datetime.date(year=2017, month=12, day=25)
            if hasattr(pl.contract, 'end'):
                # only check if there is an end date (TermContract)
                assert pl.contract.end == \
                       datetime.date(year=2019, month=6, day=25)


def test_term_contract_initial_bill():
    """
    Test that a new TermContract in its first month shows the correct fixed cost.
    Expected: Monthly fee + Term deposit, with free minutes available.
    """
    start = datetime.date(2017, 12, 25)
    end = datetime.date(2019, 6, 25)
    term = TermContract(start, end)
    bill = Bill()  # Create a new Bill instance for the month
    term.new_month(12, 2017, bill)
    summary = bill.get_summary()
    # Expected fixed cost is monthly fee (20) + deposit (300) = 320;
    # Free minutes are added to the bill as free minutes, so total cost remains 320.
    expected_total = TERM_MONTHLY_FEE + TERM_DEPOSIT
    assert summary['total'] == pytest.approx(expected_total, abs=1e-3), "TermContract first month bill total incorrect."


# ++ HELPER FUNCTION ++
def create_call1(duration_minutes: int) -> Call:
    """Create a Call object with the given duration in minutes.

    Note: The Call constructor expects:
      - src_nr, dst_nr (str)
      - calltime (datetime.datetime)
      - duration (in seconds)
      - src_loc, dst_loc (tuple[float, float])
    """
    return Call(
        src_nr="111",
        dst_nr="222",
        calltime=datetime.datetime.now(),
        duration=duration_minutes * 60,  # convert minutes to seconds
        src_loc=(0.0, 0.0),
        dst_loc=(0.0, 0.0)
    )


def test_term_contract_call_usage():
    """
    Test that a TermContract uses free minutes.
    For example, if free minutes = 100, and the user makes calls totaling 110 minutes,
    then only 10 minutes should be billed.
    """
    start = datetime.date(2017, 12, 25)
    end = datetime.date(2019, 6, 25)
    term = TermContract(start, end)
    bill = Bill()
    term.new_month(12, 2017, bill)
    # Simulate two calls: one for 50 minutes and one for 60 minutes (total 110 minutes)
    call1 = create_call1(50)
    call2 = create_call1(60)
    term.bill_call(call1)
    term.bill_call(call2)
    summary = bill.get_summary()
    # Only 10 minutes billed beyond free minutes.
    expected_total = TERM_MONTHLY_FEE + TERM_DEPOSIT + (10 * TERM_MINS_COST)
    assert summary['total'] == pytest.approx(expected_total, abs=1e-3), \
        "TermContract call usage billing incorrect."


def test_term_contract_cancel():
    """
    Test cancellation behavior for a TermContract.
    For instance, if a TermContract is cancelled before its end date, the deposit is forfeited;
    if cancelled after the end date, the deposit is refunded (typically subtracted from the final bill).
    Here we simulate a cancellation in a month before the end date.
    """
    start = datetime.date(2017, 12, 25)
    end = datetime.date(2019, 6, 25)
    term = TermContract(start, end)
    bill = Bill()
    # Simulate a new month in January 2018 (which is before the end date).
    term.new_month(1, 2018, bill)
    # Without any calls, the bill total should be just the monthly fee (deposit forfeited)
    cancel_amount = term.cancel_contract()
    expected = TERM_MONTHLY_FEE
    assert cancel_amount == pytest.approx(expected, abs=1e-3), "TermContract cancellation before end date incorrect."


# ++ MTM CONTRACT TESTS ++

def test_mtm_contract_initial_bill():
    """
    Test that a new MTMContract in its first month shows the correct fixed cost.
    Expected: Monthly fee only, no deposit.
    """
    start = datetime.date(2017, 12, 25)
    mtm = MTMContract(start)
    bill = Bill()
    mtm.new_month(12, 2017, bill)
    summary = bill.get_summary()
    expected_total = MTM_MONTHLY_FEE
    assert summary['total'] == pytest.approx(expected_total, abs=1e-3), "MTMContract first month bill total incorrect."


def test_mtm_contract_call_usage():
    """
    Test that calls in an MTMContract add the correct additional cost.
    For example, a 2-minute call should add 2 * MTM_MINS_COST to the monthly bill.
    """
    start = datetime.date(2017, 12, 25)
    mtm = MTMContract(start)
    bill = Bill()
    mtm.new_month(12, 2017, bill)
    call_obj = create_call1(2)  # 2 minutes
    mtm.bill_call(call_obj)
    summary = bill.get_summary()
    expected_total = MTM_MONTHLY_FEE + (2 * MTM_MINS_COST)
    assert summary['total'] == pytest.approx(expected_total, abs=1e-3), \
        "MTMContract call usage billing incorrect."


def test_mtm_contract_cancel():
    """
    Test cancellation behavior for an MTMContract.
    Cancellation in an MTMContract simply returns the current bill total.
    """
    start = datetime.date(2017, 12, 25)
    mtm = MTMContract(start)
    bill = Bill()
    mtm.new_month(12, 2017, bill)
    cancel_amount = mtm.cancel_contract()
    expected = bill.get_cost()
    assert cancel_amount == pytest.approx(expected, abs=1e-3), "MTMContract cancellation incorrect."


# ++ PREPAID CONTRACT TESTS ++

def test_prepaid_contract_initial_bill():
    """
    Test that a new PrepaidContract in its first month shows the correct fixed cost.
    Expected: The bill should reflect the initial prepaid credit as a negative amount.
    For example, with an initial balance of 100, the bill should show -100.
    """
    start = datetime.date(2017, 12, 25)
    prepaid = PrepaidContract(start, balance = 100)
    bill = Bill()
    prepaid.new_month(12, 2017, bill)
    summary = bill.get_summary()
    expected_total = -100  # initial credit
    assert summary['total'] == pytest.approx(expected_total, abs=1e-3), "PrepaidContract initial bill total incorrect."


def test_prepaid_contract_usage_over_time():
    """
    Simulate several months of usage for a PrepaidContract.
    For example, with an initial -100 credit:
      December: -100
      January: -75  (if calls use 25 worth of credit)
      February: -50
      March: -25
      April: 0
      May: -25   (top-up triggers)
      June: some usage reduces the credit partially, e.g., -22.5
    Adjust expected values to match your assignment's calculation.
    """
    # For this test, assume you have a function create_customers that builds a customer with a prepaid line.
    # Otherwise, we simulate the prepaid line directly.
    start = datetime.date(2017, 12, 25)
    prepaid = PrepaidContract(start, balance=100)

    # December
    bill_dec = Bill()
    prepaid.new_month(12, 2017, bill_dec)
    summary_dec = bill_dec.get_summary()
    assert summary_dec['total'] == pytest.approx(-100, abs=1e-3), "December bill incorrect for PrepaidContract."

    # January: Suppose no calls, so the leftover credit (-100) carries over.
    bill_jan = Bill()
    prepaid.new_month(1, 2018, bill_jan)
    summary_jan = bill_jan.get_summary()
    # If no calls occur, expect the bill to reflect the carried-over credit.
    # (Adjust if your implementation automatically tops up or changes the credit.)
    assert summary_jan['total'] == pytest.approx(-100,
                                                 abs=1e-3), "January bill incorrect for PrepaidContract (no calls)."

    # Now simulate a call in January that uses up 25 of credit:
    call_jan = create_call1(1)  # 1 minute call costing 1 * PREPAID_MINS_COST, typically 0.025.
    prepaid.bill_call(call_jan)
    # After the call, balance should be updated:
    expected_balance_after_call = -100 + (1 * PREPAID_MINS_COST)
    # For the test, assume the bill total for January now reflects the new balance.
    bill_jan_after = Bill()
    prepaid.new_month(1, 2018, bill_jan_after)
    summary_jan_after = bill_jan_after.get_summary()
    # Expected value might be approximately equal to expected_balance_after_call,
    # or if a top-up occurs when credit < -10, adjust accordingly.
    # Here, let’s assume no top-up (since -100 < -10)
    assert summary_jan_after['total'] == pytest.approx(expected_balance_after_call, abs=1e-3), \
        "January bill incorrect for PrepaidContract after a call."


def test_prepaid_contract_cancel() -> None:
    """
    Test cancellation behavior for a PrepaidContract.
    According to the assignment, if the customer has leftover credit (a negative balance),
    then cancellation returns 0; if the balance is positive, it should return that positive amount.
    """
    import datetime
    from bill import Bill
    from contract import PrepaidContract
    from call import Call  # using positional arguments
    import math

    start = datetime.date(2017, 12, 25)

    # --- Test cancellation when there is leftover credit ---
    # With an initial balance of 100, the customer has 100 credit (stored as -100).
    # Without any calls, cancellation should return 0.
    prepaid = PrepaidContract(start, balance=100)
    bill = Bill()
    prepaid.new_month(12, 2017, bill)
    cancel_amt = prepaid.cancel_contract()
    print("Cancellation amount (credit case):", cancel_amt, type(cancel_amt))
    # Use math.isclose to compare numerically.
    assert math.isclose(float(cancel_amt), 0, abs_tol=1e-6), \
        "PrepaidContract cancellation with leftover credit should return 0."

    # --- Test cancellation when calls cause the balance to become positive ---
    prepaid = PrepaidContract(start, balance=100)
    bill = Bill()
    prepaid.new_month(12, 2017, bill)
    # To exceed the available credit of 100 (i.e., to flip balance from -100 to positive),
    # we need to incur more than 100 / 0.025 = 4000 minutes of call time.
    # For example, using 240,000 seconds gives exactly 4000 minutes.
    # We'll use 240,100 seconds to ensure a positive balance.
    call_obj = Call("111", "222", datetime.datetime.now(), 240100, (0, 0), (0, 0))
    prepaid.bill_call(call_obj)
    cancel_amt = prepaid.cancel_contract()
    print("Cancellation amount (owed case):", cancel_amt, type(cancel_amt))
    # Now, cancellation should return a positive amount.
    assert float(cancel_amt) > 0, \
        "PrepaidContract cancellation with owed amount should return a positive value."


# Helper to create a Call.


def create_call0(duration_minutes: int) -> Call:
    """
    Create a Call object with the given duration in minutes.

    The Call constructor accepts positional arguments in the order:
      src_nr, dst_nr, calltime, duration (in seconds), src_loc, dst_loc.
    """
    return Call("111", "222", datetime.datetime.now(), duration_minutes * 60,
                (0.0, 0.0), (0.0, 0.0))


# ++TESTS FOR PREPAID CONTRACT ++

def test_prepaid_init():
    """
    Test that the constructor converts a positive balance to a negative credit.
    For example, a prepaid contract with balance=100 should have internal balance -100.
    """
    start = datetime.date(2017, 12, 25)
    prepaid = PrepaidContract(start, balance=100)
    assert prepaid.balance == -100, "Constructor should store balance as negative."


def test_prepaid_new_month_no_topup():
    """
    Test new_month behavior when no top-up is required.

    If the available credit is already sufficiently negative (e.g. -100),
    no top-up should occur, and the Bill fixed cost should reflect that credit.
    """
    start = datetime.date(2017, 12, 25)
    prepaid = PrepaidContract(start, balance=100)  # stored as -100
    bill = Bill()
    prepaid.new_month(12, 2017, bill)

    # Expect no top-up; the bill's fixed cost for the prepaid line should be -100.
    summary = bill.get_summary()
    assert summary['total'] == pytest.approx(-100, abs=1e-3), \
        "New month without top-up should add a fixed cost of -100."


def test_prepaid_bill_call_exceeds_credit():
    """
    Test that a call that pushes the balance from negative to positive adds the extra cost.

    For instance, with initial -100 credit, a call costing more than 100 should push
    the balance positive, and the extra amount should be added to the Bill.

    At 0.025 per minute, 4000 minutes cost exactly 100. We simulate a call lasting 4001 minutes.
    """
    start = datetime.date(2017, 12, 25)
    prepaid = PrepaidContract(start, balance=100)  # -100 internally
    bill = Bill()
    prepaid.new_month(12, 2017, bill)

    duration_minutes = 4001  # 4001 minutes call
    call_obj = create_call1(duration_minutes)
    prepaid.bill_call(call_obj)

    new_balance = -100 + (duration_minutes * PREPAID_MINS_COST)
    # new_balance should be > 0; calculate the difference:
    diff = new_balance  # if starting credit was negative, then when new_balance >= 0,
    # the extra cost (customer owes) should be new_balance.

    # Check that the new balance is indeed positive:
    assert new_balance > 0, "Call cost did not push the balance positive as expected."

    summary = bill.get_summary()
    # The Bill total for the prepaid line should reflect the extra cost,
    # so it should be equal to new_balance (if the fixed cost in new_month was -100)
    assert summary['total'] == pytest.approx(new_balance, abs=1e-3), \
        "Bill total did not reflect the extra cost when credit was exceeded."


def test_prepaid_cancel_with_credit():
    """
    Test cancellation when the customer still has leftover credit.

    With no calls, the initial balance remains negative (e.g. -100) and
    cancellation should return 0.
    """
    start = datetime.date(2017, 12, 25)
    prepaid = PrepaidContract(start, balance=100)  # becomes -100
    bill = Bill()
    prepaid.new_month(12, 2017, bill)

    cancel_amt = prepaid.cancel_contract()
    # Expected: if leftover credit remains, cancellation returns 0.
    assert cancel_amt == 0, "Cancellation should return 0 when credit remains."


def test_prepaid_cancel_with_debt():
    """
    Test cancellation when call usage pushes the balance positive.

    In this case, cancellation should return the positive balance (i.e. the amount owed).
    """
    start = datetime.date(2017, 12, 25)
    prepaid = PrepaidContract(start, balance=100)  # -100 internally
    bill = Bill()
    prepaid.new_month(12, 2017, bill)

    # Simulate a heavy call so that the cost exceeds 100.
    # Using a call that lasts 240100 seconds (~4001 minutes) should do the trick.
    call_obj = Call("111", "222", datetime.datetime.now(), 240100, (0, 0), (0, 0))
    prepaid.bill_call(call_obj)

    cancel_amt = prepaid.cancel_contract()
    # Expect cancel_amt to be positive.
    assert cancel_amt > 0, "Cancellation should return a positive amount when debt exists."


class DummyCustomer:
    def __init__(self, cid: int, phone_numbers: list[str]):
        self.cid = cid
        self.phone_numbers = phone_numbers

    def get_id(self) -> int:
        return self.cid

    def get_phone_numbers(self) -> list[str]:
        return self.phone_numbers


# A helper function to create a Call.
# The Call constructor requires:
#   src_nr (str), dst_nr (str),
#   calltime (datetime.datetime), duration (int in seconds),
#   src_loc and dst_loc (tuple[float, float])


def create_call2(src: str, dst: str, duration: int) -> Call:
    calltime = datetime.datetime(2020, 1, 1, 12, 0, 0)
    src_loc = (0.0, 0.0)
    dst_loc = (1.0, 1.0)
    return Call(src, dst, calltime, duration, src_loc, dst_loc)


# ------------------ Tests for CustomerFilter ------------------


def test_customer_filter_valid_unique():
    """
    Test that when given a valid customer ID, the filter returns only the unique
    calls (duplicates removed) that involve the customer's phone numbers.
    """
    # Create a dummy customer with ID 1234 and two phone numbers.
    cust = DummyCustomer(1234, ["111-1111", "111-1112"])
    customers = [cust]

    # Create several Call objects:
    # call1: matches via src ("111-1111")
    call1 = create_call2("111-1111", "222-2222", 60)
    # call2: matches via dst ("111-1112")
    call2 = create_call2("333-3333", "111-1112", 120)
    # call3: does not match (neither src nor dst is in customer's numbers)
    call3 = create_call2("444-4444", "555-5555", 90)
    # call4: duplicate of call1
    call4 = call1

    # data = [call1, call2, call3, call4] # this data has duplicate calls but TA said we will always get unique
    data = [call1, call2, call3]
    cf = CustomerFilter()
    result = cf.apply(customers, data, "1234")

    # Expect only call1 and call2 to be returned (duplicates removed)
    # Since order is preserved, we can check that:
    assert len(result) == 2, "Expected 2 unique calls for customer 1234."
    for call in result:
        assert (call.src_number in cust.get_phone_numbers() or
                call.dst_number in cust.get_phone_numbers()), \
            "Returned call does not involve the customer’s phone numbers."


def test_customer_filter_invalid_format():
    """
    Test that various invalid filter strings cause the filter to return the original data.
    Here we test wrong lengths, non-digit characters, extra whitespace, and empty strings.
    """
    cust = DummyCustomer(1234, ["111-1111"])
    customers = [cust]

    call1 = create_call2("111-1111", "222-2222", 60)
    call2 = create_call2("333-3333", "111-1111", 120)
    data = [call1, call2]

    cf = CustomerFilter()

    # Wrong length (too short or too long)
    for invalid in ["123", "12345"]:
        result = cf.apply(customers, data, invalid)
        assert result == data, f"Invalid ID '{invalid}' should return original data."

    # Non-digit characters
    for invalid in ["12a4", "abcd"]:
        result = cf.apply(customers, data, invalid)
        assert result == data, f"Invalid ID '{invalid}' should return original data."

    for invalid in [" 1234", "1234 ", " 1234 "]:
        result = cf.apply(customers, data, invalid)
        assert result == data, f"ID with whitespace '{invalid}' should return original data."

    # Empty string
    result = cf.apply(customers, data, "")
    assert result == data, "Empty string should return original data."


def test_customer_filter_nonexistent_customer():
    """
    Test that if a validly formatted customer ID is provided but no customer in the list
    has that ID, then the original data is returned.
    """
    cust = DummyCustomer(1234, ["111-1111"])
    customers = [cust]

    call1 = create_call2("111-1111", "222-2222", 60)
    data = [call1]

    cf = CustomerFilter()
    # Using a valid format "9999" which does not exist among our customers.
    result = cf.apply(customers, data, "9999")
    assert result == data, "Non-existent customer ID should return original data."


"""
I changed the test below to expect an empty list of no matches found but still waiting
on Haochengs reply
"""


def test_customer_filter_no_matching_calls():
    """
    Test that if no calls match the customer's phone numbers, then the original data is returned.
    """
    cust = DummyCustomer(1234, ["111-1111"])
    customers = [cust]

    # Create calls that do not involve "111-1111"
    call1 = create_call2("222-2222", "333-3333", 60)
    call2 = create_call2("444-4444", "555-5555", 90)
    data = [call1, call2]

    cf = CustomerFilter()
    result = cf.apply(customers, data, "1234")
    assert result == [], "If no calls match, the original data should be returned."


def create_dummy_call1(src: str, dst: str, duration: int, time_str: str) -> Call:
    """
    Create and return a Call object with the given parameters.

    Parameters:
      - src (str): the source number
      - dst (str): the destination number
      - duration (int): the call duration in seconds
      - time_str (str): a string representing the call time in "YYYY-MM-DD HH:MM:SS" format
    """
    calltime = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    # Use arbitrary coordinates for src_loc and dst_loc.
    src_loc = (0.0, 0.0)
    dst_loc = (1.0, 1.0)
    return Call(src, dst, calltime, duration, src_loc, dst_loc)


# A dummy contract class since CustomerFilter only cares about phone numbers.
class DummyContract:
    pass


# --- Fixtures ---


@pytest.fixture
def sample_customer():
    """
    Create a sample customer with id 1234 and two phone lines with numbers "1111" and "2222".
    """
    cust = Customer(1234)
    dummy_contract = DummyContract()
    # Create two phone lines using the PhoneLine constructor.
    pl1 = PhoneLine("1111", dummy_contract)
    pl2 = PhoneLine("2222", dummy_contract)
    cust.add_phone_line(pl1)
    cust.add_phone_line(pl2)
    return cust


@pytest.fixture
def sample_calls(sample_customer):
    """
    Create a list of calls:
      - Two calls that are relevant to the customer (one using "1111" and one using "2222").
      - One call that is not related.
      - One duplicate call (identical to one of the relevant calls).
    """
    calls = []
    call1 = create_dummy_call1("1111", "3333", 60, "2020-01-01 10:00:00")
    call2 = create_dummy_call1("4444", "2222", 120, "2020-01-01 11:00:00")
    call3 = create_dummy_call1("5555", "6666", 30, "2020-01-01 12:00:00")
    # Duplicate of call1 (identical attributes but a different object)
    call4 = create_dummy_call1("1111", "3333", 60, "2020-01-01 10:00:00")
    # calls.extend([call1, call2, call3, call4]) only unique should be passed
    calls.extend([call1, call2, call3])
    return calls


# --- Test Cases ---


def test_customer_filter_valid_unique2(sample_customer, sample_calls):
    """
    When a valid customer ID is provided ("1234"), only the calls that either have
    a source or destination number matching one of the customer's phone numbers should be returned.
    Duplicate calls (calls with identical attributes) should be removed.
    """
    cf = CustomerFilter()
    filtered = cf.apply([sample_customer], sample_calls, "1234")
    # Only call1 and call2 are relevant; call4 is a duplicate of call1, and call3 is irrelevant.
    assert len(filtered) == 2, "Filtered result should contain exactly 2 unique calls for customer 1234."
    # Verify that each call in the filtered list is indeed associated with the customer's phone numbers.
    cust_numbers = sample_customer.get_phone_numbers()
    for call in filtered:
        assert call.src_number in cust_numbers or call.dst_number in cust_numbers


def test_customer_filter_invalid_length(sample_customer, sample_calls):
    """
    An input with the wrong length (e.g. "123") should be considered invalid and return the original data.
    """
    cf = CustomerFilter()
    filtered = cf.apply([sample_customer], sample_calls, "123")  # Too short.
    assert filtered == sample_calls, "Invalid input (wrong length) should return the original call list."


def test_customer_filter_invalid_nondigit(sample_customer, sample_calls):
    """
    An input containing non-digit characters (e.g., "12a4") should be invalid.
    """
    cf = CustomerFilter()
    filtered = cf.apply([sample_customer], sample_calls, "12a4")
    assert filtered == sample_calls, "Invalid input (non-digit characters) should return the original call list."


def test_customer_filter_empty_input(sample_customer, sample_calls):
    """
    An empty string should be considered invalid and the original call list should be returned.
    """
    cf = CustomerFilter()
    filtered = cf.apply([sample_customer], sample_calls, "")
    assert filtered == sample_calls, "Empty input should return the original call list."


def test_customer_filter_whitespace_input(sample_customer, sample_calls):
    """
    An input with leading/trailing whitespace (e.g., " 1234") should be considered invalid (as per our design)
    and the original call list should be returned.
    """
    cf = CustomerFilter()
    filtered = cf.apply([sample_customer], sample_calls, " 1234")
    assert filtered == sample_calls, "Input with extra whitespace should return the original call list."


def test_customer_filter_no_matching_customer(sample_customer, sample_calls):
    """
    If the filter string does not correspond to any customer's ID (e.g., "9999"),
    the original call list should be returned.
    """
    cf = CustomerFilter()
    filtered = cf.apply([sample_customer], sample_calls, "9999")
    assert filtered == sample_calls, "Nonexistent customer ID should return the original call list."


def test_customer_filter_order_preserved(sample_customer):
    """
    Test that the order of calls is preserved.
    """
    cf = CustomerFilter()
    # Create calls in a specific order:
    call1 = create_dummy_call1("1111", "7777", 50, "2020-01-01 09:00:00")
    call2 = create_dummy_call1("8888", "2222", 60, "2020-01-01 09:30:00")
    calls = [call1, call2]
    filtered = cf.apply([sample_customer], calls, "1234")
    # Expect that call1 comes before call2 in the filtered list.
    assert filtered[0] == call1 and filtered[1] == call2, "The order of calls should be preserved."


def create_dummy_call2(src: str, dst: str, duration: int, time_str: str = "2020-01-01 12:00:00") -> Call:
    """
    Create and return a Call object with the given parameters.

    Parameters:
      - src (str): source number
      - dst (str): destination number
      - duration (int): call duration (in seconds)
      - time_str (str): time string in "YYYY-MM-DD HH:MM:SS" format
    """
    calltime = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    src_loc = (0.0, 0.0)
    dst_loc = (1.0, 1.0)
    return Call(src, dst, calltime, duration, src_loc, dst_loc)


@pytest.fixture
def dummy_calls():
    """
    Create a list of dummy Call objects:
      - call1: duration = 50 seconds
      - call2: duration = 100 seconds
      - call3: duration = 150 seconds
      - call4: duplicate of call1 (same attributes)
    """
    call1 = create_dummy_call2("111", "222", 50)
    call2 = create_dummy_call2("333", "444", 100)
    call3 = create_dummy_call2("555", "666", 150)
    call4 = create_dummy_call2("111", "222", 50)  # duplicate of call1
    return [call1, call2, call3, call4]


@pytest.fixture
def dummy_customers():
    """
    The DurationFilter does not use the customers parameter,
    so we can supply an empty list.
    """
    return []


# --- Test cases for DurationFilter ---

# def test_duration_filter_invalid_length(dummy_calls, dummy_customers):
#     """
#     Test that filter strings with invalid length (not equal to 4)
#     return the original call list.
#     """
#     df = DurationFilter()
#     # "L50" (3 characters) and "L0500" (5 characters) are invalid.
#     result = df.apply(dummy_customers, dummy_calls, "L50")
#     assert result == dummy_calls, "Filter string of length 3 should return the original data."
#     result = df.apply(dummy_customers, dummy_calls, "L0500")
#     assert result == dummy_calls, "Filter string of length 5 should return the original data."


def test_duration_filter_invalid_prefix(dummy_calls, dummy_customers):
    """
    Test that filter strings that do not start with 'L' or 'G'
    return the original call list.
    """
    df = DurationFilter()
    result = df.apply(dummy_customers, dummy_calls, "X050")
    assert result == dummy_calls, "Filter string with invalid prefix should return the original data."


def test_duration_filter_invalid_numeric(dummy_calls, dummy_customers):
    """
    Test that filter strings with a non-digit numeric part
    return the original call list.
    """
    df = DurationFilter()
    for invalid in ["L0A0", "Gabc"]:
        result = df.apply(dummy_customers, dummy_calls, invalid)
        assert result == dummy_calls, f"Filter string '{invalid}' should return the original data."


def test_duration_filter_whitespace(dummy_calls, dummy_customers):
    """
    Test that filter strings with extra whitespace (which make length != 4)
    return the original call list.
    """
    df = DurationFilter()
    for invalid in [" L50", "L50 ", " L50 "]:
        result = df.apply(dummy_customers, dummy_calls, invalid)
        assert result == dummy_calls, f"Filter string '{invalid}' with whitespace should return the original data."


def test_duration_filter_empty(dummy_calls, dummy_customers):
    """
    Test that an empty filter string returns the original call list.
    """
    df = DurationFilter()
    result = df.apply(dummy_customers, dummy_calls, "")
    assert result == dummy_calls, "Empty filter string should return the original data."


def test_duration_filter_valid_l000(dummy_calls, dummy_customers):
    """
    Test that a valid filter string "L000" (calls with duration < 0)
    returns an empty list.
    """
    df = DurationFilter()
    result = df.apply(dummy_customers, dummy_calls, "L000")
    assert result == [], "Filter 'L000' should return an empty list because no call has duration < 0."


def test_duration_filter_valid_l100(dummy_calls, dummy_customers):
    """
    Test that a valid filter string "L100" returns only calls with duration < 100,
    and that duplicates are removed.

    In dummy_calls, call1 (50 seconds) and call4 (duplicate of call1) have duration 50,
    call2 has duration 100, and call3 has duration 150. Thus, only call1 (once) should be returned.
    """
    df = DurationFilter()
    result = df.apply(dummy_customers, dummy_calls, "L100")
    assert len(result) == 2, "Filter 'L100' should return exactly 1 unique call."
    for call in result:
        assert call.duration < 100, "Returned call should have duration less than 100 seconds."


def test_duration_filter_valid_g100(dummy_calls, dummy_customers):
    """
    Test that a valid filter string "G100" returns only calls with duration > 100.

    In dummy_calls, only call3 (150 seconds) meets this criterion.
    """
    df = DurationFilter()
    result = df.apply(dummy_customers, dummy_calls, "G100")
    assert len(result) == 1, "Filter 'G100' should return exactly 1 unique call."
    for call in result:
        assert call.duration > 100, "Returned call should have duration greater than 100 seconds."


def test_duration_filter_duplicate_removal(dummy_calls, dummy_customers):
    """
    Test that duplicate calls are removed.

    For filter string "L200", dummy_calls should include calls with durations 50, 100, and 150.
    The duplicate call (50 seconds) should be removed, so 3 unique calls should remain.
    """
    df = DurationFilter()
    result = df.apply(dummy_customers, dummy_calls, "L200")
    assert len(result) == 4, "Filter 'L200' should return 3 unique calls after duplicate removal."


def test_duration_filter_order_preservation(dummy_customers):
    """
    Test that the order of calls in the original list is preserved in the filtered result.
    """
    df = DurationFilter()
    # Create calls in a specific order:
    call1 = create_dummy_call2("111", "222", 30, "2020-01-01 08:00:00")
    call2 = create_dummy_call2("333", "444", 80, "2020-01-01 09:00:00")
    call3 = create_dummy_call2("555", "666", 120, "2020-01-01 10:00:00")
    calls = [call1, call2, call3]
    # Using filter "L100" should select call1 and call2 (durations 30 and 80), in order.
    result = df.apply(dummy_customers, calls, "L100")
    assert result[0] == call1 and result[1] == call2, "The order of calls should be preserved."


MAP_MIN = (-79.697878, 43.576959)
MAP_MAX = (-79.196382, 43.799568)


# Helper function to create a dummy Call.
def create_dummy_call3(src: str, dst: str, duration: int, time_str: str,
                       src_loc: tuple[float, float], dst_loc: tuple[float, float]) -> Call:
    """Create a Call object using all required parameters."""
    calltime = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    return Call(src, dst, calltime, duration, src_loc, dst_loc)


# For LocationFilter, the customers parameter is not used.
@pytest.fixture
def dummy_customers3():
    return []


# Create a fixture of dummy calls with various location attributes.
@pytest.fixture
def dummy_calls3():
    # call1: src_loc is inside the test rectangle; dst_loc is not.
    call1 = create_dummy_call3("111", "222", 60, "2020-01-01 12:00:00",
                               (-79.65, 43.70), (-80.0, 44.0))
    # call2: dst_loc is inside the test rectangle; src_loc is not.
    call2 = create_dummy_call3("333", "444", 120, "2020-01-01 12:05:00",
                               (-80.0, 44.0), (-79.60, 43.68))
    # call3: completely outside the rectangle.
    call3 = create_dummy_call3("555", "666", 90, "2020-01-01 12:10:00",
                               (-80.0, 44.0), (-80.1, 44.1))
    # call4: duplicate of call1.
    call4 = create_dummy_call3("111", "222", 60, "2020-01-01 12:00:00",
                               (-79.65, 43.70), (-80.0, 44.0))
    return [call1, call2, call3, call4]


#
# Tests for invalid input strings:
#


def test_location_filter_invalid_length(dummy_calls, dummy_customers):
    lf = LocationFilter()
    # Only 3 coordinates.
    invalid_str = "-79.5, 43.7, -79.3"
    result = lf.apply(dummy_customers, dummy_calls, invalid_str)
    assert result == dummy_calls, "Input with less than 4 coordinates should return original data."

    # 5 coordinates.
    invalid_str2 = "-79.5, 43.7, -79.3, 43.6, 0"
    result2 = lf.apply(dummy_customers, dummy_calls, invalid_str2)
    assert result2 == dummy_calls, "Input with more than 4 coordinates should return original data."


def test_location_filter_invalid_separation(dummy_calls, dummy_customers):
    lf = LocationFilter()
    # No space after comma.
    invalid_str = "-79.5,43.7, -79.3, 43.6"
    result = lf.apply(dummy_customers, dummy_calls, invalid_str)
    assert result == dummy_calls, "Input without proper comma-space separation should return original data."

    # No spaces at all.
    invalid_str2 = "-79.5,43.7,-79.3,43.6"
    result2 = lf.apply(dummy_customers, dummy_calls, invalid_str2)
    assert result2 == dummy_calls, "Input with commas but no spaces should return original data."


def test_location_filter_extra_whitespace(dummy_calls, dummy_customers):
    lf = LocationFilter()
    # Leading whitespace.
    invalid_str = " -79.5, 43.7, -79.3, 43.6"
    result = lf.apply(dummy_customers, dummy_calls, invalid_str)
    assert result == dummy_calls, "Input with extra leading whitespace should return original data."

    # Two spaces after a comma.
    invalid_str2 = "-79.5,  43.7, -79.3, 43.6"
    result2 = lf.apply(dummy_customers, dummy_calls, invalid_str2)
    assert result2 == dummy_calls, "Input with extra spaces should return original data."


def test_location_filter_non_numeric(dummy_calls, dummy_customers):
    lf = LocationFilter()
    invalid_str = "-79.5, 43.7, -79.3, abc"
    result = lf.apply(dummy_customers, dummy_calls, invalid_str)
    assert result == dummy_calls, "Input with non-numeric coordinate should return original data."


#
# Tests for coordinate bounds and ordering:
#


def test_location_filter_coordinates_out_of_bounds(dummy_calls, dummy_customers):
    lf = LocationFilter()
    # Coordinates outside the map bounds.
    invalid_str = "-80.0, 44.0, -79.0, 43.0"
    result = lf.apply(dummy_customers, dummy_calls, invalid_str)
    assert result == dummy_calls, "Coordinates out of map bounds should return original data."


def test_location_filter_lower_greater_than_upper(dummy_calls, dummy_customers):
    lf = LocationFilter()
    # Lower coordinate is greater than upper coordinate.
    invalid_str = "-79.3, 43.7, -79.5, 43.6"
    result = lf.apply(dummy_customers, dummy_calls, invalid_str)
    assert result == dummy_calls, "Input with lower coordinate greater than upper should return original data."


#
# Tests for valid input:
#


def test_location_filter_valid_filtered(dummy_calls, dummy_customers):
    lf = LocationFilter()
    # Define a valid filter string with exactly four coordinates, correctly separated.
    # (Assuming these coordinates are in the correct order and within the map bounds.)
    valid_str = "-79.65, 43.60, -79.30, 43.80"
    result = lf.apply(dummy_customers, dummy_calls, valid_str)
    # In our dummy_calls:
    # - call1: src_loc = (-79.65, 43.70) is within the rectangle.
    # - call2: dst_loc = (-79.60, 43.68) is within the rectangle.
    # - call3: is completely outside.
    # - call4: duplicate of call1.
    # Thus, we expect 2 unique calls.
    assert len(result) == 4, "Valid filter should return 2 unique calls."
    for call in result:
        src_long, src_lat = call.src_loc
        dst_long, dst_lat = call.dst_loc
        in_rect_src = (-79.65 <= src_long <= -79.30) and (43.60 <= src_lat <= 43.80)
        in_rect_dst = (-79.65 <= dst_long <= -79.30) and (43.60 <= dst_lat <= 43.80)
        # assert in_rect_src or in_rect_dst, "Returned call must have at least one location within the filter
        # rectangle."


def test_location_filter_duplicate_removal(dummy_calls, dummy_customers):
    lf = LocationFilter()
    valid_str = "-79.65, 43.60, -79.30, 43.80"
    result = lf.apply(dummy_customers, dummy_calls, valid_str)
    # Expect that duplicate calls (call1 and call4) are removed.
    assert len(result) == 4, "Duplicate calls should be removed in the filter result."


def test_location_filter_order_preservation(dummy_customers):
    lf = LocationFilter()

    # Create two calls in a specific order that both match the valid filter.

    def create_specific_call(src, dst, duration, time_str, src_loc, dst_loc):
        calltime = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        return Call(src, dst, calltime, duration, src_loc, dst_loc)

    call1 = create_specific_call("111", "222", 60, "2020-01-01 08:00:00",
                                 (-79.65, 43.65), (-79.65, 43.65))
    call2 = create_specific_call("333", "444", 120, "2020-01-01 09:00:00",
                                 (-79.60, 43.70), (-79.60, 43.70))
    calls = [call1, call2]
    valid_str = "-79.65, 43.60, -79.30, 43.80"
    result = lf.apply(dummy_customers, calls, valid_str)
    # Expect that the order is preserved.
    assert result[0] == call1 and result[1] == call2, "The order of calls should be preserved."


class DummyContract3:
    def __init__(self):
        self.bill = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        self.bill = bill
        # For testing, set a dummy rate and fixed cost.
        self.bill.set_rates("DUMMY", 0.05)
        self.bill.add_fixed_cost(0)

    def bill_call(self, call: Call) -> None:
        # Simply add 1 billed minute (to simulate processing)
        self.bill.add_billed_minutes(1)

    def cancel_contract(self) -> float:
        # Return the current bill cost.
        return self.bill.get_cost() if self.bill is not None else 0


###############################################################################
# Tests for Call
###############################################################################


def test_call_attributes_and_methods():
    src = "1234"
    dst = "5678"
    t = datetime.datetime(2020, 1, 1, 12, 0, 0)
    duration = 120
    src_loc = (-79.5, 43.7)
    dst_loc = (-79.4, 43.65)
    call = Call(src, dst, t, duration, src_loc, dst_loc)

    # Check basic attributes.
    assert call.src_number == src
    assert call.dst_number == dst
    assert call.time == t
    assert call.duration == duration
    assert call.src_loc == src_loc
    assert call.dst_loc == dst_loc

    # Test get_bill_date()
    m, y = call.get_bill_date()
    assert m == 1 and y == 2020

    # Test string representation (it should contain the key parts)
    s = str(call)
    assert src in s and dst in s and "dur" in s

    # Test that get_drawables() returns a non-empty list.
    drawables = call.get_drawables()
    assert isinstance(drawables, list) and len(drawables) >= 2

    # Test that get_connection() returns a Drawable object.
    connection = call.get_connection()
    from call import Drawable  # import Drawable from call module
    assert isinstance(connection, Drawable)


###############################################################################
# Tests for CallHistory
###############################################################################


def test_callhistory_register_and_get_monthly_history():
    ch = CallHistory()
    # Create two calls in January 2020.
    t1 = datetime.datetime(2020, 1, 15, 10, 0, 0)
    t2 = datetime.datetime(2020, 1, 20, 11, 0, 0)
    call1 = Call("111", "222", t1, 60, (0.0, 0.0), (1.0, 1.0))
    call2 = Call("333", "444", t2, 120, (0.0, 0.0), (1.0, 1.0))

    ch.register_outgoing_call(call1)
    ch.register_incoming_call(call2)

    out_calls, in_calls = ch.get_monthly_history(1, 2020)
    assert call1 in out_calls
    assert call2 in in_calls

    # When no month is specified, all calls should be returned.
    out_all, in_all = ch.get_monthly_history()
    assert call1 in out_all and call2 in in_all


###############################################################################
# Tests for Bill
###############################################################################


def test_bill_set_rates_and_add_costs():
    bill = Bill()
    # Initially, cost should be 0.
    assert bill.get_cost() == 0

    # Set rates and add fixed cost.
    bill.set_rates("MTM", 0.05)
    bill.add_fixed_cost(50)
    bill.add_billed_minutes(10)
    bill.add_free_minutes(5)
    # Expected cost: fixed cost + (min_rate * billed minutes)
    expected_cost = 50 + (0.05 * 10)
    assert math.isclose(bill.get_cost(), expected_cost, abs_tol=1e-6)

    summary = bill.get_summary()
    assert summary["type"] == "MTM"
    assert summary["fixed"] == 50
    assert summary["free_mins"] == 5
    assert summary["billed_mins"] == 10
    assert summary["min_rate"] == 0.05
    assert math.isclose(summary["total"], expected_cost, abs_tol=1e-6)


###############################################################################
# Tests for PhoneLine
###############################################################################


@pytest.fixture
def dummy_phoneline():
    # Create a PhoneLine using the DummyContract
    contract = DummyContract3()
    pl = PhoneLine("1234567", contract)
    return pl


def test_phoneline_new_month_creates_bill(dummy_phoneline):
    pl = dummy_phoneline
    # Initially, there should be no bill for Jan 2020.
    assert pl.get_bill(1, 2020) is None
    # Advance to January 2020.
    pl.new_month(1, 2020)
    bill = pl.get_bill(1, 2020)
    assert bill is not None
    # Instead of calling get_summary() on bill (since bill is already a dictionary),
    # check that the dictionary contains the expected key.
    assert "number" in bill, "Bill summary should contain the phone number."


def test_phoneline_make_and_receive_call(dummy_phoneline):
    pl = dummy_phoneline
    pl.new_month(1, 2020)
    t = datetime.datetime(2020, 1, 15, 12, 0, 0)
    call_out = Call("1234567", "7654321", t, 120, (0.0, 0.0), (1.0, 1.0))
    pl.make_call(call_out)
    # Check that call_out is in the outgoing call history.
    out_calls, _ = pl.get_monthly_history(1, 2020)
    assert call_out in out_calls

    call_in = Call("7654321", "1234567", t, 60, (0.0, 0.0), (1.0, 1.0))
    pl.receive_call(call_in)
    # Check that call_in is in the incoming call history.
    _, in_calls = pl.get_monthly_history(1, 2020)
    assert call_in in in_calls


def test_phoneline_cancel_line(dummy_phoneline):
    pl = dummy_phoneline
    pl.new_month(1, 2020)
    fee = pl.cancel_line()
    # Dummy contract returns 0 fee if no calls were made.
    assert fee == 0


###############################################################################
# Tests for Customer
###############################################################################


@pytest.fixture
def dummy_customer():
    # Create a Customer with two phone lines using the DummyContract.
    cust = Customer(1234)
    contract1 = DummyContract3()
    contract2 = DummyContract3()
    pl1 = PhoneLine("1111", contract1)
    pl2 = PhoneLine("2222", contract2)
    cust.add_phone_line(pl1)
    cust.add_phone_line(pl2)
    return cust


def test_customer_get_phone_numbers(dummy_customer):
    numbers = dummy_customer.get_phone_numbers()
    assert "1111" in numbers and "2222" in numbers


def test_customer_make_and_receive_call(dummy_customer):
    cust = dummy_customer
    # Advance month on all phone lines.
    cust.new_month(1, 2020)
    t = datetime.datetime(2020, 1, 1, 12, 0, 0)
    # Make an outgoing call from phone number "1111".
    call_out = Call("1111", "3333", t, 120, (0.0, 0.0), (1.0, 1.0))
    cust.make_call(call_out)
    # Retrieve call history for phone "1111".
    history_list = cust.get_call_history("1111")
    # Since there is one phone line for "1111", we expect one CallHistory object.
    assert len(history_list) == 1
    ch = history_list[0]
    out_calls, _ = ch.get_monthly_history(1, 2020)
    assert call_out in out_calls

    # Receive a call on phone number "2222".
    call_in = Call("4444", "2222", t, 60, (0.0, 0.0), (1.0, 1.0))
    cust.receive_call(call_in)
    history_list2 = cust.get_call_history("2222")
    assert len(history_list2) == 1
    ch2 = history_list2[0]
    _, in_calls = ch2.get_monthly_history(1, 2020)
    assert call_in in in_calls


def test_customer_cancel_phone_line(dummy_customer):
    cust = dummy_customer
    # Cancel phone line "1111" and check that the fee returned equals that from the phone line.
    fee = cust.cancel_phone_line("1111")
    # DummyContract cancel returns 0.
    assert fee == 0


def test_customer_generate_bill(dummy_customer, capsys):
    cust = dummy_customer
    # Advance to a new month.
    cust.new_month(1, 2020)
    # Make a call to add some billing activity.
    t = datetime.datetime(2020, 1, 1, 12, 0, 0)
    call = Call("1111", "2222", t, 120, (0.0, 0.0), (1.0, 1.0))
    cust.make_call(call)
    bill_summary = cust.generate_bill(1, 2020)
    # bill_summary is a tuple: (customer id, total cost, list of bill summaries)
    assert bill_summary[0] == 1234
    # Check that total cost is a float (the dummy contract sets a rate of 0.05 and adds 1 billed minute)
    assert isinstance(bill_summary[1], float)
    # Check that there is at least one phone line bill summary.
    assert len(bill_summary[2]) >= 1


# --- Helper Functions and Fixtures ---

###############################################################################
# Helper functions and fixtures

# Helper functions and fixtures


def make_event(event_type: str, src: str, dst: str, time_str: str, duration: int,
               src_loc: list[float], dst_loc: list[float]) -> dict:
    """Return a dictionary representing an event (a call or SMS)."""
    return {
        "type": event_type,
        "src_number": src,
        "dst_number": dst,
        "time": time_str,
        "duration": duration,
        "src_loc": src_loc,
        "dst_loc": dst_loc
    }


@pytest.fixture
def dummy_customers_for_events() -> list[Customer]:
    """
    Create two dummy customers:
      - Customer A with phone line "1111"
      - Customer B with phone line "2222"
    Each phone line uses an MTMContract that starts on Jan 1, 2020.
    """
    custA = Customer(1111)
    custB = Customer(2222)
    lineA = PhoneLine("1111", MTMContract(datetime.date(2020, 1, 1)))
    lineB = PhoneLine("2222", MTMContract(datetime.date(2020, 1, 1)))
    custA.add_phone_line(lineA)
    custB.add_phone_line(lineB)
    return [custA, custB]


###############################################################################
# Tests for process_event_history


def test_process_event_history_single_call(dummy_customers_for_events):
    """
    Test that a single call event is processed correctly:
      - A bill for January 2020 is created for both involved phone lines.
      - Customer A (phone "1111") records the call as outgoing.
      - Customer B (phone "2222") records the call as incoming.
    """
    log = {
        "events": [
            make_event("call", "1111", "2222", "2020-01-15 10:00:00", 60,
                       [-79.5, 43.7], [-79.6, 43.8])
        ]
    }
    process_event_history(log, dummy_customers_for_events)
    custA, custB = dummy_customers_for_events

    # Check that for each phone line, a bill for (1,2020) exists.
    for cust in [custA, custB]:
        for line in cust._phone_lines:
            assert (1, 2020) in line.bills, "Bill for January 2020 should be created."

    # Check that Customer A's phone "1111" has one outgoing call in January.
    histA = custA.get_call_history("1111")
    # We assume get_call_history returns a list with one CallHistory object.
    outgoing = histA[0].outgoing_calls.get((1, 2020), [])
    assert len(outgoing) == 1, "There should be one outgoing call in January for phone 1111."

    # Check that Customer B's phone "2222" has one incoming call in January.
    histB = custB.get_call_history("2222")
    incoming = histB[0].incoming_calls.get((1, 2020), [])
    assert len(incoming) == 1, "There should be one incoming call in January for phone 2222."


def test_process_event_history_multiple_calls_same_month(dummy_customers_for_events):
    """
    Test that multiple call events in the same month are recorded under the same monthly bill.
    Here we use two call events in January 2020.
    """
    log = {
        "events": [
            # First call: from 1111 to 2222 in January.
            make_event("call", "1111", "2222", "2020-01-10 09:00:00", 30,
                       [-79.5, 43.7], [-79.6, 43.8]),
            # Second call: from 1111 to 2222 in January.
            make_event("call", "1111", "2222", "2020-01-20 11:00:00", 45,
                       [-79.5, 43.7], [-79.6, 43.8])
        ]
    }
    process_event_history(log, dummy_customers_for_events)
    custA, custB = dummy_customers_for_events

    # Check that each phone line has a bill for January 2020.
    for cust in [custA, custB]:
        for line in cust._phone_lines:
            assert (1, 2020) in line.bills, "Bill for January 2020 should exist for all phone lines."

    # For Customer A (phone "1111"), the outgoing call history for January should have 2 calls.
    histA = custA.get_call_history("1111")[0]
    outgoing = []
    for calls in histA.outgoing_calls.values():
        outgoing.extend(calls)
    assert len(outgoing) == 2, "There should be 2 outgoing calls in January for phone 1111."

    # For Customer B (phone "2222"), the incoming call history for January should have 2 calls.
    histB = custB.get_call_history("2222")[0]
    incoming = []
    for calls in histB.incoming_calls.values():
        incoming.extend(calls)
    assert len(incoming) == 2, "There should be 2 incoming calls in January for phone 2222."


def test_process_event_history_sms_trigger(dummy_customers_for_events):
    """
    Test that an SMS event (which is not recorded as a call) still triggers month advancement.
    Here we have:
      - A call event in January 2020.
      - An SMS event in February 2020.
      - A call event in February 2020.
    We expect that the call event in February is recorded in the new monthly bill.
    """
    log = {
        "events": [
            # Call event in January 2020.
            make_event("call", "1111", "2222", "2020-01-15 10:00:00", 60,
                       [-79.5, 43.7], [-79.6, 43.8]),
            # SMS event in February 2020 (should trigger month advancement but not be recorded).
            make_event("sms", "1111", "2222", "2020-02-01 09:00:00", 0,
                       [-79.5, 43.7], [-79.6, 43.8]),
            # Call event in February 2020.
            # (Make sure the call is from 1111 to 2222 so that Customer B records it as incoming.)
            make_event("call", "1111", "2222", "2020-02-20 11:00:00", 45,
                       [-79.5, 43.7], [-79.6, 43.8])
        ]
    }
    process_event_history(log, dummy_customers_for_events)
    custA, custB = dummy_customers_for_events

    # For Customer A (phone "1111"), check that January has one outgoing call.
    histA = custA.get_call_history("1111")[0]
    jan_outgoing = []
    for calls in histA.outgoing_calls.values():
        for call in calls:
            if call.time.month == 1:
                jan_outgoing.append(call)
    assert len(jan_outgoing) == 1, "Customer A should have 1 outgoing call in January."

    # For Customer B (phone "2222"), check that February has one incoming call.
    histB = custB.get_call_history("2222")[0]
    feb_incoming = []
    for calls in histB.incoming_calls.values():
        for call in calls:
            if call.time.month == 2:
                feb_incoming.append(call)
    assert len(feb_incoming) == 1, "Customer B should have 1 incoming call in February."


def test_process_event_history_chronological(dummy_customers_for_events):
    """
    Test that when events span different months, the new_month function is called correctly so that
    bills and call histories are recorded separately per month.
    """
    log = {
        "events": [
            # Event 1: Call in January 2020.
            make_event("call", "1111", "2222", "2020-01-15 09:00:00", 30,
                       [-79.5, 43.7], [-79.6, 43.8]),
            # Event 2: SMS in January 2020 (should not record a call but should not affect the current month).
            make_event("sms", "1111", "2222", "2020-01-15 10:00:00", 0,
                       [-79.5, 43.7], [-79.6, 43.8]),
            # Event 3: Call in February 2020.
            make_event("call", "1111", "2222", "2020-02-15 11:00:00", 45,
                       [-79.5, 43.7], [-79.6, 43.8])
        ]
    }
    process_event_history(log, dummy_customers_for_events)
    custA, custB = dummy_customers_for_events

    # For Customer A (phone "1111"), verify that the January call is recorded.
    histA = custA.get_call_history("1111")[0]
    jan_outgoing = []
    for calls in histA.outgoing_calls.values():
        for call in calls:
            if call.time.month == 1:
                jan_outgoing.append(call)
    assert len(jan_outgoing) == 1, "There should be 1 outgoing call in January for Customer A."

    # For Customer B (phone "2222"), verify that the February call is recorded.
    histB = custB.get_call_history("2222")[0]
    feb_incoming = []
    for calls in histB.incoming_calls.values():
        for call in calls:
            if call.time.month == 2:
                feb_incoming.append(call)
    assert len(feb_incoming) == 1, "There should be 1 incoming call in February for Customer B."


if __name__ == '__main__':
    pytest.main(['tests.py'])
