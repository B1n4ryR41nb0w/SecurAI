pragma solidity ^0.7.6;

contract OverflowTest {
    mapping(address => uint256) public balances;
    uint256 public totalSupply;
    
    function transfer(address to, uint256 amount) public {
        require(balances[msg.sender] >= amount);
        
        // Vulnerable: potential overflow without SafeMath
        balances[to] += amount;
        balances[msg.sender] -= amount;
    }
    
    function batchTransfer(address[] memory recipients, uint256 amount) public {
        // Vulnerable: multiplication overflow
        uint256 totalAmount = recipients.length * amount;
        require(balances[msg.sender] >= totalAmount);
        
        for (uint i = 0; i < recipients.length; i++) {
            balances[recipients[i]] += amount;
        }
        balances[msg.sender] -= totalAmount;
    }
}
