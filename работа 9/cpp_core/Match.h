#ifndef MATCH_H
#define MATCH_H

#include <string>
#include <map>
#include <iostream>

class Match {
private:
    std::string matchId; // уникальный ID партии
    std::string gameName; // название игры
    std::string date; // дата проведения (YYYY-MM-DD)
    std::map<std::string, double> playerResults; // результаты игроков
    
public:
    Match();
    Match(const std::string& matchId, const std::string& gameName, const std::string& date);
    ~Match();
    
    std::string getMatchId() const;
    std::string getGameName() const;
    std::string getDate() const;
    const std::map<std::string, double>& getPlayerResults() const;
    int getPlayerCount() const;
    
    bool addPlayerResult(const std::string& playerId, double result);
    double getPlayerResult(const std::string& playerId) const;
    bool hasPlayer(const std::string& playerId) const;
    std::string getWinner() const; // игрок с максимальным результатом
    
    bool operator<(const Match& other) const; // сравнение по дате
    friend std::ostream& operator<<(std::ostream& os, const Match& match);
    
    void printInfo() const;
    static void runTests();
};

#endif

