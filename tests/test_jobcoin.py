#!/usr/bin/env python
import json

import pytest
import re

import requests
from click.testing import CliRunner

from jobcoin import jobcoin
from ..jobcoin import config
from .. import cli


@pytest.fixture
def response():
    import requests
    return requests.get('https://jobcoin.gemini.com')


def test_cli_basic():
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'Welcome to the Jobcoin mixer' in result.output


def test_cli_creates_address():
    runner = CliRunner()
    address_create_output = runner.invoke(cli.main, input='1234,4321').output
    output_re = re.compile(
        r'You may now send Jobcoins to address [0-9a-zA-Z]{32}. '
        'They will be mixed and sent to your destination addresses.'
    )
    assert output_re.search(address_create_output) is not None


def test_transfer_coins_deposit_address():
    sender_address = "John"
    amount = 50
    deposit_address = "1c06c250d76b406c8926954f81c5f8cf"
    jobcoin.create_jobcoins(sender_address)
    jobcoin.transfer_coins_deposit_address(sender_address, deposit_address, 50)
    response = requests.get(config.API_ADDRESS_URL+"/"+deposit_address)
    json_data = json.loads(response.text)
    assert int(json_data["transactions"][-1]["amount"]) == 50
    assert json_data["transactions"][-1]["fromAddress"] == sender_address
    assert json_data["transactions"][-1]["toAddress"] == deposit_address


def test_transfer_coins_home_address():
    sender_address = "John"
    amount = 50
    deposit_address = "1c06c250d76b406c8926954f81c5f8cf"
    jobcoin.create_jobcoins(sender_address)
    jobcoin.transfer_coins_deposit_address(sender_address, deposit_address, amount)
    jobcoin.transfer_coins_deposit_address(deposit_address, config.HOME_ADDRESS, amount)
    response = requests.get(config.API_ADDRESS_URL+"/"+ config.HOME_ADDRESS)
    json_data = json.loads(response.text)
    assert int(json_data["transactions"][-1]["amount"]) == 50
    assert json_data["transactions"][-1]["fromAddress"] == deposit_address
    assert json_data["transactions"][-1]["toAddress"] == config.HOME_ADDRESS


def test_transfer_coins_withdrawal_address():
    sender_address = "John"
    amount = 50
    deposit_address = "1c06c250d76b406c8926954f81c5f8cf"
    withdrawal_addresses = ["Jane", "Jill"]
    jobcoin.create_jobcoins(sender_address)
    jobcoin.transfer_coins_deposit_address(sender_address, deposit_address, amount)
    jobcoin.transfer_coins_deposit_address(deposit_address, config.HOME_ADDRESS, amount)
    jobcoin.transfer_coins_deposit_address(config.HOME_ADDRESS, withdrawal_addresses[0], 25)
    response = requests.get(config.API_ADDRESS_URL+"/"+withdrawal_addresses[0])
    json_data = json.loads(response.text)
    assert int(json_data["transactions"][-1]["amount"]) == 25
    assert json_data["transactions"][-1]["toAddress"] == "Jane"

    jobcoin.transfer_coins_deposit_address(config.HOME_ADDRESS, withdrawal_addresses[1], 25)
    response = requests.get(config.API_ADDRESS_URL+"/"+withdrawal_addresses[1])
    json_data = json.loads(response.text)
    assert int(json_data["transactions"][-1]["amount"]) == 25
    assert json_data["transactions"][-1]["toAddress"] == "Jill"


def test_initiate_transfer_coins():
    sender_address = "John"
    amount = 50
    deposit_address = "1c06c250d76b406c8926954f81c5f8cf"
    withdrawal_addresses = ["Jane", "Jill"]
    jobcoin.create_jobcoins(sender_address)
    jobcoin.initiate_transfer_coins(amount, sender_address, deposit_address, withdrawal_addresses)

    response = requests.get(config.API_ADDRESS_URL + "/" + sender_address)
    json_data = json.loads(response.text)
    assert int(json_data["transactions"][-1]["amount"]) == 50
    assert json_data["transactions"][-1]["fromAddress"] == sender_address
    assert json_data["transactions"][-1]["toAddress"] == deposit_address

    response = requests.get(config.API_ADDRESS_URL+"/"+withdrawal_addresses[0])
    json_data = json.loads(response.text)
    assert int(json_data["transactions"][-1]["amount"]) == 25
    assert json_data["transactions"][-1]["toAddress"] == "Jane"

    response = requests.get(config.API_ADDRESS_URL+"/"+withdrawal_addresses[1])
    json_data = json.loads(response.text)
    assert int(json_data["transactions"][-1]["amount"]) == 25
    assert json_data["transactions"][-1]["toAddress"] == "Jill"