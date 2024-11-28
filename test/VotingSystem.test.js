const VotingSystem = artifacts.require("VotingSystem");

contract ("VotingSystem",(accounts) => {
    let voting;

    before(async () => {
        voting = await VotingSystem.deployed();
    });

    it("should add candidates", async () => {
        await voting.addCandidate("Alice",{ from: accounts[0] });
        let candidate = await voting.getCandidate(1);
        assert.equal(candidate[1], "Alice","Candidate name should be Alice");
    });

    it("should allow a voter to cast a vote", async () => {
        await voting.castVote(1, { from: accounts[1] });
        let candidate = await voting.getCandidate(1);
        assert.equal(candidate[2].toNumber(), 1, "Vote count should be 1 for Alice");
    });
});