from brownie import interface, config, network
from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from web3 import Web3

amount = Web3.toWei(0.1, "ether")


def aave_borrow():
    """
    Here, we deposit an asset/weth token to aave.
    Note that before we can deposit some tokens in our account to another contract, we will need to approve the contract.
    """
    account = get_account()
    print(f"Current account: {account}")
    print(f"Current account balance  is {account.balance()}")

    weth_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork-dev"]:
        get_weth()  # Deposit some weth to account.

    lendingPool_contract = get_lending_pool()

    # We want to approve that lendingPool_contract.address should be able to withdraw from your account, multiple times, up to the tokens amount.
    approve_erc_token(weth_address, lendingPool_contract.address, amount, account)

    # The lendingPool_contract deposit aTokens to account after grabbing asset (represented by weth_contract.address) from account.
    # The amount of asset grabbed depends on the {amount}ETH
    # account.address is the address where aTokens will be deposited to.

    print("Depositing")
    tx = lendingPool_contract.deposit(
        weth_address, amount, account.address, 0, {"from": account}
    )
    tx.wait(1)
    print("Deposited!")

    totalDebtEth, availableBorrowsEth = get_borrowable_data(
        lendingPool_contract, account
    )

    print("Borrowing DAI")

    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )

    # I want to borrow 95 percent of my available borrows as DAI token to avoid liquidation.
    amount_of_dai_to_borrow = (availableBorrowsEth * 0.95) / dai_eth_price

    print(f"We are borrowing {amount_of_dai_to_borrow} DAI")

    # Now, we are about to borrow the DAI
    dai_address = config["networks"][network.show_active()]["dai_token"]

    # Borrows amount of asset with interestRateMode, sending the amount to msg.sender, with the debt being incurred by onBehalfOf.
    borrow_tx = lendingPool_contract.borrow(
        dai_address,  # adress of the token to borrow
        Web3.toWei(amount_of_dai_to_borrow, "ether"),  # amount of dai to borrow
        1,  # 1 means stable rate, 0 means variable rate
        0,  # 0 means no referal code
        account.address,  # debt will be incurred by this account
        {"from": account},  # DAI token will be transferred to this account.
    )

    borrow_tx.wait(1)

    print("We just borrowed some DAI")
    get_borrowable_data(lendingPool_contract, account)

    print("\nNow, we are repaying the DAI token we borrowed")

    # repay_all(amount_of_dai_to_borrow, lendingPool_contract, account)


def repay_all(amount_of_dai_to_borrow, lendingPool_contract, account):
    """
    function repay(address asset, uint256 amount, uint256 rateMode, address onBehalfOf)

    Before repaying, you have to approve that you want to pay back.

    If After paying with DAI, there is still some amount in debt, we pay with our collateral
    """

    dai_address = config["networks"][network.show_active()]["dai_token"]
    approve_erc_token(
        dai_address,
        lendingPool_contract.address,
        amount_of_dai_to_borrow,
        account,
    )

    repay_tx = lendingPool_contract.repay(
        dai_address, amount_of_dai_to_borrow, 1, account.address, {"from": account}
    )

    repay_tx.wait(1)

    print("Repaid!")


def get_asset_price(dai_eth_price_feed_address):
    price_feed_contract = interface.AggregatorV3Interface(dai_eth_price_feed_address)
    (
        roundId,
        answer,
        startedAt,
        updatedAt,
        answeredInRound,
    ) = price_feed_contract.latestRoundData()
    converted_dai_eth_price = Web3.fromWei(answer, "ether")
    # print(f"The DAI/ETH price is {converted_dai_eth_price}")
    return float(converted_dai_eth_price)


def get_dai_conversion_rate(amount, dai_price_feed_address):
    price_feed_contract = interface.AggregatorV3Interface(dai_price_feed_address)
    (
        roundId,
        answer,
        startedAt,
        updatedAt,
        answeredInRound,
    ) = price_feed_contract.latestRoundData()

    # 1 ETH = 3,100.78 DAI
    dai_to_eth = answer

    return (amount * dai_to_eth) / 10 ** 18


def get_borrowable_data(lendingPool_contract, account):
    (
        totalCollateralEth,
        totalDebthEth,
        availableBorrowsEth,
        currentLiquidationThreshold,
        ltv,
        healthFactor,
    ) = lendingPool_contract.getUserAccountData(account)

    totalCollateralEth = Web3.fromWei(totalCollateralEth, "ether")
    totalDebtEth = Web3.fromWei(totalDebthEth, "ether")
    availableBorrowsEth = Web3.fromWei(availableBorrowsEth, "ether")

    print(f"The current total collateral in ETH in aave is {totalCollateralEth}")
    print(f"The current total debt (in ETH) in aave is {totalDebtEth}")
    print(f"The current available borrows (in ETH) in aave is {availableBorrowsEth}")
    print(f"The current account ETH balance is {get_account().balance()}ETH")

    return (float(totalDebtEth), float(availableBorrowsEth))


def approve_erc_token(erc20_token_address, spender, amount, account):
    erc20_token_contract = interface.IERC20(erc20_token_address)

    # Approving that spender should be able to spend up to amount from this account.
    # amount in eth will be converted to corresponding erc20_token amount
    tx = erc20_token_contract.approve(spender, amount, {"from": account})

    tx.wait(1)
    print("Approved!")

    return tx


def main():
    aave_borrow()


def get_lending_pool():
    """Here, I want to get Lending Pool contract"""

    # Get an instance of LendingPoolAddressesProvider smart contract

    lendingPoolAddressesProvider_address = config["networks"][network.show_active()][
        "lending_pool_addresses_provider"
    ]
    lendingPoolAddressesProvider_contract = interface.ILendingPoolAddressesProvider(
        lendingPoolAddressesProvider_address
    )

    # getLendingPool() method returns the address of the associated LendingPool smart contract. So through that address and abi, # we can get the LendingPool smart contract

    lendingPool_address = lendingPoolAddressesProvider_contract.getLendingPool()
    lendingPool_contract = interface.ILendingPool(lendingPool_address)

    return lendingPool_contract


# Current account: 0x66aB6D9362d4F35596279692F0251Db635165871
# Current account balance  is 100000000000000000000
