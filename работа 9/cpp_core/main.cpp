#include "BoardGame.h"
#include "Player.h"
#include "Match.h"
#include "RatingFilter.h"
#include "FeatureFilter.h"
#include "SimilarGamesFilter.h"  // Нужно для тестов
#include "GameDatabase.h"
#include "GameRecommendationEngine.h"
#include <iostream>
#include <vector>
#include <algorithm>
#include <iomanip>
#include <sstream>

// Функция для загрузки игр из CSV данных
void loadGamesFromCSV(GameDatabase& db) {
    std::cout << "\n=== ЗАГРУЗКА ИГР ИЗ CSV ДАННЫХ ===" << std::endl;
    
    // CSV данные игр (топ 50 по BGG)
    std::string csvData = R"(
Brass: Birmingham,"Build networks, grow industries, and navigate the world of the Industrial Revolution.",2,4,2018,8,60,120,Евро игра,Экономическая,"Маркетплейс, Размещение тайлов, Построение сети, Управление ресурсами",Картон,Промышленная/Индустрия,Классический,Стратегический,Высокое качество
Pandemic Legacy: Season 1,"Mutating diseases are spreading around the world - can your team save humanity?",2,4,2015,6,60,90,Кооперативная,Стратегия,"Кооперация, Управление рукой, Развитие сюжета, Кампания",Картон,Современный мир/Эпидемия,Тематический,Наративный,Хорошее
Ark Nova,"Plan and build a modern, scientifically managed zoo to support conservation projects.",1,4,2021,8,90,150,Евро игра,Стратегия,"Размещение, Карточки проектов, Управление ресурсами, Сетап полей",Картон,Зоопарк/Консервация,Современный,Стратегический,Высокое качество
Gloomhaven,"Vanquish monsters with strategic cardplay. Fulfill your quest to leave your legacy!",1,4,2017,8,60,120,Кооперативная,Приключения,"Кампейн, Колода действий, Ролевая прокачка, Управление ресурсами",Картон/Пластик,Фэнтези/Подземелья,Тёмный/гранж,Кооперативный,Премиум
Twilight Imperium: Fourth Edition,"Build an intergalactic empire through trade, research, conquest and grand politics.",3,6,2017,9,240,480,Смешанная,Стратегия,"Контроль территорий, Политика, Торговля, Война",Картон/Пластик,Космос/Галактика,Эпический/мифический,Епический,Премиум
Dune: Imperium,"Influence, intrigue, and combat in the universe of Dune.",1,4,2020,6,60,120,Смешанная,Стратегия,"Декбилдинг, Управление ресурсами, Тайловая сетка, Влияние",Картон/Пластик,Космос/Дюна,Стильный,Темы по лицензии,Хорошее
Terraforming Mars,"Compete with rival CEOs to make Mars habitable and build your corporate empire.",1,5,2016,7,90,150,Евро игра,Экономическая,"Карточки, Пул ресурсов, Управление таймингом, Планирование",Картон,Космос/Колонизация Марса,Техно-реалистичный,Стратегический,Хорошее
War of the Ring: Second Edition,"The Fellowship and the Free Peoples clash with Sauron over the fate of Middle-earth.",2,4,2011,7,120,480,Смешанная,Тематическая,"Асимметрия сторон, Большая карта, Тактика и стратегия",Картон/Пластик,Фэнтези/Средиземье,Эпический,Тематический,Премиум
Dune: Imperium – Uprising,"Deploy agents, build your deck, and engage in strategic battles to control Arrakis.",1,4,2023,7,60,90,Смешанная,Стратегия,"Декбилдинг, Контроль областей, Управление ресурсами",Картон,Космос/Дюна,Модерн-минимал,Стратегический,Хорошее
Star Wars: Rebellion,"Strike from your hidden base as the Rebels—or find and destroy it as the Empire.",2,4,2016,8,180,240,Смешанная,Тематическая,"Скрытая информация, Асимметрия, Кампания, Контроль карты",Картон/Пластик,Космос/Звёздные войны,Киновизуальный,Тематический,Премиум
Spirit Island,"Island Spirits join forces using月球 powers to defend their home from invaders.",1,4,2017,8,90,120,Кооперативная,Стратегия,"Кооперация, Асимметрия, Контроль территорий, Развитие умений",Картон,Природа/Духи,Артистичный,Тематический,Хорошее
Gloomhaven: Jaws of the Lion,"Vitamin monsters with strategic cardplay in a 25-scenario Gloomhaven campaign.",1,4,2020,6,45,120,Кооперативная,Приключения,"Кампейн, Колода действий, Ролевая прокачка",Картон,Фэнтези/Подземелья,Упрощённый,Кооперативный,Хорошее
Gaia Project,"Expand, research, upgrade, and settle the galaxy with one of 14 alien species.",1,4,2017,8,60,150,Евро игра,Стратегия,"Размещение тайлов, Построение сетей, Постоянное развитие",Картон,Космос/Колонизация,Научно-фантастический,Стратегический,Премиум
Twilight Struggle,"Relive the Cold War and rewrite history in an epic clash between the USA and USSR.",2,2,2005,8,120,240,Соревновательная,Стратегия,"Карточная игра, Конфликты, Управление влиянием, Историческая тематика",Картон,Холодная война/Политика,Классический,Стратегический,Хорошее
Through the Ages: A New Story of Civilization,"Forge your own path through history as you draft a civilization for the ages.",2,4,2015,8,120,240,Евро игра,Стратегия,"Драфт карт, Управление ресурсами, Развитие цивилизации",Картон,История/Цивилизация,Классический,Глубокий,Премиум
The Castles of Burgundy,"Plan, trade, and build your Burgundian estate to prosperity and prominence.",2,4,2011,6,60,120,Евро игра,Стратегия,"Размещение тайлов, Планирование, Управление ресурсами",Картон,Средневековье/Аграрная,Классический,Стратегический,Хорошее
Great Western Trail,"Use strategic outposts and navigate danger as you herd your cattle to Kansas City.",2,4,2016,8,75,150,Евро игра,Стратегия,"Маршрут, Управление картами, Оптимизация действий",Картон,Дикий запад/Транспорт,Вестерн-стиль,Стратегический,Хорошее
Eclipse: Second Dawn for the Galaxy,"Build an interstellar civilization by exploration, research, conquest, and diplomacy.",2,6,2020,8,120,240,Евро игра,Стратегия,"Исследование, Боевая система, Развитие технологий",Картон/Пластик,Космос/Империи,Научно-фантастический,Эпический,Премиум
Brass: Lancashire,"Test your economic mettle as you build and network in the Industrial Revolution.",2,4,2007,8,60,120,Евро игра,Экономическая,"Построение сети, Управление ресурсами, Тайлы",Картон,Промышленная/Индустрия,Классический,Стратегический,Хорошее
Frosthaven,"Adventure in the frozen north and build up your outpost throughout an epic campaign.",1,4,2022,9,60,180,Кооперативная,Приключения,"Кампейн, Тактические бои, Прокачка персонажей",Картон/Пластик,Фэнтези/Север,Эпический,Кампейновый,Премиум
7 Wonders Duel,"Science? Military? What will you draft to win this head-to-head version of 7 Wonders?",2,2,2015,4,15,30,Евро игра,Стратегия,"Драфт, Коллекция сетов, Контроль ресурсов",Картон,Античность/Архитектура,Минималистичный,Дуэльный,Хорошее
Scythe,"Five factions vie for dominance in a war-torn, mech-filled, dieselpunk 1920s Europe.",1,5,2016,8,90,150,Евро игра,Стратегия,"Управление ресурсами, Управление работниками, Контроль территорий",Картон/Пластик,Альтернативное прошлое/Дизельпанк,Артистичный,Стратегический,Премиум
Nemesis,"Survive an alien-infested spaceship, but beware of other players and their agendas!",1,5,2018,6,90,180,Смешанная,Ужасы,"Скрытые роли, Симуляция, Тактические бои, Выживание",Картон/Пластик,Космический ужас,Гранж/хоррор,Тематический,Хорошее
Clank! Legacy: Acquisitions Incorporated,"'Go forth, be bold, and ACQUIRE!' in this campaign version of 'Clank!'",2,4,2019,6,60,120,Смешанная,Приключения,"Декбилдинг, Кампания, Управление рукою",Картон,Фэнтези/Приключения,Комичный/легкий,Кампейновый,Хорошее
A Feast for Odin,"Puzzle together the life of a Viking village as you hunt, farm, craft, and explore.",1,4,2016,8,60,180,Евро игра,Стратегия,"Расположение плит, Управление ресурсами, Мозаика",Картон,Викинги/Средневековье,Нордический,Глубокий,Премиум
Concordia,"Merchants build and trade throughout the Roman Empire to please the Gods.",2,5,2013,6,90,120,Евро игра,Стратегия,"Карточный драфт, Торговля, Передвижение по карте",Картон,Римская империя/Торговля,Классический,Стратегический,Хорошее
Great Western Trail: Second Edition,"Wrangle your herd of cows across the Midwest prairie and deliver it to Kansas City.",1,4,2021,8,90,150,Евро игра,Стратегия,"Маршрут, Оптимизация, Управление картами",Картон,Дикий запад/Транспорт,Модернизированный,Стратегический,Хорошее
Lost Ruins of Arnak,"Explore an island to find resources and discover the lost ruins of Arnak.",1,4,2020,6,60,120,Смешанная,Приключения,"Декбилдинг, Разведка, Управление ресурсами",Картон,Приключения/Остров,Археологический,Исследовательский,Хорошее
Arkham Horror: The Card Game,"Investigate the horrors of Arkham while courting cosmic doom.",1,2,2016,6,60,120,Кооперативная,Картовая,"Кампейн, Декбилдинг/Колода, Исследование",Картон,Хоррор/Лавкрафт,Мрачный,Наративный,Хорошее
SETI: Search for Extraterrestrial Intelligence,"Search for signs of alien life by launching probes and analyzing distant signals.",1,4,2024,6,60,120,Евро игра,Научная,"Управление ресурсами, Дорожки развития, Планирование",Картон,Космос/Научная,Современный,Научный,Стандарт
Slay the Spire: The Board Game,"Craft a unique deck, discover powerful relics, and Slay the Spire together!",1,4,2024,6,60,120,Смешанная,Декбилдинг,"Декбилдинг, Кампания, Тактические бои",Картон,Фэнтези/Башня,Аркадный,Кооперативный/Соло,Стандарт
The Lord of the Rings: Duel for Middle-earth,"Play as the Fellowship or Sauron and attempt to determine the fate of Middle-earth.",1,2,2024,6,30,75,Соревновательная,Тематическая,"Асимметрия, Карточная механика, Тактический дуэль",Картон,Фэнтези/Средиземье,Киновизуальный,Дуэльный,Стандарт
Root,"Decide the fate of the forest as woodland factions fight for contrasting goals.",2,4,2018,8,60,120,Смешанная,Асимметричная,"Асимметричные фракции, Контроль территорий, Управление картой",Картон,Фэнтези/Лес,Иллюстративный,Асимметричный,Хорошее
Sky Team,"Work together silently to land a plane under increasingly challenging circumstances.",3,8,2023,4,20,40,Парти игра,Кооперативная,"Коммуникация, Симуляция, Командная работа",Картон,Современный/Авиасимуляция,Минималистичный,Парти,Стандарт
Too Many Bones,"Toss gobs of unique dice in an epic adventure en route to a final boss showdown.",1,4,2017,8,60,240,Кооперативная,Тактическая,"Кубическая механика, Тактические бои, Сбор экипировки",Пластик,Фэнтези/Приключения,Настольный RPG-стиль,Тематический,Премиум
Terra Mystica,"Play fantastical factions. Expand your influence by terraforming and joining cults.",2,5,2012,8,60,150,Евро игра,Стратегия,"Размещение тайлов, Управление территорией, Адаптация",Картон,Фэнтези/Магия,Минималистичный,Глубокий,Хорошее
Orléans,"Craftsmen, scholars & monks can help you reign supreme—but who will turn up to help?",2,4,2014,6,60,120,Евро игра,Стратегия,"Билеты/мешок, Управление ресурсами, Планирование",Картон,Средневековье/Торговля,Средневековый,Стратегический,Хорошее
Wingspan,"Attract a beautiful and diverse collection of birds to your wildlife preserve.",1,5,2019,4,40,70,Семейная,Симуляция,"Коллекция наборов, Управление ресурсами, Драфт",Картон,Природа/Птицы,Иллюстративный,Спокойный,Хорошее
Barrage,"Nations vie for hydroelectric dominance in a dystopia where water is power.",1,4,2019,8,90,150,Евро игра,Экономическая,"Построение сети, Тайлы, Управление водой",Картон,Индустриальный/Гидроэнергетика,Тёмный,Технический,Премиум
Mage Knight Board Game,"Build your hero's spells, abilities, and artifacts as you explore & conquer cities.",1,5,2011,9,120,240,Смешанная,Ролевой,"Соло/Кооперация, Прокачка персонажа, Управление колодой",Картон/Пластик,Фэнтези/Путешествие,Эпический,Сложный,Премиум
Everdell,"Gather resources to develop a harmonious village of woodland critters and structures.",1,4,2018,6,40,80,Евро игра,Семейная,"Механика размещения рабочих, Коллекция карт, Управление ресурсами",Картон,Фэнтези/Природа,Иллюстративный,Семейный,Хорошее
Viticulture Essential Edition,"Create the most prosperous winery in Italy from the Tuscan vineyard you've inherited.",1,6,2015,6,60,120,Евро игра,Стратегия,"Размещение рабочих, Управление временем/сезонами, Производство",Картон,Аграрная/Виноделие,Тёплый/художественный,Семейный/Стратегический,Хорошее
The Crew: Mission Deep Sea,"Explore the deep sea, outwit fate, and discover the mythic land of Mu!",2,5,2021,4,20,40,Кооперативная,Трик,"Триковая механика, Кооперация, Обмен информацией",Картон,Космос/Исследования,Минималистичный,Парти/Кооператив,Стандарт
Hegemony: Lead Your Class to Victory,"Simulate a whole contemporary nation in this asymmetric, politico-economic euro-game.",1,4,2023,8,120,240,Евро игра,Политическая,"Асимметрия, Управление политикой, Экономическое планирование",Картон,Современный/Политика,Серьёзный,Симулятивный,Стандарт
Heat: Pedal to the Metal,"Push your car to the limit in the pursuit of victory, but don't overheat!",1,6,2022,6,45,120,Соревновательная,Гоночная,"Управление радиатором, Тактическое движение, Ситуационная скорость",Картон/Пластик,Гонки/Автоспорт,Реалистичный,Тематический,Хорошее
Marvel Champions: The Card Game,"Battle Marvel villains with unique teams of iconic heroes in this LCG.",1,4,2019,6,45,90,Кооперативная,Картовая,"Колода героев, Соло/Кооперация, Модульные злодеи",Картон,Современный/Супергерои,Комикс-стиль,Кооперативный,Хорошее
Crokinole,"Flick discs and make trick shots in this traditional Canadian dexterity game!",2,4,1876,4,15,45,Абстрактная,Декстрити,"Декстрити, Меткость, Тактичесное размещение",Дерево,Ретро/Классика,Ремесленный,Партия,Высокое
Kanban EV,"EV-factory workers optimize and innovate to stand out at the big board meeting.",1,4,2020,8,90,150,Евро игра,Стратегия,"Управление производством, Плагины/улучшения, Тайловая оптимизация",Картон,Современная промышленность,Индустриальный,Стратегический,Хорошее
Food Chain Magnate,"Strategically hire and manage your workforce to outcompete rival fast food chains.",2,5,2015,8,120,240,Евро игра,Экономическая,"Стратегия найма, Маркетинг, Управление цепочкой поставок",Картон,Современный/Бизнес,Реалистичный,Глубокий,Премиум
Underwater Cities,"Develop future cities on the seafloor through politics, production, and science.",1,4,2018,8,60,120,Евро игра,Стратегия,"Сеть построек, Управление ресурсами, Карты проектов",Картон,Научная/Будущее,Современный,Стратегический,Хорошее
)";
    
    std::stringstream ss(csvData);
    std::string line;
    int gameCount = 0;
    
    // Пропускаем заголовок
    std::getline(ss, line);
    
    while (std::getline(ss, line)) {
        if (line.empty()) continue;
        
        std::vector<std::string> fields;
        std::stringstream lineStream(line);
        std::string field;
        bool inQuotes = false;
        std::string currentField = "";
        
        // Парсинг CSV с учетом кавычек
        for (char c : line) {
            if (c == '"') {
                inQuotes = !inQuotes;
            } else if (c == ',' && !inQuotes) {
                fields.push_back(currentField);
                currentField = "";
            } else {
                currentField += c;
            }
        }
        fields.push_back(currentField); // Последнее поле
        
        if (fields.size() >= 16) {
            // Создаем игру
            BoardGame* game = new BoardGame(
                fields[0],  // Название
                fields[1],  // Описание
                std::stoi(fields[2]),  // МинИгроков
                std::stoi(fields[3]),  // МаксИгроков
                ""  // Издание - не указано в CSV
            );
            
            // Устанавливаем параметры
            // fields[4] это год издания, сохраняем как feature
            if (!fields[4].empty()) {
                game->addFeature("ГодИздания", fields[4]);
            }
            if (!fields[5].empty()) {
                game->setComplexity(fields[5]);
            }
            if (!fields[6].empty() && !fields[7].empty()) {
                game->setDurationRange(std::stoi(fields[6]), std::stoi(fields[7]));
            } else if (!fields[6].empty()) {
                // Если есть только минимальная длительность, устанавливаем её как среднюю
                int duration = std::stoi(fields[6]);
                game->setDuration(duration);
            }
            if (!fields[8].empty()) {
                game->addFeature("ТипИгры", fields[8]);
            }
            if (!fields[9].empty()) {
                game->addFeature("Жанр", fields[9]);
            }
            if (!fields[10].empty()) {
                game->addFeature("Механики", fields[10]);
            }
            if (!fields[11].empty()) {
                game->addFeature("Материал", fields[11]);
            }
            if (!fields[12].empty()) {
                game->addFeature("Тема", fields[12]);
            }
            if (!fields[13].empty()) {
                game->addFeature("Дизайн", fields[13]);
            }
            if (!fields[14].empty()) {
                game->addFeature("Стиль", fields[14]);
            }
            if (!fields[15].empty()) {
                game->addFeature("Качество", fields[15]);
            }
            
            // Добавляем в базу данных
            if (db.addGame(game)) {
                gameCount++;
                std::cout << "✓ Добавлена игра: " << fields[0] << std::endl;
            } else {
                std::cout << "✗ Ошибка добавления игры: " << fields[0] << std::endl;
                delete game;
            }
        }
    }
    
    std::cout << "\n=== ЗАГРУЖЕНО " << gameCount << " ИГР ===" << std::endl;
}

int main() {
    std::cout << "=====================================================" << std::endl;
    std::cout << "===   ТЕСТИРОВАНИЕ ИЕРАРХИИ КЛАССОВ BOARDGAME    ===" << std::endl;
    std::cout << "=====================================================" << std::endl;
    
    // запуск тестов всех классов
    Player::runTests();
    Match::runTests();
    RatingFilter::runTests();
    FeatureFilter::runTests();
    SimilarGamesFilter::runTests();
    GameDatabase::runTests();
    
    // Тестирование системы рекомендаций
    GameRecommendationEngine::runTests();
    
    std::cout << "\n=====================================================" << std::endl;
    std::cout << "===       ВСЕ ТЕСТЫ УСПЕШНО ЗАВЕРШЕНЫ            ===" << std::endl;
    std::cout << "=====================================================" << std::endl;
    
    std::cout << "\n=== ДЕМОНСТРАЦИЯ РАБОТЫ СИСТЕМЫ ===" << std::endl;
    
    // создаем базу данных и наполняем её
    GameDatabase db;
    
    // Загружаем игры из CSV данных (топ-50 BGG)
    loadGamesFromCSV(db);
    
    // добавляем игроков
    db.addPlayer(new Player("ivan", "Иван"));
    db.addPlayer(new Player("maria", "Мария"));
    db.addPlayer(new Player("petr", "Петр"));
    
    // выставляем оценки для игр из CSV
    db.addRating("Brass: Birmingham", "ivan", 5);
    db.addRating("Brass: Birmingham", "maria", 5);
    db.addRating("Ark Nova", "ivan", 4);
    db.addRating("Ark Nova", "petr", 5);
    db.addRating("Wingspan", "maria", 4);
    db.addRating("Wingspan", "petr", 4);
    db.addRating("Gloomhaven", "ivan", 5);
    db.addRating("Terraforming Mars", "maria", 4);
    
    // добавляем партии для игр из CSV
    Match* m1 = new Match("m1", "Brass: Birmingham", "2024-10-01");
    m1->addPlayerResult("ivan", 1.0);
    m1->addPlayerResult("maria", 0.0);
    db.addMatch(m1);
    
    Match* m2 = new Match("m2", "Ark Nova", "2024-10-05");
    m2->addPlayerResult("ivan", 95.0);
    m2->addPlayerResult("maria", 88.0);
    m2->addPlayerResult("petr", 102.0);
    db.addMatch(m2);
    
    Match* m3 = new Match("m3", "Gloomhaven", "2024-10-03");
    m3->addPlayerResult("ivan", 1.0);
    m3->addPlayerResult("maria", 0.0);
    db.addMatch(m3);
    
    // добавляем схожесть игр из CSV
    db.addSimilarity("Brass: Birmingham", "Brass: Lancashire");
    db.addSimilarity("Dune: Imperium", "Dune: Imperium – Uprising");
    db.addSimilarity("Terraforming Mars", "Eclipse: Second Dawn for the Galaxy");
    
    db.printStatistics();
    
    // демонстрация фильтров
    std::cout << "\n--- Поиск игр с рейтингом >= 4.5 ---" << std::endl;
    RatingFilter highRating(4.5);
    std::vector<BoardGame*> highRatedGames = db.findGames(&highRating);
    for (BoardGame* game : highRatedGames) {
        std::cout << game->getName() << " (рейтинг: " << game->getAverageRating() << ")" << std::endl;
    }
    
    std::cout << "\n--- Поиск стратегических игр ---" << std::endl;
    std::map<std::string, std::string> strategyFeature;
    strategyFeature["Жанр"] = "Стратегия";
    FeatureFilter strategyFilter(strategyFeature);
    std::vector<BoardGame*> strategyGames = db.findGames(&strategyFilter);
    for (BoardGame* game : strategyGames) {
        std::cout << game->getName() << std::endl;
    }
    
    std::cout << "\n--- Игры, похожие на Brass: Birmingham (автоматическая система) ---" << std::endl;
    auto similarGamesRecs = db.getRecommendations("Brass: Birmingham", 10);
    for (const auto& rec : similarGamesRecs) {
        std::cout << rec.gameName << " (схожесть: " << std::fixed << std::setprecision(1) 
                  << (rec.similarityScore * 100) << "%)" << std::endl;
    }
    
    std::cout << "\n--- Рейтинг игрока Ivan в Ark Nova ---" << std::endl;
    double rating = db.getPlayerRatingInGame("ivan", "Ark Nova");
    std::cout << "Рейтинг: " << rating << std::endl;
    
    // === ДЕМОНСТРАЦИЯ СИСТЕМЫ РЕКОМЕНДАЦИЙ С ЗАГРУЖЕННЫМИ ИГРАМИ ===
    
    std::cout << "\n--- Система автоматических рекомендаций ---" << std::endl;
    
    // Получаем рекомендации для Brass: Birmingham (топ-1 BGG)
    auto brassRecs = db.getRecommendations("Brass: Birmingham", 5);
    std::cout << "Рекомендации для игры 'Brass: Birmingham' (№1 BGG):" << std::endl;
    if (!brassRecs.empty()) {
        for (size_t i = 0; i < brassRecs.size(); ++i) {
            const auto& rec = brassRecs[i];
            std::cout << "  " << (i + 1) << ". " << rec.gameName 
                      << " (схожесть: " << std::fixed << std::setprecision(1) 
                      << (rec.similarityScore * 100) << "%)" << std::endl;
        }
    } else {
        std::cout << "  Рекомендации не найдены" << std::endl;
    }
    
    // Получаем рекомендации для Gloomhaven (топ-4 BGG)
    auto gloomhavenRecs = db.getRecommendations("Gloomhaven", 5);
    std::cout << "\nРекомендации для игры 'Gloomhaven' (№4 BGG):" << std::endl;
    if (!gloomhavenRecs.empty()) {
        for (size_t i = 0; i < gloomhavenRecs.size(); ++i) {
            const auto& rec = gloomhavenRecs[i];
            std::cout << "  " << (i + 1) << ". " << rec.gameName 
                      << " (схожесть: " << std::fixed << std::setprecision(1) 
                      << (rec.similarityScore * 100) << "%)" << std::endl;
        }
    } else {
        std::cout << "  Рекомендации не найдены" << std::endl;
    }
    
    // Демонстрация детализированных рекомендаций для Wingspan (семейная игра)
    std::cout << "\n--- Детализированные рекомендации для Wingspan (семейная игра) ---" << std::endl;
    auto detailedRecs = db.getDetailedRecommendations("Wingspan", 4);
    if (!detailedRecs.empty()) {
        for (size_t i = 0; i < detailedRecs.size(); ++i) {
            const auto& rec = detailedRecs[i];
            std::cout << "  " << (i + 1) << ". " << rec.gameName 
                      << " (общая схожесть: " << std::fixed << std::setprecision(1) 
                      << (rec.similarityScore * 100) << "%)" << std::endl;
            
            std::cout << "     Детализация: ";
            bool first = true;
            for (const auto& param : rec.parameterScores) {
                if (!first) std::cout << ", ";
                std::cout << param.first << " (" << std::fixed << std::setprecision(0) 
                          << (param.second * 100) << "%)";
                first = false;
            }
            std::cout << std::endl;
        }
    }
    
    // Поиск игр, похожих на несколько образцов (космические игры)
    std::cout << "\n--- Поиск игр, похожих на Terraforming Mars И Dune: Imperium (космические темы) ---" << std::endl;
    std::vector<std::string> referenceGames = {"Terraforming Mars", "Dune: Imperium"};
    auto multiRecs = db.findGamesSimilarToMultiple(referenceGames, 5);
    if (!multiRecs.empty()) {
        for (size_t i = 0; i < multiRecs.size(); ++i) {
            const auto& rec = multiRecs[i];
            std::cout << "  " << (i + 1) << ". " << rec.gameName 
                      << " (схожесть: " << std::fixed << std::setprecision(1) 
                      << (rec.similarityScore * 100) << "%)" << std::endl;
        }
    } else {
        std::cout << "  Рекомендации не найдены" << std::endl;
    }
    
    // Поиск сложных игр (сложность 8-9)
    std::cout << "\n--- Поиск игр, похожих на Mage Knight (сложные игры) ---" << std::endl;
    auto mageKnightRecs = db.getRecommendations("Mage Knight Board Game", 5);
    if (!mageKnightRecs.empty()) {
        for (size_t i = 0; i < mageKnightRecs.size(); ++i) {
            const auto& rec = mageKnightRecs[i];
            std::cout << "  " << (i + 1) << ". " << rec.gameName 
                      << " (схожесть: " << std::fixed << std::setprecision(1) 
                      << (rec.similarityScore * 100) << "%)" << std::endl;
        }
    }
    
    // Статистика системы рекомендаций
    std::cout << "\n--- Статистика системы рекомендаций ---" << std::endl;
    auto recStats = db.getRecommendationStats();
    std::cout << "Всего игр: " << recStats.totalGames << std::endl;
    std::cout << "Игр с рекомендациями: " << recStats.gamesWithRecommendations << std::endl;
    std::cout << "Среднее количество рекомендаций на игру: " 
              << std::fixed << std::setprecision(1) << recStats.averageRecommendationsPerGame << std::endl;
    std::cout << "Средняя схожесть рекомендаций: " 
              << std::fixed << std::setprecision(1) << (recStats.averageSimilarityScore * 100) << "%" << std::endl;
    
    // Демонстрация работы с темами
    std::cout << "\n--- Демонстрация работы с темами ---" << std::endl;
    
    // Показываем игры с космической тематикой
    std::cout << "Игры с космической тематикой:" << std::endl;
    auto allGames = db.getAllGames();
    int spaceCount = 0;
    for (const auto& pair : allGames) {
        BoardGame* game = pair.second;
        if (game->hasFeature("Тема")) {
            std::string theme = game->getFeature("Тема");
            if (theme.find("Космос") != std::string::npos || 
                theme.find("Галактика") != std::string::npos ||
                theme.find("Марс") != std::string::npos ||
                theme.find("Дюна") != std::string::npos) {
                std::cout << "  " << (spaceCount + 1) << ". " << game->getName();
                
                // Добавляем сложность
                std::string complexity = game->getComplexity();
                if (!complexity.empty()) {
                    std::cout << " (сложность: " << complexity << "/10)";
                }
                
                // Добавляем длительность
                int duration = game->getDuration();
                if (duration > 0) {
                    std::cout << " [длительность: " << duration << " мин]";
                }
                
                std::cout << std::endl;
                spaceCount++;
            }
        }
    }
    std::cout << "Всего космических игр: " << spaceCount << std::endl;
    
    // Показываем игры с фэнтези тематикой
    std::cout << "\nИгры с фэнтези тематикой:" << std::endl;
    int fantasyCount = 0;
    for (const auto& pair : allGames) {
        BoardGame* game = pair.second;
        if (game->hasFeature("Тема")) {
            std::string theme = game->getFeature("Тема");
            if (theme.find("Фэнтези") != std::string::npos || 
                theme.find("Средиземье") != std::string::npos ||
                theme.find("Подземелья") != std::string::npos ||
                theme.find("Север") != std::string::npos) {
                std::cout << "  " << (fantasyCount + 1) << ". " << game->getName();
                
                // Добавляем сложность
                std::string complexity = game->getComplexity();
                if (!complexity.empty()) {
                    std::cout << " (сложность: " << complexity << "/10)";
                }
                
                // Добавляем длительность
                int duration = game->getDuration();
                if (duration > 0) {
                    std::cout << " [длительность: " << duration << " мин]";
                }
                
                std::cout << std::endl;
                fantasyCount++;
            }
        }
    }
    std::cout << "Всего фэнтези игр: " << fantasyCount << std::endl;
    
    // Показываем евро игры
    std::cout << "\nЕвро игры (с информацией о сложности):" << std::endl;
    int euroCount = 0;
    int euroWithComplexity = 0;
    for (const auto& pair : allGames) {
        BoardGame* game = pair.second;
        if (game->getGameType() == "Евро игра") {
            std::string complexity = game->getComplexity();
            std::cout << "  " << (euroCount + 1) << ". " << game->getName();
            
            if (!complexity.empty()) {
                std::cout << " (сложность: " << complexity << "/10)";
                euroWithComplexity++;
            } else {
                std::cout << " (сложность: не указана)";
            }
            
            // Добавляем информацию о рейтинге
            double avgRating = game->getAverageRating();
            if (avgRating > 0) {
                std::cout << " [рейтинг: " << std::fixed << std::setprecision(1) << avgRating << "]";
            }
            
            std::cout << std::endl;
            euroCount++;
        }
    }
    std::cout << "Всего евро игр: " << euroCount << " (из них с указанной сложностью: " << euroWithComplexity << ")" << std::endl;
    
    // Показываем кооперативные игры
    std::cout << "\nКооперативные игры (с информацией о сложности):" << std::endl;
    int coopCount = 0;
    int coopWithComplexity = 0;
    for (const auto& pair : allGames) {
        BoardGame* game = pair.second;
        std::string gameType = game->getGameType();
        if (gameType.find("Кооперативная") != std::string::npos) {
            std::string complexity = game->getComplexity();
            std::cout << "  " << (coopCount + 1) << ". " << game->getName();
            
            if (!complexity.empty()) {
                std::cout << " (сложность: " << complexity << "/10)";
                coopWithComplexity++;
            } else {
                std::cout << " (сложность: не указана)";
            }
            
            // Добавляем информацию о рейтинге
            double avgRating = game->getAverageRating();
            if (avgRating > 0) {
                std::cout << " [рейтинг: " << std::fixed << std::setprecision(1) << avgRating << "]";
            }
            
            std::cout << std::endl;
            coopCount++;
        }
    }
    std::cout << "Всего кооперативных игр: " << coopCount << " (из них с указанной сложностью: " << coopWithComplexity << ")" << std::endl;
    
    // демонстрация операторов
    std::cout << "\n--- operator bool() для проверки валидности ---" << std::endl;
    BoardGame* validGame = db["Brass: Birmingham"];
    BoardGame* invalidGame = db["НесуществующаяИгра"];
    
    if (validGame && *validGame) {
        std::cout << "✓ Игра 'Brass: Birmingham' валидна и существует" << std::endl;
    }
    if (!invalidGame) {
        std::cout << "✓ Игра 'НесуществующаяИгра' не найдена (operator[] вернул nullptr)" << std::endl;
    }
    
    std::cout << "\n--- operator[] для доступа к играм ---" << std::endl;
    BoardGame* game = db["Ark Nova"];
    if (game) {
        std::cout << "Доступ через operator[]: " << game->getName() 
                  << " (рейтинг: " << game->getAverageRating() << ")" << std::endl;
    }
    
    std::cout << "\n--- Статический метод getTotalGamesCreated() ---" << std::endl;
    std::cout << "Всего игр создано за время работы программы: " 
              << BoardGame::getTotalGamesCreated() << std::endl;
    
    std::cout << "\n--- Перегрузка операторов сравнения ---" << std::endl;
    BoardGame* brassGame = db["Brass: Birmingham"];
    BoardGame* wingspanGame = db["Wingspan"];
    if (brassGame && wingspanGame) {
        if (*brassGame > *wingspanGame) {
            std::cout << "Brass: Birmingham (рейтинг " << brassGame->getAverageRating() 
                      << ") имеет более высокий рейтинг, чем Wingspan (рейтинг " 
                      << wingspanGame->getAverageRating() << ")" << std::endl;
        }
    }
    
    std::cout << "\n=== ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА ===" << std::endl;
    
    return 0;
}
