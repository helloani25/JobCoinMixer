#!/usr/bin/env python
import sys
import uuid

import jobcoin

import click

from jobcoin import jobcoin


@click.command()
def main(args=None):
    print('Welcome to the Jobcoin mixer!\n')
    while True:
        addresses = click.prompt(
            'Please enter a comma-separated list of new, unused Jobcoin '
            'addresses where your mixed Jobcoins will be sent.',
            prompt_suffix='\n[blank to quit] > ',
            default='',
            show_default=False)
        if addresses.strip() == '':
            sys.exit(0)
        deposit_address = uuid.uuid4().hex
        click.echo(
            '\nYou may now send Jobcoins to address {deposit_address}. They '
            'will be mixed and sent to your destination addresses.\n'
              .format(deposit_address=deposit_address))
        sender_address = click.prompt(
            'Please enter a sender address',
            prompt_suffix='\n[blank to quit] > ',
            default='',
            show_default=False)
        jobcoin.create_jobcoins(sender_address)
        amount = click.prompt(
            'Please enter the amount',
            prompt_suffix='\n[blank to quit] > ',
            default='',
            show_default=False)
        jobcoin.initiate_transfer_coins(amount, sender_address, deposit_address, addresses)


if __name__ == '__main__':
    sys.exit(main())
