pragma solidity ^0.8.0;

contract MultiVulnTest {
    address public owner;
    mapping(address => uint256) public balances;
    mapping(address => bool) public authorized;
    
    constructor() {
        owner = msg.sender;
    }
    
    // Reentrancy vulnerability
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount);
        
        (bool success,) = msg.sender.call{value: amount}("");
        require(success);
        
        balances[msg.sender] -= amount; // State change after external call
    }
    
    // Access control vulnerability
    function adminTransfer(address from, address to, uint256 amount) public {
        // Missing proper authorization check
        require(authorized[msg.sender] || msg.sender == owner);
        balances[from] -= amount;
        balances[to] += amount;
    }
    
    // Unchecked return value
    function batchPayment(address[] memory recipients, uint256[] memory amounts) public {
        require(recipients.length == amounts.length);
        
        for (uint i = 0; i < recipients.length; i++) {
            // Vulnerable: unchecked low-level call
            recipients[i].call{value: amounts[i]}("");
        }
    }
    
    // Timestamp dependence
    function timeLock() public view returns (bool) {
        // Vulnerable: block.timestamp manipulation
        return block.timestamp > 1640995200; // Hardcoded timestamp
    }
}
