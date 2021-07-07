from multiprocessing import Pool
from time import sleep

from . import config
from . import customexceptions
import requests
import json

# Write your Jobcoin API client here.


def create_jobcoins(sender_address):
    post_fields = {'address': sender_address}
    response = requests.post("https://jobcoin.gemini.com/thorn-hatbox/create", data=post_fields)
    if response.status_code != 200:
        raise customexceptions.ApiException({"message":"JobCoin create failed", "status":response.status_code})


def get_balance(address):
    response = requests.get(config.API_ADDRESS_URL+"/"+ address)
    json_data = json.loads(response.text)
    if response.status_code != 200:
        raise customexceptions.ApiException({"message":"JobCoin create failed", "status":response.status_code})
    return int(json_data["balance"])


def initiate_transfer_coins(amount, sender_address, deposit_address, withdrawal_addresses, withdrawal_amounts):
    if not withdrawal_addresses:
        raise ValueError("Withdrawal addresses empty!")
    transfer_coins_deposit_address(sender_address, deposit_address, amount)
    pool = Pool(processes=1)  # Start a worker processes.
    pool.apply_async(transfer_coins_home_address, [deposit_address, withdrawal_addresses, amount, withdrawal_amounts])


def transfer_coins(from_address, to_address, amount, error_message):
    post_fields = {'fromAddress': from_address, 'toAddress': to_address, 'amount': amount}
    response = requests.post("https://jobcoin.gemini.com/thorn-hatbox/send", data=post_fields)
    if response.status_code != 200:
        raise customexceptions.ApiException({"message": error_message, "status": response.status_code})


def transfer_coins_deposit_address(sender_address, deposit_address, amount):
    transfer_coins(sender_address, deposit_address, amount, config.DEPOSIT_ADDRESS_TRANSFER_ERR_MSG)


def transfer_coins_home_address(deposit_address, withdrawal_addresses, amount, withdrawal_amounts):
    transfer_coins(deposit_address, config.HOME_ADDRESS, amount, config.HOME_ADDRESS_TRANSFER_ERR_MSG)
    sleep(1)
    withdrawal_address_list = withdrawal_addresses.split(",")
    for i in range(len(withdrawal_address_list)):
        sleep(1)
        transfer_coins_withdrawal_address(config.HOME_ADDRESS, withdrawal_address_list[i], withdrawal_amounts[i])


def transfer_coins_withdrawal_address(home_address, withdrawal_address, increment_amount):
    transfer_coins(home_address, withdrawal_address, increment_amount, config.WITHDRAWAL_ADDRESS_TRANSFER_ERR_MSG)





