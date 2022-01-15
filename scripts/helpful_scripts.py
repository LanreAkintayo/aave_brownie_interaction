from brownie import accounts, network, interface, config

FORKED_BLOCKCHAIN_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["ganache-local", "development"]


def get_account(index=None, id=None):
    """
    1. if index is specified, use accounts[index]
    2. if accountId is specified, use that account
    3. if we are on a development environment, use accounts[0]
    4. if we are on a test network generate your account from the private key in brownie-config.yaml,
    """

    # 1
    if index:
        return accounts[index]

    # 2
    if id:
        return accounts.load(id)

    # 3
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_BLOCKCHAIN_ENVIRONMENTS
    ):
        return accounts[0]

    # 4
    return accounts.add(config["wallets"]["from_key"])