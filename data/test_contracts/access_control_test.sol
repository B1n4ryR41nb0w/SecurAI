pragma solidity ^0.8.0;

contract AccessControlTest {
    address public owner;
    uint256 public totalSupply;
    mapping(address => uint256) public balances;
    
    constructor() {
        owner = msg.sender;
        totalSupply = 1000000;
        balances[owner] = totalSupply;
    }
    
    // Vulnerable: missing access control
    function mint(address to, uint256 amount) public {
        totalSupply += amount;
        balances[to] += amount;
    }
    
    // Vulnerable: weak access control
    function emergencyWithdraw() public {
        require(msg.sender != address(0)); // Weak check
        payable(msg.sender).transfer(address(this).balance);
    }
    
    // Proper access control example
    function setOwner(address newOwner) public {
        require(msg.sender == owner, "Only owner");
        owner = newOwner;
    }
}
