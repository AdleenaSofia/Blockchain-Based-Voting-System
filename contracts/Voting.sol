// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VotingSystem{
    struct Candidate{
        uint id;
        string name;
        uint voteCount;
    }

    struct Voter{
        bool hasVoted;
        uint vote;
    }

    address public admin;
    uint public candidateCount;
    uint public voterCount;
    mapping(uint => Candidate) public candidates;
    mapping(address => Voter) public voters;

    event VoteCast(address indexed voter,uint candidateId);

    constructor(){
        admin = msg.sender;
    }

    modifier onlyAdmin(){
        require(msg.sender == admin,"Only admin can call this.");
        _;
    }

    function addCandidate(string memory _name) public onlyAdmin{
        candidateCount++;
        candidates[candidateCount] = Candidate(candidateCount, _name, 0);
    }

    function castVote(uint _candidateId) public {
        require(!voters[msg.sender].hasVoted,"Already voted.");
        require(_candidateId > 0 && _candidateId <= candidateCount,"Invalid candidate ID.");

        voters[msg.sender].hasVoted = true;
        voters[msg.sender].vote = _candidateId;

        candidates[_candidateId].voteCount++;

        emit VoteCast(msg.sender, _candidateId);
    }

    function getCandidate(uint _candidateId) public view returns (uint, string memory, uint){
        Candidate memory candidate = candidates[_candidateId];
        return (candidate.id, candidate.name, candidate.voteCount);
    }
}
