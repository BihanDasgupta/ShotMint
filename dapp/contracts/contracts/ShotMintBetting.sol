// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ShotMintBetting
 * @dev Smart contract for NBA game betting using RNN predictions
 */
contract ShotMintBetting {
    // Structs
    struct Game {
        string gameId;
        string team0;
        string team1;
        uint256 gameDate;
        bool isResolved;
        string winner; // "TEAM0" or "TEAM1"
        uint256 team0WinProbability; // Scaled by 10000 (e.g., 0.65 = 6500)
    }

    struct Bet {
        uint256 betId;
        string gameId;
        address bettor;
        string team; // "TEAM0" or "TEAM1"
        uint256 amount;
        uint256 odds; // Scaled by 10000 (e.g., 1.5x = 15000)
        uint256 timestamp;
        bool isResolved;
        bool isWon;
        uint256 payout;
    }

    // State variables
    address public owner;
    uint256 public totalBets;
    uint256 public contractBalance;
    uint256 public minBetAmount = 0.001 ether;
    uint256 public maxBetAmount = 10 ether;
    uint256 public houseEdge = 500; // 5% (500/10000)

    // Mappings
    mapping(string => Game) public games;
    mapping(uint256 => Bet) public bets;
    mapping(address => uint256[]) public userBets;
    mapping(string => uint256[]) public gameBets;

    // Events
    event GameCreated(
        string indexed gameId,
        string team0,
        string team1,
        uint256 gameDate,
        uint256 team0WinProbability
    );

    event BetPlaced(
        uint256 indexed betId,
        string indexed gameId,
        address indexed bettor,
        string team,
        uint256 amount,
        uint256 odds
    );

    event GameResolved(
        string indexed gameId,
        string winner
    );

    event BetResolved(
        uint256 indexed betId,
        address indexed bettor,
        bool isWon,
        uint256 payout
    );

    event Withdrawal(
        address indexed user,
        uint256 amount
    );

    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Not the owner");
        _;
    }

    modifier validBetAmount(uint256 amount) {
        require(amount >= minBetAmount, "Bet amount too low");
        require(amount <= maxBetAmount, "Bet amount too high");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    /**
     * @dev Create a new game with predictions
     * @param gameId Unique game identifier
     * @param team0 Name of team 0
     * @param team1 Name of team 1
     * @param gameDate Unix timestamp of game date
     * @param team0WinProbability Probability of team0 winning (0-10000, where 6500 = 65%)
     */
    function createGame(
        string memory gameId,
        string memory team0,
        string memory team1,
        uint256 gameDate,
        uint256 team0WinProbability
    ) public onlyOwner {
        require(bytes(games[gameId].gameId).length == 0, "Game already exists");
        require(team0WinProbability <= 10000, "Invalid probability");

        games[gameId] = Game({
            gameId: gameId,
            team0: team0,
            team1: team1,
            gameDate: gameDate,
            isResolved: false,
            winner: "",
            team0WinProbability: team0WinProbability
        });

        emit GameCreated(gameId, team0, team1, gameDate, team0WinProbability);
    }

    /**
     * @dev Place a bet on a game
     * @param gameId Game identifier
     * @param team Team to bet on ("TEAM0" or "TEAM1")
     */
    function placeBet(
        string memory gameId,
        string memory team
    ) public payable validBetAmount(msg.value) {
        Game memory game = games[gameId];
        require(bytes(game.gameId).length > 0, "Game does not exist");
        require(!game.isResolved, "Game already resolved");
        require(
            keccak256(bytes(team)) == keccak256(bytes("TEAM0")) ||
            keccak256(bytes(team)) == keccak256(bytes("TEAM1")),
            "Invalid team"
        );

        // Calculate odds based on probability
        uint256 odds;
        if (keccak256(bytes(team)) == keccak256(bytes("TEAM0"))) {
            // Odds = 1 / probability (with house edge)
            odds = (10000 * 10000) / (game.team0WinProbability + houseEdge);
        } else {
            uint256 team1Prob = 10000 - game.team0WinProbability;
            odds = (10000 * 10000) / (team1Prob + houseEdge);
        }

        // Create bet
        uint256 betId = totalBets++;
        bets[betId] = Bet({
            betId: betId,
            gameId: gameId,
            bettor: msg.sender,
            team: team,
            amount: msg.value,
            odds: odds,
            timestamp: block.timestamp,
            isResolved: false,
            isWon: false,
            payout: 0
        });

        userBets[msg.sender].push(betId);
        gameBets[gameId].push(betId);
        contractBalance += msg.value;

        emit BetPlaced(betId, gameId, msg.sender, team, msg.value, odds);
    }

    /**
     * @dev Resolve a game and calculate payouts
     * @param gameId Game identifier
     * @param winner Winning team ("TEAM0" or "TEAM1")
     */
    function resolveGame(
        string memory gameId,
        string memory winner
    ) public onlyOwner {
        Game storage game = games[gameId];
        require(bytes(game.gameId).length > 0, "Game does not exist");
        require(!game.isResolved, "Game already resolved");
        require(
            keccak256(bytes(winner)) == keccak256(bytes("TEAM0")) ||
            keccak256(bytes(winner)) == keccak256(bytes("TEAM1")),
            "Invalid winner"
        );

        game.isResolved = true;
        game.winner = winner;

        // Resolve all bets for this game
        uint256[] memory betIds = gameBets[gameId];
        for (uint256 i = 0; i < betIds.length; i++) {
            Bet storage bet = bets[betIds[i]];
            if (!bet.isResolved) {
                bool isWon = keccak256(bytes(bet.team)) == keccak256(bytes(winner));
                bet.isResolved = true;
                bet.isWon = isWon;

                if (isWon) {
                    // Calculate payout: amount * (odds / 10000)
                    bet.payout = (bet.amount * bet.odds) / 10000;
                    contractBalance -= bet.payout;
                    payable(bet.bettor).transfer(bet.payout);
                }

                emit BetResolved(bet.betId, bet.bettor, isWon, bet.payout);
            }
        }

        emit GameResolved(gameId, winner);
    }

    /**
     * @dev Get bet details
     * @param betId Bet identifier
     */
    function getBet(uint256 betId) public view returns (Bet memory) {
        return bets[betId];
    }

    /**
     * @dev Get all bets for a user
     * @param user User address
     */
    function getUserBets(address user) public view returns (uint256[] memory) {
        return userBets[user];
    }

    /**
     * @dev Get all bets for a game
     * @param gameId Game identifier
     */
    function getGameBets(string memory gameId) public view returns (uint256[] memory) {
        return gameBets[gameId];
    }

    /**
     * @dev Get game details
     * @param gameId Game identifier
     */
    function getGame(string memory gameId) public view returns (Game memory) {
        return games[gameId];
    }

    /**
     * @dev Update minimum bet amount
     */
    function setMinBetAmount(uint256 _minBetAmount) public onlyOwner {
        minBetAmount = _minBetAmount;
    }

    /**
     * @dev Update maximum bet amount
     */
    function setMaxBetAmount(uint256 _maxBetAmount) public onlyOwner {
        maxBetAmount = _maxBetAmount;
    }

    /**
     * @dev Update house edge (in basis points, e.g., 500 = 5%)
     */
    function setHouseEdge(uint256 _houseEdge) public onlyOwner {
        require(_houseEdge <= 1000, "House edge too high"); // Max 10%
        houseEdge = _houseEdge;
    }

    /**
     * @dev Withdraw contract balance (owner only)
     */
    function withdraw(uint256 amount) public onlyOwner {
        require(amount <= contractBalance, "Insufficient balance");
        contractBalance -= amount;
        payable(owner).transfer(amount);
        emit Withdrawal(owner, amount);
    }

    /**
     * @dev Deposit funds to contract
     */
    function deposit() public payable {
        contractBalance += msg.value;
    }

    /**
     * @dev Get contract balance
     */
    function getContractBalance() public view returns (uint256) {
        return contractBalance;
    }

    // Fallback function to receive ETH
    receive() external payable {
        deposit();
    }
}

