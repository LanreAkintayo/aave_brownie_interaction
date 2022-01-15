Here,

LendingPool contract is the main contract of the aave protocol.

LendingPoolAddressesProvider smart contract:
Whenever the LendingPool smartcontract is needed, It is recommended to fetch the correct address from LendingPoolAddressesProvider.

So, an instance of LendingPoolAddressesProvider calls getLendingPool() method and that method returns the Lending Pool address we need.

Note that you need to approve another contract to use your tokens


Borrowing DAI
Some certain amount of DAI will be deposited to my account.
The DAI will be transferred from aave to my account.
1. Get the ETH/DAI conversion rate
2. The DAI token you can borrow depends on the available borrows you have in the AAVE protocol.
