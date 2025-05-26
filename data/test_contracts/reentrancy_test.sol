pragma solidity ^0.8.0;

contract ReentrancyTest {
    mapping(address => uint256) public balances;
    
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
    
    function withdraw() public {
        uint256 amount = balances[msg.sender];
        require(amount > 0);
        
        (bool success,) = msg.sender.call{value: amount}("");
        require(success);
        
        balances[msg.sender] = 0;
    }
}
