from brownie import interface, config, network, accounts
from scripts.helpful_scripts import get_account
from web3 import Web3

def get_weth():
    """
    The purpose of this function is to get the ERC 20 token version of ETH which is WETH.
    In other words, we are swapping our ETH with WETH
    """
    account = get_account()
    weth_contract = interface.IERC20(config["networks"][network.show_active()]["weth_token"])

    # deposit() method of the weth_contract gives us WETH and collect our Eth
    # weth_contract deposits some weth token after grabing 0.1 ether from account, 

    tx = weth_contract.deposit({"from": account, "value": Web3.toWei(0.1, "ether")})

    print("0.1 WETH has been deposited to the account")
    print(f"{network.show_active()}")

    return tx


def main():
    get_weth()

