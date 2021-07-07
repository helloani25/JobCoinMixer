#!/usr/bin/env python
import json
import pytest
import requests
from click.testing import CliRunner

from ..jobcoin import config
from ..jobcoin import jobcoin
from .. import cli


@pytest.fixture
def response():
    return requests.get('https://jobcoin.gemini.com')


def test_cli_basic():
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'Welcome to the Jobcoin mixer' in result.output


def test_validate_percent_amounts():
    percent_amounts = "10, 100"
    with pytest.raises(ValueError):
        cli.validate_percent_amounts(percent_amounts)


def test_validate_percent_amounts_invalid_input():
    percent_amounts = "10, b"
    with pytest.raises(ValueError):
        cli.validate_percent_amounts(percent_amounts)


def test_validate_percent_amounts_empty_input():
    percent_amounts = ""
    with pytest.raises(ValueError):
        cli.validate_percent_amounts(percent_amounts)


def test_validate_withdrawals_exceeds_amount():
    runner = CliRunner()
    sender_address = "John"
    amount = 999999
    percent_amounts = [10, 90]
    runner.invoke(cli.main, input='John').output
    runner.invoke(cli.main, input='1234,4321').output
    runner.invoke(cli.main, input='10,900').output
    runner.invoke(cli.main, input='50').output
    with pytest.raises(ValueError):
        cli.validate_amount(percent_amounts, amount, sender_address)


def test_validate_amount_exceeds_balance():
    runner = CliRunner()
    sender_address = "John"
    amount = 999999
    percent_amounts = [10, 90]
    runner.invoke(cli.main, input='John').output
    runner.invoke(cli.main, input='1234,4321').output
    runner.invoke(cli.main, input='10,90').output
    runner.invoke(cli.main, input='50').output
    with pytest.raises(ValueError):
        cli.validate_amount(percent_amounts, amount, sender_address)

def test_validate_amount():
    runner = CliRunner()
    sender_address = "John"
    amount = 50
    percent_amounts = [10, 90]
    runner.invoke(cli.main, input='John').output
    runner.invoke(cli.main, input='1234,4321').output
    runner.invoke(cli.main, input='10,90').output
    runner.invoke(cli.main, input='50').output
    assert cli.validate_amount(percent_amounts, amount, sender_address) == [5, 45]


def test_transfer_coins_deposit_address():
    sender_address = "John"
    amount = 50
    deposit_address = "1c06c250d76b406c8926954f81c5f8cf"
    jobcoin.create_jobcoins(sender_address)
    jobcoin.transfer_coins_deposit_address(sender_address, deposit_address, amount)
    response = requests.get(config.API_ADDRESS_URL+"/"+deposit_address)
    json_data = json.loads(response.text)
    assert int(json_data["transactions"][-1]["amount"]) == amount
    assert json_data["transactions"][-1]["fromAddress"] == sender_address
    assert json_data["transactions"][-1]["toAddress"] == deposit_address


def test_transfer_coins_withdrawal_address():
    sender_address = "John"
    amount = 50
    deposit_address = "1c06c250d76b406c8926954f81c5f8cf"
    withdrawal_addresses = ["Jane", "Jill"]
    jobcoin.create_jobcoins(sender_address)
    jobcoin.transfer_coins_deposit_address(sender_address, deposit_address, amount)
    jobcoin.transfer_coins(deposit_address, config.HOME_ADDRESS, amount, config.HOME_ADDRESS_TRANSFER_ERR_MSG)
    jobcoin.transfer_coins_withdrawal_address(config.HOME_ADDRESS, withdrawal_addresses[0], 5)
    response = requests.get(config.API_ADDRESS_URL+"/"+withdrawal_addresses[0])
    json_data = json.loads(response.text)
    assert int(json_data["transactions"][-1]["amount"]) == 5
    assert json_data["transactions"][-1]["toAddress"] == "Jane"

    jobcoin.transfer_coins_withdrawal_address(config.HOME_ADDRESS, withdrawal_addresses[1], 45)
    response = requests.get(config.API_ADDRESS_URL+"/"+withdrawal_addresses[1])
    json_data = json.loads(response.text)
    assert int(json_data["transactions"][-1]["amount"]) == 45
    assert json_data["transactions"][-1]["toAddress"] == "Jill"


def test_initiate_transfer_coins():
    sender_address = "John"
    amount = 50
    deposit_address = "1c06c250d76b406c8926954f81c5f8cf"
    withdrawal_addresses = ["Jane", "Jill"]
    withdrawal_amounts = ["10, 90"]
    jobcoin.create_jobcoins(sender_address)
    jobcoin.initiate_transfer_coins(amount, sender_address, deposit_address, withdrawal_addresses, withdrawal_amounts)

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