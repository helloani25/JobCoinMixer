#!/usr/bin/env python
import sys
import uuid
import re
import click

from jobcoin import jobcoin


def validate_percent_amounts(amounts):
    if not amounts:
        raise ValueError("Amounts must be comma separated list of integers")
    if re.search(r'(?:\\d+|,)+', amounts) is None:
        raise ValueError("Amounts must be comma separated list of integers ")
    percent_amounts = list(map(lambda x: int(x), amounts.split(",")))
    percent_sum = sum(percent_amounts)
    if sum(percent_amounts) > 100:
        raise ValueError("Percent sum {} does not equal 100 ".format(percent_sum))
    return percent_amounts


def validate_amount(percent_amounts, amount, sender_address):
    balance = jobcoin.get_balance(sender_address)
    amount = int(amount)
    if amount > balance:
        raise ValueError("Withdrawal amount {} exceeds balance {}" .format(amount , balance))

    withdrawal_amounts = list(map(lambda x: x*0.01*amount, percent_amounts))
    return withdrawal_amounts


@click.command()
def main(args=None):
    print('Welcome to the Jobcoin mixer!\n')
    while True:
        sender_address = click.prompt(
            'Please enter a sender address',
            prompt_suffix='\n[blank to quit] > ',
            default='',
            show_default=False)
        addresses = click.prompt(
            'Please enter a comma-separated list of new, unused Jobcoin '
            'addresses where your mixed Jobcoins will be sent.',
            prompt_suffix='\n[blank to quit] > ',
            default='',
            show_default=False)
        if addresses.strip() == '':
            sys.exit(0)
        percent_amounts = click.prompt(
            'Please enter a comma-separated list of percentage amounts for the Jobcoin '
            'addresses where your mixed Jobcoins will be sent.',
            prompt_suffix='\n[blank to quit] > ',
            default='',
            show_default=False)
        percent_amounts = validate_percent_amounts(percent_amounts)
        deposit_address = uuid.uuid4().hex
        click.echo(
            '\nYou may now send Jobcoins to address {deposit_address}. They '
            'will be mixed and sent to your destination addresses.\n'
              .format(deposit_address=deposit_address))
        jobcoin.create_jobcoins(sender_address)
        amount = click.prompt(
            'Please enter the amount',
            prompt_suffix='\n[blank to quit] > ',
            default='',
            show_default=False)
        withdrawal_amounts = validate_amount(percent_amounts, amount, sender_address)
        jobcoin.initiate_transfer_coins(amount, sender_address, deposit_address, addresses, withdrawal_amounts)


if __name__ == '__main__':
    sys.exit(main())
