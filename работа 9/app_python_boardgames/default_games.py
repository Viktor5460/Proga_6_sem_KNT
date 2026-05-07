import csv
from io import StringIO
from typing import List

from boardgame_lib import BoardGame, GameDatabase


# CSV-данные, перенесённые из main.cpp (топ-50 игр BGG).
# Формат полей:
# 0: Название
# 1: Описание
# 2: Мин. игроков
# 3: Макс. игроков
# 4: Год издания
# 5: Сложность
# 6: Мин. длительность
# 7: Макс. длительность
# 8: Тип игры
# 9: Жанр
# 10: Механики
# 11: Материал
# 12: Тема
# 13: Дизайн
# 14: Стиль
# 15: Качество

CSV_DATA = r"""
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
"""


def load_default_games(db: GameDatabase) -> List[str]:
    """Загрузить игры из CSV в переданную базу данных.

    Возвращает список названий успешно добавленных игр.
    """
    reader = csv.reader(StringIO(CSV_DATA.strip(), newline=""), delimiter=",", quotechar='"')
    added_names: List[str] = []

    for fields in reader:
        if len(fields) < 16:
            continue

        name = fields[0]
        desc = fields[1]
        try:
            min_players = int(fields[2])
            max_players = int(fields[3])
        except ValueError:
            min_players, max_players = 1, 4

        game = BoardGame.create(name, desc, min_players, max_players, "")

        # год издания
        year = fields[4]
        if year:
            game.add_feature("ГодИздания", year)

        complexity = fields[5]
        if complexity:
            game.set_complexity(complexity)

        min_dur = fields[6]
        max_dur = fields[7]
        if min_dur and max_dur:
            try:
                avg = (int(min_dur) + int(max_dur)) // 2
                game.set_duration(avg)
            except ValueError:
                pass
        elif min_dur:
            try:
                game.set_duration(int(min_dur))
            except ValueError:
                pass

        if fields[8]:
            game.set_game_type(fields[8])
        if fields[9]:
            game.set_genre(fields[9])
        if fields[10]:
            game.set_mechanics(fields[10])
        if fields[11]:
            game.add_feature("Материал", fields[11])
        if fields[12]:
            game.add_feature("Тема", fields[12])
        if fields[13]:
            game.add_feature("Дизайн", fields[13])
        if fields[14]:
            game.add_feature("Стиль", fields[14])
        if fields[15]:
            game.add_feature("Качество", fields[15])

        if db.add_game(game):
            added_names.append(name)

    return added_names



