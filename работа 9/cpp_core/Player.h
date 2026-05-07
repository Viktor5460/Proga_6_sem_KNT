#ifndef PLAYER_H
#define PLAYER_H

#include <string>
#include <vector>
#include <iostream>

class Player {
private:
    std::string playerId; // уникальный идентификатор
    std::string name; // имя игрока
    std::vector<std::string> matchHistory; // история партий

public:
    Player();
    Player(const std::string& playerId, const std::string& name = "");
    ~Player();
    
    std::string getPlayerId() const;
    std::string getName() const;
    const std::vector<std::string>& getMatchHistory() const;
    
    void setName(const std::string& name);
    void addMatchToHistory(const std::string& matchId);
    double calculateRatingInGame(const std::vector<double>& results) const; // средний результат
    
    bool operator==(const Player& other) const; // сравнение по ID
    friend std::ostream& operator<<(std::ostream& os, const Player& player);
    
    void printInfo() const;
    static void runTests();
};

#endif

