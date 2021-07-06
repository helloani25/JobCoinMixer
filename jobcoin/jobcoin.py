from multiprocessing import Pool
from time import sleep

from . import config
from . import customexceptions
import requests

# Write your Jobcoin API client here.


def create_jobcoins(sender_address):
    post_fields = {'address': sender_address}
    response = requests.post("https://jobcoin.gemini.com/thorn-hatbox/create", data=post_fields)
    if response.status_code != 200:
        raise customexceptions.ApiException({"message":"JobCoin create failed", "status":response.status_code})


def initiate_transfer_coins(amount, sender_address, deposit_address, withdrawal_addresses):
    if not withdrawal_addresses:
        raise ValueError("Withdrawal addresses empty!")
    transfer_coins_deposit_address(sender_address, deposit_address, amount)
    pool = Pool(processes=1)  # Start a worker processes.
    pool.apply_async(transfer_coins_home_address, [deposit_address, withdrawal_addresses, amount])


def transfer_coins(from_address, to_address, amount, error_message):
    post_fields = {'fromAddress': from_address, 'toAddress': to_address, 'amount': amount}
    response = requests.post("https://jobcoin.gemini.com/thorn-hatbox/send", data=post_fields)
    if response.status_code != 200:
        raise customexceptions.ApiException({"message": error_message, "status": response.status_code})


def transfer_coins_deposit_address(sender_address, deposit_address, amount):
    transfer_coins(sender_address, deposit_address, amount, config.DEPOSIT_ADDRESS_TRANSFER_ERR_MSG)


def transfer_coins_home_address(deposit_address, withdrawal_addresses, amount):
    transfer_coins(deposit_address, config.HOME_ADDRESS, amount, config.HOME_ADDRESS_TRANSFER_ERR_MSG)
    sleep(1)
    withdrawal_address_list = withdrawal_addresses.split(",")
    increment_amount = int(amount)/len(withdrawal_address_list)
    for address in withdrawal_address_list:
        sleep(1)
        transfer_coins_withdrawal_address(config.HOME_ADDRESS, address, increment_amount)


def transfer_coins_withdrawal_address(home_address, withdrawal_address, increment_amount):
    transfer_coins(home_address, withdrawal_address, increment_amount, config.WITHDRAWAL_ADDRESS_TRANSFER_ERR_MSG)





