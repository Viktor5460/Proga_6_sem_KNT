import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import json
import os
import re

from boardgame_lib import BoardGame, GameDatabase, Match

try:
    # Дополнительный виджет календаря, если установлен tkcalendar.
    from tkcalendar import DateEntry  # type: ignore
except Exception:  # pragma: no cover - опциональная зависимость
    DateEntry = None


class LibraryDataError(Exception):
    """
    Исключение для ошибок обработки данных внутри библиотеки.
    
    Используется для демонстрации техники обработки ошибок,
    возникающих при работе с данными в C++ библиотеке через Python-обёртку.
    """
    def __init__(self, message: str, operation: str = "", game_name: str = ""):
        super().__init__(message)
        self.operation = operation  # Название операции, вызвавшей ошибку
        self.game_name = game_name   # Название игры, связанной с ошибкой
        self.message = message
    
    def __str__(self) -> str:
        error_msg = f"Ошибка обработки данных библиотеки: {self.message}"
        if self.operation:
            error_msg += f" (операция: {self.operation})"
        if self.game_name:
            error_msg += f" (игра: {self.game_name})"
        return error_msg


class LibraryNullPointerError(Exception):
    """
    Исключение для ошибок NULL указателей в библиотеке.
    
    Используется для демонстрации техники обработки ошибок NULL указателей,
    возникающих при передаче некорректных параметров в C++ библиотеку.
    """
    def __init__(self, message: str, operation: str = "", parameter: str = ""):
        super().__init__(message)
        self.operation = operation  # Название операции, вызвавшей ошибку
        self.parameter = parameter  # Название параметра, который был NULL
        self.message = message
    
    def __str__(self) -> str:
        error_msg = f"Ошибка NULL указателя в библиотеке: {self.message}"
        if self.operation:
            error_msg += f" (операция: {self.operation})"
        if self.parameter:
            error_msg += f" (параметр: {self.parameter})"
        return error_msg


#
# Простое, но расширяемое GUI-приложение на Tkinter.
# Структура:
# - стартовое окно: выбор "Новая вселенная" / "Открыть вселенную" / "Общая база"
# - главное окно: вкладки "Игры", "Игроки", "Партии", "Рекомендации"
# - кнопка-шестерёнка (настройки) с вкладкой весов рекомендаций.
#


class Universe:
    """Python-представление вселенной для сохранения/загрузки."""

    def __init__(self, name: str):
        self.name = name
        self.db = GameDatabase()

    def to_dict(self) -> dict:
        # Для простоты сохраняем только имя вселенной.
        # Игры/игроков/матчи можно сериализовать позже при необходимости.
        return {"name": self.name}

    @classmethod
    def from_dict(cls, data: dict) -> "Universe":
        return cls(data.get("name", "Вселенная"))


class SettingsDialog(tk.Toplevel):
    def __init__(self, master, db: GameDatabase):
        super().__init__(master)
        self.title("Настройки")
        self.db = db
        self.geometry("600x700")
        self.resizable(True, True)

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Вкладка "Веса рекомендаций"
        weights_frame = ttk.Frame(notebook)
        notebook.add(weights_frame, text="Веса рекомендаций")

        # Веса в процентах (сумма должна быть 100%)
        # Начальные значения (нормализованные до 100%)
        default_weights = {
            "complexity": 25.0,
            "player_count": 20.0,
            "game_type": 15.0,
            "duration": 15.0,
            "mechanics": 15.0,
            "genre": 10.0,
            "user_params": 5.0,
        }
        # Нормализуем начальные значения
        total = sum(default_weights.values())
        if total > 0:
            for key in default_weights:
                default_weights[key] = (default_weights[key] / total) * 100.0
        
        self.weight_vars = {
            key: tk.DoubleVar(value=default_weights[key]) for key in default_weights
        }
        self.weight_labels = {}  # Для отображения процентов
        self.weight_order = ["complexity", "player_count", "game_type", "duration", "mechanics", "genre", "user_params"]
        
        self.min_threshold_var = tk.DoubleVar(value=0.15)
        self.max_recs_var = tk.IntVar(value=10)
        self.missing_data_penalty_var = tk.DoubleVar(value=0.05)
        
        # Загружаем сохранённые настройки
        self._load_settings()

        # Индикатор суммы
        sum_frame = ttk.Frame(weights_frame)
        sum_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        ttk.Label(sum_frame, text="Сумма весов:", font=("Segoe UI", 10, "bold")).pack(side="left")
        self.sum_label = ttk.Label(sum_frame, text="100.0%", font=("Segoe UI", 10, "bold"), foreground="green")
        self.sum_label.pack(side="left", padx=10)
        self.valid_label = ttk.Label(sum_frame, text="✓ Валидно", font=("Segoe UI", 9), foreground="green")
        self.valid_label.pack(side="left")

        row = 1
        for key, label in [
            ("complexity", "Сложность игры"),
            ("player_count", "Кол-во игроков"),
            ("game_type", "Тип игры"),
            ("duration", "Длительность"),
            ("mechanics", "Механики"),
            ("genre", "Жанр"),
            ("user_params", "Доп. параметры"),
        ]:
            ttk.Label(weights_frame, text=label).grid(row=row, column=0, sticky="w", padx=5, pady=2)
            
            # Используем обычный Scale вместо ttk.Scale для поддержки resolution
            scale = tk.Scale(
                weights_frame,
                from_=0.0,
                to=100.0,
                resolution=0.1,  # Мелкий шаг для плавной нормализации
                orient="horizontal",
                variable=self.weight_vars[key],
                command=lambda v, k=key: self._on_weight_change(k, float(v)),
            )
            scale.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
            
            # Метка с процентом
            percent_label = ttk.Label(weights_frame, text="25.0%", width=8)
            percent_label.grid(row=row, column=2, padx=5, pady=2)
            self.weight_labels[key] = percent_label
            
            row += 1

        weights_frame.columnconfigure(1, weight=1)

        # Минимальный порог схожести
        ttk.Label(weights_frame, text="Мин. порог схожести").grid(
            row=row, column=0, sticky="w", padx=5, pady=2
        )
        ttk.Scale(
            weights_frame,
            from_=0.0,
            to=1.0,
            orient="horizontal",
            variable=self.min_threshold_var,
        ).grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        row += 1

        # Штраф за отсутствие данных
        ttk.Label(weights_frame, text="Штраф за отсутствие данных").grid(
            row=row, column=0, sticky="w", padx=5, pady=2
        )
        ttk.Scale(
            weights_frame,
            from_=0.0,
            to=1.0,
            orient="horizontal",
            variable=self.missing_data_penalty_var,
        ).grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        row += 1

        ttk.Label(weights_frame, text="Максимум рекомендаций").grid(
            row=row, column=0, sticky="w", padx=5, pady=2
        )
        ttk.Spinbox(weights_frame, from_=1, to=50, textvariable=self.max_recs_var).grid(
            row=row, column=1, sticky="w", padx=5, pady=2
        )
        row += 1

        # Вкладка "Дополнительные настройки"
        advanced_frame = ttk.Frame(notebook)
        notebook.add(advanced_frame, text="Дополнительно")

        # Флажки
        self.auto_update_var = tk.BooleanVar(value=True)
        self.use_cache_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(advanced_frame, text="Автообновление рекомендаций", 
                       variable=self.auto_update_var).pack(anchor="w", padx=10, pady=5)
        ttk.Checkbutton(advanced_frame, text="Использовать кэш рекомендаций", 
                       variable=self.use_cache_var).pack(anchor="w", padx=10, pady=5)

        ttk.Button(advanced_frame, text="Очистить кэш рекомендаций", 
                  command=self._clear_cache).pack(padx=10, pady=10)


        # Обновляем отображение процентов
        self._update_percentages()

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Button(btn_frame, text="Сохранить", command=self._apply).pack(
            side="right", padx=5
        )
        ttk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side="right")

    def _normalize_weights(self):
        """Автоматическая нормализация весов до 100%."""
        # Получаем текущие значения
        current_values = {key: self.weight_vars[key].get() for key in self.weight_order}
        
        # Вычисляем сумму
        total = sum(current_values.values())
        
        if total <= 0:
            # Если сумма нулевая или отрицательная, равномерно распределяем
            per_weight = 100.0 / len(self.weight_order)
            for key in self.weight_order:
                self.weight_vars[key].set(per_weight)
        else:
            # Нормализуем до 100%
            for key in self.weight_order:
                normalized = (current_values[key] / total) * 100.0
                self.weight_vars[key].set(normalized)
    
    def _on_weight_change(self, changed_key: str, new_value: float):
        """Обработчик изменения веса - автоматически нормализует остальные веса."""
        # Ограничиваем значение диапазоном 0-100
        new_value = max(0.0, min(100.0, new_value))
        
        # Получаем старое значение
        old_value = self.weight_vars[changed_key].get()
        
        # Если значение не изменилось существенно, просто обновляем отображение
        if abs(new_value - old_value) < 0.01:
            self._update_percentages()
            return
        
        # Устанавливаем новое значение
        self.weight_vars[changed_key].set(new_value)
        
        # Получаем текущую сумму всех весов
        total = sum(self.weight_vars[k].get() for k in self.weight_order)
        
        if abs(total - 100.0) > 0.1:
            # Если сумма не равна 100%, нормализуем все веса
            # Сохраняем пропорции остальных весов
            other_keys = [k for k in self.weight_order if k != changed_key]
            if other_keys:
                other_total = sum(self.weight_vars[k].get() for k in other_keys)
                if other_total > 0:
                    # Вычисляем, сколько осталось для остальных весов
                    remaining = 100.0 - new_value
                    # Распределяем пропорционально текущим значениям
                    for k in other_keys:
                        proportion = self.weight_vars[k].get() / other_total
                        new_val = remaining * proportion
                        self.weight_vars[k].set(max(0.0, new_val))
                else:
                    # Если остальные нули, равномерно распределяем
                    per_weight = (100.0 - new_value) / len(other_keys)
                    for k in other_keys:
                        self.weight_vars[k].set(per_weight)
        
        # Финальная нормализация для точности
        self._normalize_weights()
        self._update_percentages()

    def _update_percentages(self):
        """Обновить отображение процентов и проверить валидность."""
        total = sum(self.weight_vars[k].get() for k in self.weight_order)
        
        # Обновляем метки процентов (показываем с одним знаком после запятой)
        for key, label in self.weight_labels.items():
            value = self.weight_vars[key].get()
            label.config(text=f"{value:.1f}%")
        
        # Обновляем сумму
        self.sum_label.config(text=f"{total:.1f}%")
        
        # Проверка валидности (сумма должна быть близка к 100%)
        if abs(total - 100.0) < 0.1:
            self.sum_label.config(foreground="green")
            self.valid_label.config(text="✓ Валидно", foreground="green")
        else:
            self.sum_label.config(foreground="red")
            self.valid_label.config(text="✗ Невалидно (сумма должна быть 100%)", foreground="red")

    def _clear_cache(self):
        """Очистить кэш рекомендаций."""
        # Нужен метод в C API для очистки кэша
        messagebox.showinfo("Информация", 
                          "Очистка кэша требует добавления метода clearRecommendationsCache в C API.")

    def _load_settings(self):
        """Загрузить сохранённые настройки из файла."""
        settings_file = Path("settings.json")
        if settings_file.exists():
            try:
                with open(settings_file, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                
                # Загружаем веса (нормализуем их до 100%)
                if "weights" in settings:
                    weights = settings["weights"]
                    total = sum(weights.get(key, 0) for key in self.weight_order)
                    if total > 0:
                        for key in self.weight_order:
                            if key in weights:
                                normalized = (weights[key] / total) * 100.0
                                self.weight_vars[key].set(normalized)
                
                # Загружаем другие параметры
                if "min_threshold" in settings:
                    self.min_threshold_var.set(settings["min_threshold"])
                if "max_recs" in settings:
                    self.max_recs_var.set(settings["max_recs"])
                if "missing_data_penalty" in settings:
                    self.missing_data_penalty_var.set(settings["missing_data_penalty"])
                
                # Нормализуем веса после загрузки
                self._normalize_weights()
            except Exception as e:
                # Если ошибка при загрузке, используем значения по умолчанию
                pass
    
    def _save_settings(self):
        """Сохранить текущие настройки в файл."""
        settings_file = Path("settings.json")
        try:
            # Нормализуем веса перед сохранением
            self._normalize_weights()
            
            settings = {
                "weights": {key: self.weight_vars[key].get() for key in self.weight_order},
                "min_threshold": self.min_threshold_var.get(),
                "max_recs": self.max_recs_var.get(),
                "missing_data_penalty": self.missing_data_penalty_var.get(),
            }
            
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            # Игнорируем ошибки сохранения
            pass
    
    def _apply(self):
        """Применить настройки."""
        # Нормализуем веса перед сохранением
        self._normalize_weights()
        
        # Проверяем валидность
        total = sum(self.weight_vars[k].get() for k in self.weight_order)
        if abs(total - 100.0) > 0.1:
            if not messagebox.askyesno("Предупреждение", 
                                     f"Сумма весов равна {total:.1f}%, а не 100%.\n"
                                     "Продолжить сохранение?"):
                return
        
        # Нормализуем веса (делим на 100 для получения значений от 0 до 1)
        w = self.weight_vars
        self.db.set_similarity_weights(
            w["complexity"].get() / 100.0,
            w["player_count"].get() / 100.0,
            w["game_type"].get() / 100.0,
            w["duration"].get() / 100.0,
            w["mechanics"].get() / 100.0,
            w["genre"].get() / 100.0,
            w["user_params"].get() / 100.0,
            self.min_threshold_var.get(),
            self.missing_data_penalty_var.get(),
            self.max_recs_var.get(),
        )
        
        # Сохраняем настройки в файл
        self._save_settings()
        
        messagebox.showinfo("Успех", "Настройки успешно сохранены!")
        self.destroy()


class MainWindow(tk.Tk):
    def __init__(self, universe: Universe):
        super().__init__()
        self.title(f"BoardGame Advisor — {universe.name}")
        self.geometry("900x600")

        self.universe = universe
        self.db = universe.db
        self.players: dict[str, str] = {}  # player_id -> name
        self.matches: list[dict] = []      # простые сведения о партиях
        self.match_counter = 1
        self.player_counter = 1
        self.similarities: set[tuple[str, str]] = set()  # пары похожих игр
        self.removed_similarities: set[tuple[str, str]] = set()  # удалённые связи (чтобы не показывать при обновлении)

        self._build_ui()

    def _build_ui(self):
        top_bar = ttk.Frame(self)
        top_bar.pack(fill="x")

        ttk.Label(top_bar, text=self.universe.name, font=("Segoe UI", 12, "bold")).pack(
            side="left", padx=10, pady=5
        )

        ttk.Button(top_bar, text="📊 Отчёт", command=self.show_report).pack(side="right", padx=5)
        settings_btn = ttk.Button(top_bar, text="⚙", width=3, command=self.open_settings)
        settings_btn.pack(side="right", padx=10)
        # Кнопка для демонстрации обработки ошибок библиотеки
        tests_btn = ttk.Button(top_bar, text="🧪 Тесты", command=self.show_tests_dialog)
        tests_btn.pack(side="right", padx=5)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self._build_games_tab()
        self._build_players_tab()
        self._build_matches_tab()
        self._build_recommendations_tab()
        self._build_statistics_tab()

    # --- Вспомогательные методы ---

    def _generate_player_id(self) -> str:
        """Сгенерировать уникальный ID игрока вида p001, p002, ..."""
        while True:
            pid = f"p{self.player_counter:03d}"
            self.player_counter += 1
            if pid not in self.players:
                return pid

    def _find_player_id_by_name(self, name: str) -> str | None:
        for pid, nm in self.players.items():
            if nm == name:
                return pid
        return None

    # --- Вкладка "Игры" ---

    def _build_games_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Игры")

        left = ttk.Frame(frame)
        left.pack(side="left", fill="y", padx=5, pady=5)

        right = ttk.Frame(frame)
        right.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.games_list = tk.Listbox(left, height=20)
        self.games_list.pack(side="left", fill="y")

        ttk.Button(left, text="Добавить игру", command=self.add_game_dialog).pack(
            fill="x", pady=2
        )
        ttk.Button(left, text="Удалить игру", command=self.remove_selected_game).pack(
            fill="x", pady=2
        )
        ttk.Button(left, text="Редактировать признаки", command=self.edit_game_features).pack(
            fill="x", pady=2
        )
        ttk.Button(left, text="Управление похожими играми", command=self.manage_similar_games).pack(
            fill="x", pady=2
        )

        # Разделяем правую панель на две части: детали и рейтинги
        details_frame = ttk.Frame(right)
        details_frame.pack(fill="both", expand=True)

        self.game_details = tk.Text(details_frame, height=10, wrap="word")
        self.game_details.pack(fill="both", expand=True, pady=(0, 5))

        # Секция рейтингов
        ratings_frame = ttk.LabelFrame(details_frame, text="Оценки и рейтинги")
        ratings_frame.pack(fill="x", pady=5)

        # Информация о рейтинге
        self.rating_info = tk.Text(ratings_frame, height=4, wrap="word", state="disabled")
        self.rating_info.pack(fill="x", padx=5, pady=5)

        # Форма добавления оценки
        rating_form = ttk.Frame(ratings_frame)
        rating_form.pack(fill="x", padx=5, pady=5)

        ttk.Label(rating_form, text="Игрок:").grid(row=0, column=0, sticky="w", padx=2)
        self.rating_player_var = tk.StringVar()
        rating_player_combo = ttk.Combobox(rating_form, textvariable=self.rating_player_var, width=20)
        rating_player_combo.grid(row=0, column=1, padx=2)

        ttk.Label(rating_form, text="Оценка (1-5):").grid(row=0, column=2, sticky="w", padx=2)
        self.rating_value_var = tk.IntVar(value=5)
        rating_spinbox = ttk.Spinbox(rating_form, from_=1, to=5, textvariable=self.rating_value_var, width=5)
        rating_spinbox.grid(row=0, column=3, padx=2)

        ttk.Button(rating_form, text="Добавить/Изменить оценку", command=self.add_rating_to_game).grid(
            row=0, column=4, padx=5
        )

        self.rating_player_combo = rating_player_combo

        self.games_list.bind("<<ListboxSelect>>", self._on_game_select)

    def _get_all_genres(self):
        """Получить все уникальные жанры из базы данных."""
        genres = set()
        for i in range(self.games_list.size()):
            game_name = self.games_list.get(i)
            game = self.db.get_game(game_name)
            if game:
                genre = game.get_genre()
                if genre:
                    genres.add(genre)
        return sorted(list(genres))
    
    def _get_all_themes(self):
        """Получить все уникальные темы из базы данных."""
        themes = set()
        for i in range(self.games_list.size()):
            game_name = self.games_list.get(i)
            game = self.db.get_game(game_name)
            if game:
                theme = game.get_feature("Тема")
                if theme:
                    themes.add(theme)
        return sorted(list(themes))
    
    def _get_all_mechanics(self):
        """Получить все уникальные механики из базы данных."""
        mechanics = set()
        for i in range(self.games_list.size()):
            game_name = self.games_list.get(i)
            game = self.db.get_game(game_name)
            if game:
                mech = game.get_mechanics()
                if mech:
                    # Механики могут быть разделены запятыми
                    for m in mech.split(","):
                        m = m.strip()
                        if m:
                            mechanics.add(m)
        return sorted(list(mechanics))
    
    def _get_all_durations(self):
        """Получить все уникальные длительности из базы данных."""
        durations = set()
        for i in range(self.games_list.size()):
            game_name = self.games_list.get(i)
            game = self.db.get_game(game_name)
            if game:
                dur = game.get_duration()
                if dur > 0:
                    durations.add(str(dur))
        return sorted(list(durations), key=lambda x: int(x))
    
    def _get_all_complexities(self):
        """Получить все уникальные сложности из базы данных."""
        complexities = set()
        for i in range(self.games_list.size()):
            game_name = self.games_list.get(i)
            game = self.db.get_game(game_name)
            if game:
                comp = game.get_complexity()
                if comp:
                    complexities.add(comp)
        return sorted(list(complexities))
    
    def _get_all_game_types(self):
        """Получить все уникальные типы игр из базы данных."""
        game_types = set()
        for i in range(self.games_list.size()):
            game_name = self.games_list.get(i)
            game = self.db.get_game(game_name)
            if game:
                gt = game.get_game_type()
                if gt:
                    game_types.add(gt)
        return sorted(list(game_types))
    
    def _refresh_players_list(self):
        """Обновить список игроков во вкладке игроков."""
        self.players_list.delete(0, tk.END)
        for player_id, name in sorted(self.players.items(), key=lambda x: x[1]):
            self.players_list.insert(tk.END, f"{name} ({player_id})")

    def add_game_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Новая игра")

        entries = {}
        row = 0
        
        # Название
        ttk.Label(dialog, text="Название").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.grid(row=row, column=1, padx=5, pady=2)
        entries["name"] = name_entry
        row += 1
        
        # Описание
        ttk.Label(dialog, text="Описание").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        desc_entry = ttk.Entry(dialog, width=40)
        desc_entry.grid(row=row, column=1, padx=5, pady=2)
        entries["description"] = desc_entry
        row += 1
        
        # Мин. игроков (выпадающий список 1-20)
        ttk.Label(dialog, text="Мин. игроков").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        min_players_combo = ttk.Combobox(dialog, values=[str(i) for i in range(1, 21)], width=37, state="readonly")
        min_players_combo.set("1")
        min_players_combo.grid(row=row, column=1, padx=5, pady=2)
        entries["min_players"] = min_players_combo
        row += 1
        
        # Макс. игроков (выпадающий список 1-20)
        ttk.Label(dialog, text="Макс. игроков").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        max_players_combo = ttk.Combobox(dialog, values=[str(i) for i in range(1, 21)], width=37, state="readonly")
        max_players_combo.set("4")
        max_players_combo.grid(row=row, column=1, padx=5, pady=2)
        entries["max_players"] = max_players_combo
        row += 1
        
        # Сложность (выпадающий список с валидацией формата)
        ttk.Label(dialog, text="Сложность (1-10)").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        complexities = self._get_all_complexities()
        complexity_combo = ttk.Combobox(dialog, values=complexities, width=37)
        complexity_combo.grid(row=row, column=1, padx=5, pady=2)
        entries["complexity"] = complexity_combo
        row += 1
        
        # Длительность (выпадающий список с возможностью ввода своего)
        ttk.Label(dialog, text="Длительность (мин)").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        durations = self._get_all_durations()
        duration_combo = ttk.Combobox(dialog, values=durations, width=37)
        duration_combo.grid(row=row, column=1, padx=5, pady=2)
        entries["duration"] = duration_combo
        row += 1
        
        # Тип игры (выпадающий список с возможностью ввода своего)
        ttk.Label(dialog, text="Тип игры").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        game_types = self._get_all_game_types()
        game_type_combo = ttk.Combobox(dialog, values=game_types, width=37)
        game_type_combo.grid(row=row, column=1, padx=5, pady=2)
        entries["game_type"] = game_type_combo
        row += 1
        
        # Жанр (выпадающий список с возможностью ввода своего)
        ttk.Label(dialog, text="Жанр").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        genres = self._get_all_genres()
        genre_combo = ttk.Combobox(dialog, values=genres, width=37)
        genre_combo.grid(row=row, column=1, padx=5, pady=2)
        entries["genre"] = genre_combo
        row += 1
        
        # Тема (выпадающий список с возможностью ввода своего)
        ttk.Label(dialog, text="Тема").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        themes = self._get_all_themes()
        theme_combo = ttk.Combobox(dialog, values=themes, width=37)
        theme_combo.grid(row=row, column=1, padx=5, pady=2)
        entries["theme"] = theme_combo
        row += 1
        
        # Механики (выпадающий список с возможностью ввода своего)
        ttk.Label(dialog, text="Механики").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        mechanics = self._get_all_mechanics()
        mechanics_combo = ttk.Combobox(dialog, values=mechanics, width=37)
        mechanics_combo.grid(row=row, column=1, padx=5, pady=2)
        entries["mechanics"] = mechanics_combo
        row += 1

        def on_ok():
            try:
                name = entries["name"].get().strip()
                if not name:
                    raise ValueError("Название обязательно")
                desc = entries["description"].get().strip()
                
                # Получаем значения из комбобоксов или введённые значения
                min_p_str = entries["min_players"].get() if hasattr(entries["min_players"], "get") else entries["min_players"]
                max_p_str = entries["max_players"].get() if hasattr(entries["max_players"], "get") else entries["max_players"]
                min_p = int(min_p_str or "1")
                max_p = int(max_p_str or "4")
                
                if min_p > max_p:
                    raise ValueError("Минимальное количество игроков не может быть больше максимального")
                
                # Сложность - проверяем формат (может быть число с точкой)
                complexity = entries["complexity"].get().strip()
                if complexity:
                    try:
                        # Пробуем преобразовать в float для проверки формата
                        float(complexity)
                        # Проверяем, что значение в диапазоне 1-10
                        comp_value = float(complexity)
                        if comp_value < 1 or comp_value > 10:
                            raise ValueError("Сложность должна быть в диапазоне от 1 до 10")
                    except ValueError as e:
                        if "Сложность должна быть" in str(e):
                            raise
                        raise ValueError("Сложность должна быть числом (можно с точкой, например: 7.5)")
                
                # Длительность - проверяем, что это число
                duration_str = entries["duration"].get().strip()
                if not duration_str:
                    duration = 60
                else:
                    try:
                        duration = int(duration_str)
                        if duration <= 0:
                            raise ValueError("Длительность должна быть положительным числом")
                    except ValueError:
                        raise ValueError("Длительность должна быть целым числом (в минутах)")
                
                # Тип игры - проверяем, что не пустой (если указан)
                game_type = entries["game_type"].get().strip()
                if game_type and len(game_type) < 2:
                    raise ValueError("Тип игры должен содержать хотя бы 2 символа")
                
                # Жанр - может быть из списка или введённый вручную
                genre = entries["genre"].get().strip()
                
                # Тема - может быть из списка или введённая вручную
                theme = entries["theme"].get().strip()
                
                mechanics = entries["mechanics"].get().strip()
            except Exception as exc:
                messagebox.showerror("Ошибка", str(exc), parent=dialog)
                return

            game = BoardGame.create(name, desc, min_p, max_p, "")
            if complexity:
                game.set_complexity(complexity)
            game.set_duration(duration)
            if game_type:
                game.set_game_type(game_type)
            if genre:
                game.set_genre(genre)
            if theme:
                game.add_feature("Тема", theme)
            if mechanics:
                game.set_mechanics(mechanics)

            if self.db.add_game(game):
                self.games_list.insert(tk.END, name)
                self.refresh_games_combobox()
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", f"Не удалось добавить игру '{name}'. Возможно, игра с таким названием уже существует.", parent=dialog)

        ttk.Button(dialog, text="OK", command=on_ok).grid(
            row=row, column=0, columnspan=2, pady=5
        )

    def _on_game_select(self, event=None):
        """
        Обработчик выбора игры из списка.
        
        Демонстрирует обработку ошибки обработки данных внутри библиотеки:
        если игра присутствует в списке, но не найдена в базе данных библиотеки,
        это считается ошибкой обработки данных и обрабатывается соответствующим образом.
        """
        idx = self.games_list.curselection()
        if not idx:
            return
        name = self.games_list.get(idx[0])
        
        # Получаем игру из библиотеки
        # Обработка ошибки обработки данных внутри библиотеки
        try:
            game = self.db.get_game(name)
            if not game:
                # Игра есть в списке, но не найдена в базе данных библиотеки
                # Это ошибка обработки данных внутри библиотеки
                raise LibraryDataError(
                    f"Игра '{name}' найдена в списке, но не обнаружена в базе данных библиотеки. "
                    "Возможно, произошла ошибка синхронизации данных между интерфейсом и библиотекой.",
                    operation="get_game",
                    game_name=name
                )
        except LibraryDataError as e:
            # Обработка ошибки обработки данных внутри библиотеки
            # Показываем пользователю понятное сообщение об ошибке
            messagebox.showerror(
                "Ошибка обработки данных библиотеки",
                f"{str(e)}\n\n"
                "Рекомендуется обновить список игр или перезапустить приложение.",
                parent=self
            )
            # Очищаем детали игры, так как данные недоступны
            self.game_details.delete("1.0", tk.END)
            self.game_details.insert(tk.END, f"Ошибка: {e.message}")
            # Очищаем информацию о рейтингах
            self.rating_info.config(state="normal")
            self.rating_info.delete("1.0", tk.END)
            self.rating_info.insert(tk.END, "Данные недоступны из-за ошибки обработки.")
            self.rating_info.config(state="disabled")
            return

        info = [
            f"Название: {game.get_name()}",
            f"Описание: {game.get_description()}",
            f"Игроки: {game.get_min_players()}–{game.get_max_players()}",
            f"Сложность: {game.get_complexity()}",
            f"Длительность: {game.get_duration()} мин",
            f"Тип игры: {game.get_game_type()}",
            f"Жанр: {game.get_genre()}",
            f"Механики: {game.get_mechanics()}",
        ]

        self.game_details.delete("1.0", tk.END)
        self.game_details.insert(tk.END, "\n".join(info))

        # Обновляем информацию о рейтингах
        self._update_rating_info(game)

        # Обновляем список игроков для выбора
        player_values = [f"{name} ({pid})" for pid, name in self.players.items()]
        self.rating_player_combo["values"] = player_values

    def _update_rating_info(self, game):
        """Обновить информацию о рейтингах игры."""
        self.rating_info.config(state="normal")
        self.rating_info.delete("1.0", tk.END)

        avg_rating = game.get_average_rating()
        ratings_count = game.get_ratings_count()

        if ratings_count > 0:
            rating_text = f"Средний рейтинг: {avg_rating:.2f} (на основе {ratings_count} оценок)\n"
            # Получаем рейтинги через базу данных (если есть метод)
            # Пока что просто показываем средний рейтинг
            rating_text += "Для просмотра всех оценок используйте базу данных."
        else:
            rating_text = "Оценок пока нет. Добавьте первую оценку!"

        self.rating_info.insert("1.0", rating_text)
        self.rating_info.config(state="disabled")

    def add_rating_to_game(self):
        """Добавить или изменить оценку выбранной игре."""
        idx = self.games_list.curselection()
        if not idx:
            messagebox.showwarning("Не выбрана игра", "Сначала выберите игру из списка.")
            return

        game_name = self.games_list.get(idx[0])
        player_text = self.rating_player_var.get().strip()
        rating = self.rating_value_var.get()

        if not player_text:
            messagebox.showwarning("Не выбран игрок", "Выберите игрока из списка.")
            return

        # Извлекаем ID игрока из строки вида "Имя (p001)" или используем как есть
        if "(" in player_text and player_text.endswith(")"):
            player_id = player_text.rsplit("(", 1)[1][:-1].strip()
        else:
            # Пытаемся найти по имени
            player_id = self._find_player_id_by_name(player_text)
            if not player_id:
                messagebox.showerror("Ошибка", f"Игрок '{player_text}' не найден.")
                return

        # Проверяем, есть ли уже оценка у этого игрока
        existing_rating = self.db.get_player_rating_in_game(player_id, game_name)
        is_update = existing_rating > 0
        
        # Добавляем или обновляем оценку через базу данных
        # Метод add_rating в C++ должен перезаписывать существующую оценку
        if self.db.add_rating(game_name, player_id, rating):
            if is_update:
                messagebox.showinfo("Успех", 
                    f"Оценка игрока '{player_text}' для игры '{game_name}' изменена с {int(existing_rating)} на {rating}.")
            else:
                messagebox.showinfo("Успех", 
                    f"Оценка {rating} добавлена для игры '{game_name}' от игрока '{player_text}'.")
            # Обновляем информацию о рейтингах
            game = self.db.get_game(game_name)
            if game:
                self._update_rating_info(game)
        else:
            messagebox.showerror("Ошибка", "Не удалось добавить/изменить оценку.")

    def edit_game_features(self):
        """Открыть диалог редактирования признаков игры."""
        idx = self.games_list.curselection()
        if not idx:
            messagebox.showwarning("Не выбрана игра", "Сначала выберите игру из списка.")
            return

        game_name = self.games_list.get(idx[0])
        
        # Обработка ошибки обработки данных внутри библиотеки
        try:
            game = self.db.get_game(game_name)
            if not game:
                # Игра не найдена в базе данных библиотеки
                raise LibraryDataError(
                    f"Игра '{game_name}' не найдена в базе данных библиотеки. "
                    "Невозможно редактировать признаки несуществующей игры.",
                    operation="get_game (edit_features)",
                    game_name=game_name
                )
        except LibraryDataError as e:
            # Обработка ошибки обработки данных внутри библиотеки
            messagebox.showerror(
                "Ошибка обработки данных библиотеки",
                str(e),
                parent=self
            )
            return

        dialog = tk.Toplevel(self)
        dialog.title(f"Редактирование признаков: {game_name}")
        dialog.geometry("550x500")

        # Список существующих признаков
        features_frame = ttk.LabelFrame(dialog, text="Существующие признаки")
        features_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Treeview для отображения признаков
        columns = ("Название", "Значение")
        features_tree = ttk.Treeview(features_frame, columns=columns, show="headings", height=10)
        features_tree.heading("Название", text="Название")
        features_tree.heading("Значение", text="Значение")
        features_tree.column("Название", width=200)
        features_tree.column("Значение", width=300)
        features_tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Собираем все возможные названия признаков из всех игр
        all_feature_names = set()
        games = [self.games_list.get(i) for i in range(self.games_list.size())]
        for gname in games:
            g = self.db.get_game(gname)
            if g:
                # Проверяем стандартные признаки
                standard_features = ["Тема", "Издатель", "Год", "Дизайнер", "Художник", 
                                   "Число игроков", "Длительность", "Сложность", "Жанр", 
                                   "Тип игры", "Механики", "Описание"]
                for feat in standard_features:
                    val = g.get_feature(feat)
                    if val or g.has_feature(feat):
                        all_feature_names.add(feat)
        
        # Добавляем стандартные признаки, даже если они не используются
        standard_features_list = ["Тема", "Издатель", "Год", "Дизайнер", "Художник", 
                                "Число игроков", "Длительность", "Сложность", "Жанр", 
                                "Тип игры", "Механики", "Описание", "Рейтинг", "Количество оценок"]
        all_feature_names.update(standard_features_list)
        
        def refresh_features_list():
            """Обновить список признаков в дереве."""
            features_tree.delete(*features_tree.get_children())
            # Получаем все признаки текущей игры
            current_features = {}
            for feat_name in sorted(all_feature_names):
                val = game.get_feature(feat_name)
                if val:
                    current_features[feat_name] = val
                    features_tree.insert("", tk.END, values=(feat_name, val))
            
            # Также проверяем стандартные поля игры как признаки
            if game.get_genre():
                features_tree.insert("", tk.END, values=("Жанр", game.get_genre()))
            if game.get_game_type():
                features_tree.insert("", tk.END, values=("Тип игры", game.get_game_type()))
            if game.get_mechanics():
                features_tree.insert("", tk.END, values=("Механики", game.get_mechanics()))
            if game.get_complexity():
                features_tree.insert("", tk.END, values=("Сложность", game.get_complexity()))
            if game.get_duration():
                features_tree.insert("", tk.END, values=("Длительность", str(game.get_duration()) + " мин"))
            features_tree.insert("", tk.END, values=("Число игроков", f"{game.get_min_players()}-{game.get_max_players()}"))

        refresh_features_list()

        # Форма добавления/редактирования признака
        form_frame = ttk.LabelFrame(dialog, text="Добавить/Изменить признак")
        form_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(form_frame, text="Название:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        feature_name_combo = ttk.Combobox(form_frame, width=28)
        feature_name_combo["values"] = sorted(all_feature_names)
        feature_name_combo.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(form_frame, text="Значение:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        feature_value_entry = ttk.Entry(form_frame, width=30)
        feature_value_entry.grid(row=1, column=1, padx=5, pady=2)

        def add_or_update_feature():
            name = feature_name_combo.get().strip()
            value = feature_value_entry.get().strip()
            if not name:
                messagebox.showwarning("Ошибка", "Название признака обязательно.", parent=dialog)
                return
            try:
                if game.add_feature(name, value):
                    # Обновляем список
                    refresh_features_list()
                    feature_name_combo.set("")
                    feature_value_entry.delete(0, tk.END)
                    messagebox.showinfo("Успех", f"Признак '{name}' добавлен/обновлён.", parent=dialog)
                else:
                    messagebox.showerror("Ошибка", "Не удалось добавить признак.", parent=dialog)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при добавлении признака:\n{str(e)}", parent=dialog)

        def delete_selected_feature():
            selection = features_tree.selection()
            if not selection:
                messagebox.showwarning("Не выбран признак", "Выберите признак для удаления.", parent=dialog)
                return
            item = features_tree.item(selection[0])
            feature_name = item["values"][0]
            # Нельзя удалять стандартные поля игры
            if feature_name in ["Жанр", "Тип игры", "Механики", "Сложность", "Длительность", "Число игроков"]:
                messagebox.showwarning("Предупреждение", 
                                     f"Признак '{feature_name}' является стандартным полем игры и не может быть удалён.", 
                                     parent=dialog)
                return
            if messagebox.askyesno("Подтверждение", f"Удалить признак '{feature_name}'?", parent=dialog):
                try:
                    if game.remove_feature(feature_name):
                        refresh_features_list()
                        messagebox.showinfo("Успех", f"Признак '{feature_name}' удалён.", parent=dialog)
                    else:
                        messagebox.showerror("Ошибка", "Не удалось удалить признак.", parent=dialog)
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка при удалении признака:\n{str(e)}", parent=dialog)

        def on_feature_select(event):
            selection = features_tree.selection()
            if selection:
                item = features_tree.item(selection[0])
                feature_name_combo.set(item["values"][0])
                feature_value_entry.delete(0, tk.END)
                feature_value_entry.insert(0, item["values"][1])

        features_tree.bind("<<TreeviewSelect>>", on_feature_select)

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=5)

        ttk.Button(btn_frame, text="Добавить/Изменить", command=add_or_update_feature).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Удалить", command=delete_selected_feature).pack(side="left", padx=5)

        ttk.Button(dialog, text="Закрыть", command=dialog.destroy).pack(pady=10)

    def manage_similar_games(self):
        """Открыть диалог управления похожими играми."""
        dialog = tk.Toplevel(self)
        dialog.title("Управление похожими играми")
        dialog.geometry("600x500")

        # Форма добавления связи
        add_frame = ttk.LabelFrame(dialog, text="Добавить связь похожести")
        add_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(add_frame, text="Игра A:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        game_a_var = tk.StringVar()
        game_a_combo = ttk.Combobox(add_frame, textvariable=game_a_var, width=30)
        games_list = [self.games_list.get(i) for i in range(self.games_list.size())]
        game_a_combo["values"] = games_list
        game_a_combo.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(add_frame, text="похожа на игру B:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        game_b_var = tk.StringVar()
        game_b_combo = ttk.Combobox(add_frame, textvariable=game_b_var, width=30)
        game_b_combo["values"] = games_list
        game_b_combo.grid(row=1, column=1, padx=5, pady=2)

        def add_similarity():
            game_a = game_a_var.get().strip()
            game_b = game_b_var.get().strip()
            if not game_a or not game_b:
                messagebox.showwarning("Ошибка", "Выберите обе игры.", parent=dialog)
                return
            if game_a == game_b:
                messagebox.showwarning("Ошибка", "Игра не может быть похожа сама на себя.", parent=dialog)
                return
            if self.db.add_similarity(game_a, game_b):
                # Добавляем в локальный кэш
                pair = tuple(sorted([game_a, game_b]))
                self.similarities.add(pair)
                messagebox.showinfo("Успех", f"Связь между '{game_a}' и '{game_b}' добавлена.", parent=dialog)
                refresh_similarities_list()
                game_a_var.set("")
                game_b_var.set("")
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить связь.", parent=dialog)

        ttk.Button(add_frame, text="Добавить связь", command=add_similarity).grid(
            row=2, column=0, columnspan=2, pady=5
        )

        # Список существующих связей
        list_frame = ttk.LabelFrame(dialog, text="Существующие связи")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Treeview для отображения связей
        tree_container = ttk.Frame(list_frame)
        tree_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        columns = ("Игра A", "Игра B")
        similarities_tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=12)
        similarities_tree.heading("Игра A", text="Игра A")
        similarities_tree.heading("Игра B", text="Игра B")
        similarities_tree.column("Игра A", width=250)
        similarities_tree.column("Игра B", width=250)
        similarities_tree.pack(fill="both", expand=True)

        def refresh_similarities_list():
            """Обновить список связей похожести."""
            similarities_tree.delete(*similarities_tree.get_children())
            # Обновляем кэш связей, проверяя все пары игр
            games = [self.games_list.get(i) for i in range(self.games_list.size())]
            for i, game_a in enumerate(games):
                for game_b in games[i+1:]:
                    pair_key = tuple(sorted([game_a, game_b]))
                    # Пропускаем удалённые связи
                    if pair_key in self.removed_similarities:
                        continue
                    # Проверяем, есть ли связь в кэше или в базе данных
                    if pair_key in self.similarities or self.db.are_similar(game_a, game_b):
                        if pair_key not in self.similarities:
                            self.similarities.add(pair_key)
                        similarities_tree.insert("", tk.END, values=(game_a, game_b))

        def delete_selected_similarity():
            selection = similarities_tree.selection()
            if not selection:
                messagebox.showwarning("Не выбрана связь", "Выберите связь для удаления.", parent=dialog)
                return
            item = similarities_tree.item(selection[0])
            game_a, game_b = item["values"]
            
            # Подтверждение удаления
            if not messagebox.askyesno(
                "Удалить связь",
                f"Удалить связь между '{game_a}' и '{game_b}'?",
                parent=dialog
            ):
                return
            
            # Пытаемся удалить связь из базы данных
            # Если метод remove_similarity существует, используем его
            removed = False
            if hasattr(self.db, 'remove_similarity'):
                removed = self.db.remove_similarity(game_a, game_b)
            else:
                # Если метода нет, просто удаляем из локального кэша
                # (в будущем можно добавить метод в C API)
                removed = True
            
            if removed:
                # Удаляем из локального кэша
                pair_key = tuple(sorted([game_a, game_b]))
                self.similarities.discard(pair_key)
                # Добавляем в список удалённых, чтобы не показывать при обновлении
                self.removed_similarities.add(pair_key)
                similarities_tree.delete(selection[0])
                messagebox.showinfo("Успех", f"Связь между '{game_a}' и '{game_b}' удалена.", parent=dialog)
            else:
                messagebox.showerror("Ошибка", f"Не удалось удалить связь между '{game_a}' и '{game_b}'.", parent=dialog)

        refresh_similarities_list()

        # Кнопки управления связями (размещаем после Treeview, но внутри list_frame)
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill="x", padx=5, pady=5)

        ttk.Button(btn_frame, text="🔄 Обновить список", command=refresh_similarities_list).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="❌ Удалить выбранную", command=delete_selected_similarity).pack(side="left", padx=5)

        # Кнопка закрытия диалога
        ttk.Button(dialog, text="Закрыть", command=dialog.destroy).pack(pady=10)

    def demo_library_error(self):
        """
        Демонстрация обработки ошибки обработки данных внутри библиотеки.
        
        Создаёт искусственную ситуацию рассинхронизации:
        добавляет игру в список интерфейса, но не добавляет её в базу данных библиотеки.
        При попытке выбрать эту игру будет вызвана обработка ошибки LibraryDataError.
        """
        if not messagebox.askyesno(
            "Демонстрация обработки ошибки",
            "Этот режим создаст искусственную ситуацию для демонстрации обработки ошибки.\n\n"
            "Будет добавлена тестовая игра в список интерфейса, но не в базу данных библиотеки.\n"
            "При попытке выбрать эту игру вы увидите обработку ошибки LibraryDataError.\n\n"
            "Продолжить?",
            parent=self
        ):
            return
        
        # Создаём тестовую игру в списке, но НЕ добавляем её в базу данных
        # Это создаёт ситуацию рассинхронизации для демонстрации обработки ошибки
        test_game_name = "ТЕСТОВАЯ_ИГРА_ДЛЯ_ДЕМО_ОШИБКИ"
        
        # Проверяем, нет ли уже такой игры
        if test_game_name in [self.games_list.get(i) for i in range(self.games_list.size())]:
            messagebox.showinfo(
                "Информация",
                f"Тестовая игра '{test_game_name}' уже добавлена.\n"
                "Попробуйте выбрать её из списка, чтобы увидеть обработку ошибки.",
                parent=self
            )
            return
        
        # Добавляем игру только в список интерфейса, НЕ в базу данных
        # Это создаёт ситуацию рассинхронизации
        self.games_list.insert(tk.END, test_game_name)
        
        messagebox.showinfo(
            "Демонстрация готова",
            f"Тестовая игра '{test_game_name}' добавлена в список интерфейса.\n\n"
            "Теперь:\n"
            "1. Выберите эту игру из списка игр\n"
            "2. Вы увидите обработку ошибки LibraryDataError\n"
            "3. Появится сообщение об ошибке обработки данных библиотеки\n\n"
            "Это демонстрирует технику обработки ошибок, возникающих при работе\n"
            "с данными в C++ библиотеке через Python-обёртку.",
            parent=self
        )
        
        # Автоматически выбираем добавленную игру для демонстрации
        # Находим индекс добавленной игры
        for i in range(self.games_list.size()):
            if self.games_list.get(i) == test_game_name:
                self.games_list.selection_set(i)
                self.games_list.see(i)
                # Вызываем обработчик выбора для демонстрации ошибки
                self._on_game_select()
                break

    def show_tests_dialog(self):
        """
        Диалог для демонстрации обработки ошибок библиотеки.
        Объединяет все тесты обработки ошибок в одном месте.
        """
        dialog = tk.Toplevel(self)
        dialog.title("Тесты обработки ошибок библиотеки")
        dialog.geometry("800x600")
        
        # Создаём вкладки для разных типов ошибок
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # === Вкладка 1: Ошибка обработки данных ===
        data_error_frame = ttk.Frame(notebook)
        notebook.add(data_error_frame, text="Ошибка обработки данных")
        
        # Описание ошибки
        desc_frame = ttk.LabelFrame(data_error_frame, text="Описание ошибки")
        desc_frame.pack(fill="x", padx=10, pady=5)
        
        desc_text = tk.Text(desc_frame, height=8, wrap="word", font=("Consolas", 9))
        desc_text.pack(fill="both", expand=True, padx=5, pady=5)
        desc_text.insert("1.0", 
            "ОШИБКА ОБРАБОТКИ ДАННЫХ В БИБЛИОТЕКЕ\n"
            "═══════════════════════════════════════════════════════════════\n\n"
            "ЧТО ЭТО ЗА ОШИБКА?\n"
            "Ошибка возникает, когда данные в интерфейсе (Python GUI) не синхронизированы\n"
            "с данными в библиотеке (C++ DLL). Например, игра присутствует в списке\n"
            "интерфейса, но отсутствует в базе данных библиотеки.\n\n"
            "ПОЧЕМУ ОНА МОЖЕТ ВОЗНИКНУТЬ?\n"
            "1. Рассинхронизация данных между интерфейсом и библиотекой\n"
            "2. Ошибка при добавлении игры (игра добавлена в список, но не в базу)\n"
            "3. Игра была удалена из базы, но осталась в списке интерфейса\n"
            "4. Проблемы с сохранением/загрузкой данных\n\n"
            "КАК ОНА ОБРАБАТЫВАЕТСЯ?\n"
            "1. При попытке получить игру из библиотеки проверяется результат\n"
            "2. Если игра не найдена, выбрасывается исключение LibraryDataError\n"
            "3. Исключение перехватывается в try-except блоке\n"
            "4. Пользователю показывается информативное сообщение об ошибке\n"
            "5. UI очищается от недоступных данных\n\n"
            "ГДЕ В КОДЕ?\n"
            "- Класс LibraryDataError (app_gui.py, строки 17-36)\n"
            "- Обработка в _on_game_select() (app_gui.py, строки 772-800)\n"
            "- Обработка в edit_game_features() (app_gui.py, строки 870-880)"
        )
        desc_text.config(state="disabled")
        
        # Кнопка запуска теста
        test_btn_frame = ttk.Frame(data_error_frame)
        test_btn_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(test_btn_frame, text="▶ Запустить тест", 
                  command=lambda: self._run_data_error_test(dialog)).pack(side="left", padx=5)
        
        # === Вкладка 2: Ошибка NULL указателя ===
        null_error_frame = ttk.Frame(notebook)
        notebook.add(null_error_frame, text="Ошибка NULL указателя")
        
        # Описание ошибки
        desc_frame2 = ttk.LabelFrame(null_error_frame, text="Описание ошибки")
        desc_frame2.pack(fill="x", padx=10, pady=5)
        
        desc_text2 = tk.Text(desc_frame2, height=8, wrap="word", font=("Consolas", 9))
        desc_text2.pack(fill="both", expand=True, padx=5, pady=5)
        desc_text2.insert("1.0",
            "ОШИБКА NULL УКАЗАТЕЛЯ В БИБЛИОТЕКЕ\n"
            "═══════════════════════════════════════════════════════════════\n\n"
            "ЧТО ЭТО ЗА ОШИБКА?\n"
            "Ошибка возникает, когда в функцию C++ библиотеки передаётся NULL указатель\n"
            "вместо валидного указателя на данные. Это критическая ошибка, которая может\n"
            "привести к крашу программы, если не обработана правильно.\n\n"
            "ПОЧЕМУ ОНА МОЖЕТ ВОЗНИКНУТЬ?\n"
            "1. Передача None из Python в ctypes (автоматически преобразуется в NULL)\n"
            "2. Ошибка в коде, где не проверяется валидность указателя перед передачей\n"
            "3. Проблемы с кодированием строк (пустая строка или ошибка encode)\n"
            "4. Неправильная инициализация объектов\n\n"
            "КАК ОНА ОБРАБАТЫВАЕТСЯ?\n"
            "1. В C++ коде проверяется каждый указатель на NULL перед использованием\n"
            "2. Если обнаружен NULL, функция возвращает 0 (False) вместо выполнения операции\n"
            "3. В Python-обёртке результат проверяется и преобразуется в исключение\n"
            "4. Исключение LibraryNullPointerError перехватывается и обрабатывается\n"
            "5. Пользователю показывается информативное сообщение с техническими деталями\n\n"
            "ГДЕ В КОДЕ?\n"
            "- Проверка NULL в C++: GameDatabaseCAPI.cpp, строки 49-55\n"
            "  if (!db || !player_id || !player_name) return 0;\n"
            "- Метод add_player_with_null_check() (boardgame_lib.py, строки 361-388)\n"
            "- Класс LibraryNullPointerError (app_gui.py, строки 38-54)\n"
            "- Обработка в demo_null_pointer_error() (app_gui.py)"
        )
        desc_text2.config(state="disabled")
        
        # Кнопка запуска теста
        test_btn_frame2 = ttk.Frame(null_error_frame)
        test_btn_frame2.pack(fill="x", padx=10, pady=5)
        ttk.Button(test_btn_frame2, text="▶ Запустить тест", 
                  command=lambda: self._run_null_pointer_test(dialog)).pack(side="left", padx=5)
        
        # Кнопка закрытия
        close_btn = ttk.Button(dialog, text="Закрыть", command=dialog.destroy)
        close_btn.pack(pady=10)
    
    def _run_data_error_test(self, parent_dialog):
        """Запустить тест ошибки обработки данных."""
        # Используем существующий метод, но без показа диалога подтверждения
        test_game_name = "ТЕСТОВАЯ_ИГРА_ДЛЯ_ДЕМО_ОШИБКИ"
        
        # Проверяем, нет ли уже такой игры
        if test_game_name in [self.games_list.get(i) for i in range(self.games_list.size())]:
            messagebox.showinfo(
                "Информация",
                f"Тестовая игра '{test_game_name}' уже добавлена.\n"
                "Попробуйте выбрать её из списка, чтобы увидеть обработку ошибки.",
                parent=parent_dialog
            )
            return
        
        # Добавляем игру только в список интерфейса, НЕ в базу данных
        self.games_list.insert(tk.END, test_game_name)
        
        messagebox.showinfo(
            "Тест запущен",
            f"Тестовая игра '{test_game_name}' добавлена в список интерфейса.\n\n"
            "Теперь выберите эту игру из списка игр, чтобы увидеть обработку ошибки.\n\n"
            "Ожидаемое поведение:\n"
            "1. При выборе игры будет вызвана обработка ошибки LibraryDataError\n"
            "2. Появится сообщение об ошибке обработки данных библиотеки\n"
            "3. Детали игры будут очищены (данные недоступны)",
            parent=parent_dialog
        )
        
        # Автоматически выбираем добавленную игру для демонстрации
        for i in range(self.games_list.size()):
            if self.games_list.get(i) == test_game_name:
                self.games_list.selection_set(i)
                self.games_list.see(i)
                # Вызываем обработчик выбора для демонстрации ошибки
                self._on_game_select()
                break
    
    def _run_null_pointer_test(self, parent_dialog):
        """Запустить тест ошибки NULL указателя."""
        # Используем существующий метод, но без показа диалога подтверждения
        try:
            # Пытаемся добавить игрока с NULL указателем на имя
            result = self.db.add_player_with_null_check("p999", None)
            
            if not result:
                # Библиотека вернула False, что означает обнаружение NULL указателя
                raise LibraryNullPointerError(
                    "Библиотека обнаружила NULL указатель при добавлении игрока. "
                    "Параметр 'name' не может быть NULL.",
                    operation="db_add_player",
                    parameter="player_name"
                )
        except LibraryNullPointerError as e:
            # Обработка ошибки NULL указателя в библиотеке
            messagebox.showerror(
                "Тест выполнен: Ошибка NULL указателя обнаружена",
                f"{str(e)}\n\n"
                "✅ ТЕСТ ПРОЙДЕН: Библиотека корректно обработала NULL указатель\n\n"
                "Что произошло:\n"
                "1. В библиотеку был передан NULL указатель на имя игрока\n"
                "2. Библиотека C++ обнаружила NULL в функции db_add_player\n"
                "3. Функция вернула 0 (False) вместо выполнения операции\n"
                "4. Ошибка была обработана и преобразована в исключение\n\n"
                "Это демонстрирует правильную технику обработки ошибок NULL указателей\n"
                "в C++ библиотеке через Python-обёртку.",
                parent=parent_dialog
            )
            
            # Показываем дополнительную информацию
            info_text = (
                "ТЕХНИЧЕСКИЕ ДЕТАЛИ ОБРАБОТКИ\n"
                "═══════════════════════════════════════════════════════════════\n\n"
                "1. В C++ коде (GameDatabaseCAPI.cpp, строки 49-55):\n"
                "   int db_add_player(GameDatabaseHandle db, const char* player_id, const char* player_name) {\n"
                "       if (!db || !player_id || !player_name) {\n"
                "           return 0;  // ← Обнаружен NULL указатель\n"
                "       }\n"
                "       ...\n"
                "   }\n\n"
                "2. В Python-обёртке (boardgame_lib.py):\n"
                "   - None автоматически преобразуется в NULL для ctypes\n"
                "   - Результат проверяется и преобразуется в исключение\n\n"
                "3. В GUI (app_gui.py):\n"
                "   - Исключение LibraryNullPointerError перехватывается\n"
                "   - Показывается информативное сообщение пользователю"
            )
            messagebox.showinfo(
                "Технические детали",
                info_text,
                parent=parent_dialog
            )
        except AttributeError:
            # Если метод add_player_with_null_check не существует
            messagebox.showerror(
                "Ошибка",
                "Метод add_player_with_null_check не найден.\n"
                "Убедитесь, что он добавлен в boardgame_lib.py",
                parent=parent_dialog
            )

    def demo_null_pointer_error(self):
        """
        Демонстрация обработки ошибки NULL указателя в библиотеке.
        
        Создаёт ситуацию, когда в библиотеку передаётся NULL указатель,
        и демонстрирует, как библиотека обрабатывает эту ошибку.
        """
        if not messagebox.askyesno(
            "Демонстрация ошибки NULL указателя",
            "Этот режим продемонстрирует обработку ошибки NULL указателя в библиотеке.\n\n"
            "Будет вызван метод добавления игрока с передачей NULL указателя.\n"
            "Библиотека обнаружит NULL указатель и вернёт ошибку.\n"
            "Вы увидите обработку ошибки LibraryNullPointerError.\n\n"
            "Продолжить?",
            parent=self
        ):
            return
        
        # Демонстрируем обработку ошибки NULL указателя
        try:
            # Пытаемся добавить игрока с NULL указателем на имя
            # Используем специальный метод для демонстрации
            result = self.db.add_player_with_null_check("p999", None)
            
            if not result:
                # Библиотека вернула False, что означает обнаружение NULL указателя
                raise LibraryNullPointerError(
                    "Библиотека обнаружила NULL указатель при добавлении игрока. "
                    "Параметр 'name' не может быть NULL.",
                    operation="db_add_player",
                    parameter="player_name"
                )
        except LibraryNullPointerError as e:
            # Обработка ошибки NULL указателя в библиотеке
            messagebox.showerror(
                "Ошибка NULL указателя в библиотеке",
                f"{str(e)}\n\n"
                "Библиотека C++ корректно обработала NULL указатель:\n"
                "- Проверка на NULL выполняется в функции db_add_player\n"
                "- При обнаружении NULL указателя функция возвращает 0 (False)\n"
                "- Это предотвращает краш программы и позволяет обработать ошибку\n\n"
                "Это демонстрирует технику обработки ошибок NULL указателей\n"
                "в C++ библиотеке через Python-обёртку.",
                parent=self
            )
            
            # Показываем дополнительную информацию
            info_text = (
                "Технические детали:\n"
                "────────────────────\n"
                "1. В C++ коде (GameDatabaseCAPI.cpp):\n"
                "   if (!db || !player_id || !player_name) {\n"
                "       return 0;  // Обнаружен NULL указатель\n"
                "   }\n\n"
                "2. В Python-обёртке (boardgame_lib.py):\n"
                "   Результат проверяется и преобразуется в исключение\n\n"
                "3. В GUI (app_gui.py):\n"
                "   Исключение перехватывается и показывается пользователю"
            )
            messagebox.showinfo(
                "Технические детали обработки",
                info_text,
                parent=self
            )
        except AttributeError:
            # Если метод add_player_with_null_check не существует
            messagebox.showerror(
                "Ошибка",
                "Метод add_player_with_null_check не найден.\n"
                "Убедитесь, что он добавлен в boardgame_lib.py",
                parent=self
            )

    def remove_selected_game(self):
        idx = self.games_list.curselection()
        if not idx:
            return
        name = self.games_list.get(idx[0])
        if not messagebox.askyesno(
            "Удалить игру",
            f"Удалить игру '{name}' из текущей вселенной?\n"
            "Партии и рекомендации, в которых она участвовала, могут стать недействительными.",
            parent=self,
        ):
            return
        
        # Проверяем, является ли это тестовой игрой (не добавленной в базу данных)
        is_test_game = name == "ТЕСТОВАЯ_ИГРА_ДЛЯ_ДЕМО_ОШИБКИ"
        
        # Пытаемся удалить из базы данных
        removed_from_db = False
        if not is_test_game:
            # Для обычных игр пытаемся удалить из базы данных
            removed_from_db = self.db.remove_game(name)
        else:
            # Для тестовой игры она не была добавлена в базу, поэтому пропускаем удаление из БД
            removed_from_db = True  # Считаем успешным, так как её и не было в БД
        
        # Удаляем из списка интерфейса в любом случае
        if removed_from_db or is_test_game:
            self.games_list.delete(idx[0])
            self.game_details.delete("1.0", tk.END)
            # Удаляем локальные партии, связанные с этой игрой
            self.matches = [m for m in self.matches if m["game"] != name]
            self._refresh_matches_list()
            # Обновляем списки игр в комбобоксах
            self.refresh_games_combobox()
            
            if is_test_game:
                messagebox.showinfo(
                    "Игра удалена",
                    f"Тестовая игра '{name}' удалена из списка интерфейса.\n"
                    "(Она не была в базе данных, поэтому удаление из БД не требовалось.)",
                    parent=self
                )
        else:
            # Не удалось удалить из базы данных
            messagebox.showerror(
                "Ошибка",
                f"Не удалось удалить игру '{name}' из базы данных.",
                parent=self
            )

    # --- Вкладка "Игроки" ---

    def _build_players_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Игроки")

        left = ttk.Frame(frame)
        left.pack(side="left", fill="y", padx=5, pady=5)

        right = ttk.Frame(frame)
        right.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.players_list = tk.Listbox(left, height=20)
        self.players_list.pack(fill="y")

        ttk.Button(left, text="Добавить игрока", command=self.add_player_dialog).pack(
            fill="x", pady=2
        )
        ttk.Button(left, text="Удалить игрока", command=self.remove_selected_player).pack(
            fill="x", pady=2
        )

        self.player_details = tk.Text(right, height=10, wrap="word")
        self.player_details.pack(fill="both", expand=True)

        self.players_list.bind("<<ListboxSelect>>", self._on_player_select)

    def add_player_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Новый игрок")

        ttk.Label(dialog, text="ID игрока").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(dialog, text="(генерируется автоматически)").grid(
            row=0, column=1, sticky="w", padx=5, pady=2
        )

        ttk.Label(dialog, text="Имя игрока").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=1, column=1, padx=5, pady=2)

        def on_ok():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Ошибка", "Имя игрока обязательно", parent=dialog)
                return

            existing_id = self._find_player_id_by_name(name)
            if existing_id is not None:
                use_existing = messagebox.askyesno(
                    "Игрок уже существует",
                    f"Игрок с именем '{name}' уже есть (ID {existing_id}). Использовать его?",
                    parent=dialog,
                )
                if use_existing:
                    # просто выделим его в списке
                    for idx in range(self.players_list.size()):
                        if self.players_list.get(idx).endswith(f"({existing_id})"):
                            self.players_list.selection_clear(0, tk.END)
                            self.players_list.selection_set(idx)
                            self.players_list.see(idx)
                            break
                    dialog.destroy()
                    return

            player_id = self._generate_player_id()
            if self.db.add_player(player_id, name):
                self.players[player_id] = name
                self.players_list.insert(tk.END, f"{name} ({player_id})")
                self._update_stats_players_list()
            dialog.destroy()

        ttk.Button(dialog, text="OK", command=on_ok).grid(
            row=2, column=0, columnspan=2, pady=5
        )

    def remove_selected_player(self):
        idx = self.players_list.curselection()
        if not idx:
            return
        line = self.players_list.get(idx[0])
        # Формат: "Имя (p001)"
        if "(" in line and line.endswith(")"):
            player_id = line.split("(", 1)[1][:-1]
        else:
            player_id = line
        if messagebox.askyesno("Удалить игрока", f"Удалить игрока {line}?", parent=self):
            if self.db.remove_player(player_id):
                self.players_list.delete(idx[0])
                self.players.pop(player_id, None)
                self.player_details.delete("1.0", tk.END)
                # Обновляем список игроков в статистике
                self._update_stats_players_list()

    def _on_player_select(self, event=None):
        idx = self.players_list.curselection()
        if not idx:
            return
        line = self.players_list.get(idx[0])
        if "(" in line and line.endswith(")"):
            name, _, pid_part = line.partition(" (")
            player_id = pid_part[:-1]
        else:
            name = line
            player_id = ""
        info = [f"ID: {player_id}", f"Имя: {name}"]
        self.player_details.delete("1.0", tk.END)
        self.player_details.insert(tk.END, "\n".join(info))

    # --- Вкладка "Партии" ---

    def _build_matches_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Партии")

        left = ttk.Frame(frame)
        left.pack(side="left", fill="y", padx=5, pady=5)

        right = ttk.Frame(frame)
        right.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.matches_list = tk.Listbox(left, height=20)
        self.matches_list.pack(fill="y")

        ttk.Button(left, text="Добавить партию", command=self.add_match_dialog).pack(
            fill="x", pady=2
        )
        ttk.Button(left, text="Удалить партию", command=self.remove_selected_match).pack(
            fill="x", pady=2
        )
        
        # Фильтры и сортировка
        filter_frame = ttk.LabelFrame(left, text="Фильтры")
        filter_frame.pack(fill="x", pady=5)
        
        ttk.Label(filter_frame, text="Сортировка:").pack(anchor="w", padx=5, pady=2)
        self.match_sort_var = tk.StringVar(value="дата")
        sort_combo = ttk.Combobox(filter_frame, textvariable=self.match_sort_var, 
                                   values=["дата", "игра", "игрок"], state="readonly", width=15)
        sort_combo.pack(fill="x", padx=5, pady=2)
        sort_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_matches_list())
        
        ttk.Label(filter_frame, text="Фильтр по игре:").pack(anchor="w", padx=5, pady=2)
        self.match_filter_game_var = tk.StringVar()
        filter_game_combo = ttk.Combobox(filter_frame, textvariable=self.match_filter_game_var,
                                         width=15)
        filter_game_combo["values"] = ["(все)"] + [self.games_list.get(i) for i in range(self.games_list.size())]
        filter_game_combo.pack(fill="x", padx=5, pady=2)
        filter_game_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_matches_list())
        
        self.match_filter_game_combo = filter_game_combo

        self.match_details = tk.Text(right, height=10, wrap="word")
        self.match_details.pack(fill="both", expand=True)

        self.matches_list.bind("<<ListboxSelect>>", self._on_match_select)

    def add_match_dialog(self):
        if self.games_list.size() == 0:
            messagebox.showwarning("Нет игр", "Сначала добавьте хотя бы одну игру.")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Новая партия")

        ttk.Label(dialog, text="Игра").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        game_var = tk.StringVar()
        game_cb = ttk.Combobox(dialog, textvariable=game_var, state="readonly", width=30)
        game_cb["values"] = [self.games_list.get(i) for i in range(self.games_list.size())]
        if game_cb["values"]:
            game_var.set(game_cb["values"][0])
        game_cb.grid(row=0, column=1, padx=5, pady=2)
        
        # Обновляем места при изменении игры
        def update_places_on_game_change(event=None):
            game_name = game_var.get()
            if game_name:
                game_obj = self.db.get_game(game_name)
                if game_obj:
                    new_max = min(game_obj.get_max_players(), 6)
                    # Обновляем список мест
                    place_options = []
                    for i in range(1, new_max + 1):
                        if i == 1:
                            place_options.append("1-е место")
                        elif i == 2:
                            place_options.append("2-е место")
                        elif i == 3:
                            place_options.append("3-е место")
                        elif i == 4:
                            place_options.append("4-е место")
                        elif i == 5:
                            place_options.append("5-е место")
                        elif i == 6:
                            place_options.append("6-е место")
                        else:
                            place_options.append(f"{i}-е место")
                    
                    # Обновляем значения в комбобоксах мест
                    for place_combo in self.match_player_place_combos:
                        place_combo["values"] = place_options
                        if place_combo.get() not in place_options and place_options:
                            place_combo.set(place_options[0])
        
        game_cb.bind("<<ComboboxSelected>>", update_places_on_game_change)

        ttk.Label(dialog, text="Дата").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        if DateEntry is not None:
            date_entry = DateEntry(dialog, width=18, date_pattern="yyyy-mm-dd")
        else:
            date_entry = ttk.Entry(dialog, width=20)
            date_entry.insert(0, "2025-01-01")
        date_entry.grid(row=1, column=1, padx=5, pady=2)

        # Поля игроков: количество зависит от параметров игры (но не более 6 для удобства)
        players_frame = ttk.LabelFrame(dialog, text="Игроки и места")
        players_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Заголовки колонок
        ttk.Label(players_frame, text="Игрок", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, padx=2, pady=2)
        ttk.Label(players_frame, text="Имя", font=("Segoe UI", 9, "bold")).grid(row=0, column=1, padx=2, pady=2)
        ttk.Label(players_frame, text="Место", font=("Segoe UI", 9, "bold")).grid(row=0, column=2, padx=2, pady=2)

        game_obj = self.db.get_game(game_cb.get())
        min_players = game_obj.get_min_players() if game_obj else 1
        max_players = game_obj.get_max_players() if game_obj else 4
        max_players = min(max_players, 6)

        self.match_player_name_combos = []
        self.match_player_place_combos = []  # Для выбора места игрока
        self.match_player_rows = []
        self.current_visible_match_rows = min_players
        self.match_max_players_for_dialog = max_players

        def all_player_display_values():
            # Имя (ID)
            return [f"{name} ({pid})" for pid, name in self.players.items()]

        def setup_autocomplete(cb):
            def on_keyrelease(event):
                text = cb.get()
                values = all_player_display_values()
                if text:
                    filtered = [v for v in values if v.lower().startswith(text.lower())]
                else:
                    filtered = values
                cb["values"] = filtered
            cb.bind("<KeyRelease>", on_keyrelease)

        # Создаём список мест для выбора (1-е, 2-е, 3-е и т.д.)
        place_options = []
        for i in range(1, max_players + 1):
            if i == 1:
                place_options.append("1-е место")
            elif i == 2:
                place_options.append("2-е место")
            elif i == 3:
                place_options.append("3-е место")
            elif i == 4:
                place_options.append("4-е место")
            elif i == 5:
                place_options.append("5-е место")
            elif i == 6:
                place_options.append("6-е место")
            else:
                place_options.append(f"{i}-е место")

        for i in range(max_players):
            lbl = ttk.Label(players_frame, text=f"Игрок {i + 1}")
            lbl.grid(row=i + 1, column=0, sticky="w", padx=2, pady=2)  # +1 потому что первая строка - заголовки
            var = tk.StringVar()
            combo = ttk.Combobox(players_frame, textvariable=var, width=25)
            combo["values"] = all_player_display_values()
            combo.grid(row=i + 1, column=1, padx=2, pady=2, sticky="ew")  # +1 потому что первая строка - заголовки
            setup_autocomplete(combo)
            self.match_player_name_combos.append(combo)
            
            # Добавляем выбор места
            place_var = tk.StringVar()
            place_combo = ttk.Combobox(players_frame, textvariable=place_var, values=place_options, 
                                       state="readonly", width=12)
            place_combo.grid(row=i + 1, column=2, padx=2, pady=2)  # +1 потому что первая строка - заголовки
            if i < len(place_options):
                place_var.set(place_options[i])  # Устанавливаем место по умолчанию
            self.match_player_place_combos.append(place_combo)
            
            self.match_player_rows.append((lbl, combo, place_combo))
            if i >= self.current_visible_match_rows:
                lbl.grid_remove()
                combo.grid_remove()
                place_combo.grid_remove()
        
        # Вызываем обновление мест при первой загрузке
        update_places_on_game_change()

        def add_player_row():
            if self.current_visible_match_rows >= self.match_max_players_for_dialog:
                messagebox.showinfo(
                    "Лимит игроков",
                    f"Для этой игры максимум {self.match_max_players_for_dialog} игрок(ов).",
                    parent=dialog,
                )
                return
            lbl, combo, place_combo = self.match_player_rows[self.current_visible_match_rows]
            lbl.grid()
            combo.grid()
            place_combo.grid()
            self.current_visible_match_rows += 1

        ttk.Button(dialog, text="+ игрок", command=add_player_row).grid(
            row=3, column=0, columnspan=2, pady=2
        )

        def ensure_player_by_name(name: str) -> str:
            """Вернуть ID игрока по имени, создавая нового при необходимости."""
            if not name:
                return ""
            existing_id = self._find_player_id_by_name(name)
            if existing_id is not None:
                return existing_id
            pid = self._generate_player_id()
            if self.db.add_player(pid, name):
                self.players[pid] = name
                self.players_list.insert(tk.END, f"{name} ({pid})")
                return pid
            return ""

        def on_ok():
            game_name = game_var.get().strip()
            if not game_name:
                messagebox.showerror("Ошибка", "Не выбрана игра", parent=dialog)
                return
            date = date_entry.get().strip() or "2025-01-01"

            # Собираем игроков с их местами
            player_data = []
            game_obj_local = self.db.get_game(game_name)
            min_players_local = game_obj_local.get_min_players() if game_obj_local else 1
            max_players_local = game_obj_local.get_max_players() if game_obj_local else 4

            for i, combo in enumerate(self.match_player_name_combos[: self.current_visible_match_rows]):
                text = combo.get().strip()
                if not text:
                    continue
                # Ожидаем строку вида "Имя (p001)" или просто имя
                if "(" in text and text.endswith(")"):
                    name = text.rsplit("(", 1)[0].strip()
                else:
                    name = text
                
                # Получаем место игрока
                place_text = self.match_player_place_combos[i].get().strip()
                # Извлекаем число из строки вида "1-е место" -> 1
                place = 1  # По умолчанию
                if place_text:
                    try:
                        # Извлекаем первое число из строки
                        place_match = re.search(r'\d+', place_text)
                        if place_match:
                            place = int(place_match.group())
                    except (ValueError, AttributeError):
                        place = i + 1  # Если не удалось распарсить, используем порядковый номер
                
                # Сохраняем место как результат (чем меньше место, тем лучше результат)
                # Преобразуем место в результат: 1-е место = max_players, 2-е = max_players-1, и т.д.
                result_value = float(max_players_local - place + 1)
                player_data.append((name, result_value, place))

            if len(player_data) < min_players_local:
                messagebox.showerror(
                    "Недостаточно игроков",
                    f"Для этой игры требуется минимум {min_players_local} игрок(ов).",
                    parent=dialog,
                )
                return

            match_id = f"m{self.match_counter}"
            self.match_counter += 1

            match = Match.create(match_id, game_name, date)

            stored_players = []
            for player_info in player_data:
                if len(player_info) == 3:
                    nm, r_val, place = player_info
                else:
                    nm, r_val = player_info
                    place = 1
                pid = ensure_player_by_name(nm)
                if pid:
                    match.add_result(pid, r_val)
                    # Сохраняем в формате (pid, name, result, place) для совместимости
                    stored_players.append((pid, nm, r_val, place))

            if self.db.add_match(match):
                desc = f"{match_id}: {game_name} ({date})"
                self.matches.append(
                    {
                        "id": match_id,
                        "game": game_name,
                        "date": date,
                        "players": stored_players,
                    }
                )
                self._refresh_matches_list()
                # Обновляем список игроков, так как могли быть добавлены новые игроки
                self._refresh_players_list()
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", f"Не удалось добавить партию. Проверьте корректность данных.", parent=dialog)

        ttk.Button(dialog, text="OK", command=on_ok).grid(row=6, column=0, columnspan=2, pady=5)

    def _on_match_select(self, event=None):
        idx = self.matches_list.curselection()
        if not idx:
            return
        match_id = self.matches_list.get(idx[0]).split(":", 1)[0]
        data = next((m for m in self.matches if m["id"] == match_id), None)
        if not data:
            return
        
        # Получаем информацию о партии из базы данных для получения победителя
        # Пока что используем локальные данные
        lines = [
            f"ID партии: {data['id']}",
            f"Игра: {data['game']}",
            f"Дата: {data['date']}",
            "",
            "Результаты игроков:",
        ]
        
        players_data = data.get("players", [])
        if players_data:
            # Сортируем игроков по месту (если есть) или по результату
            def get_place(player_info):
                if len(player_info) > 3:
                    return player_info[3]  # Место
                return 999  # Если места нет, ставим в конец
            
            sorted_players = sorted(players_data, key=get_place)
            
            for player_info in sorted_players:
                if len(player_info) >= 3:
                    pid, name, res = player_info[0], player_info[1], player_info[2]
                    place = player_info[3] if len(player_info) > 3 else 1
                    
                    # Форматируем место
                    if place == 1:
                        place_text = "1-е место"
                        winner_mark = " 🏆"
                    elif place == 2:
                        place_text = "2-е место"
                        winner_mark = ""
                    elif place == 3:
                        place_text = "3-е место"
                        winner_mark = ""
                    elif place == 4:
                        place_text = "4-е место"
                        winner_mark = ""
                    elif place == 5:
                        place_text = "5-е место"
                        winner_mark = ""
                    elif place == 6:
                        place_text = "6-е место"
                        winner_mark = ""
                    else:
                        place_text = f"{place}-е место"
                        winner_mark = ""
                    
                    lines.append(f"  {place_text}: {name} ({pid}) - результат: {res:.1f}{winner_mark}")
            
            # Победитель (1-е место)
            winner_info = next((p for p in sorted_players if len(p) > 3 and p[3] == 1), None)
            if not winner_info and sorted_players:
                winner_info = sorted_players[0]  # Если нет места, берём первого
            
            if winner_info:
                winner_pid, winner_name = winner_info[0], winner_info[1]
                lines.append("")
                lines.append(f"🏆 Победитель: {winner_name} ({winner_pid})")
        else:
            lines.append("Нет данных об игроках")
            
        self.match_details.delete("1.0", tk.END)
        self.match_details.insert(tk.END, "\n".join(lines))

    def remove_selected_match(self):
        idx = self.matches_list.curselection()
        if not idx:
            return
        line = self.matches_list.get(idx[0])
        match_id = line.split(":", 1)[0]
        if not messagebox.askyesno("Удалить партию", f"Удалить партию {line}?", parent=self):
            return
        # удаляем из C++ базы и локального списка
        if self.db.remove_match(match_id):
            self.matches = [m for m in self.matches if m["id"] != match_id]
            self._refresh_matches_list()
            self.match_details.delete("1.0", tk.END)

    def _refresh_matches_list(self):
        """Обновить список партий с учётом фильтров и сортировки."""
        self.matches_list.delete(0, tk.END)
        
        # Фильтрация
        filter_game = self.match_filter_game_var.get()
        filtered_matches = self.matches
        if filter_game and filter_game != "(все)":
            filtered_matches = [m for m in filtered_matches if m["game"] == filter_game]
        
        # Сортировка
        sort_by = self.match_sort_var.get()
        if sort_by == "дата":
            filtered_matches = sorted(filtered_matches, key=lambda x: x["date"], reverse=True)
        elif sort_by == "игра":
            filtered_matches = sorted(filtered_matches, key=lambda x: x["game"])
        elif sort_by == "игрок":
            # Сортируем по первому игроку
            filtered_matches = sorted(filtered_matches, 
                                     key=lambda x: x["players"][0][1] if x.get("players") else "")
        
        # Обновляем список
        for m in filtered_matches:
            self.matches_list.insert(tk.END, f"{m['id']}: {m['game']} ({m['date']})")
        
        # Обновляем список игр в фильтре
        games = ["(все)"] + [self.games_list.get(i) for i in range(self.games_list.size())]
        self.match_filter_game_combo["values"] = games

    # --- Вкладка "Рекомендации" ---

    def _build_recommendations_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Рекомендации")

        # Верхняя панель: базовая игра и кнопки
        top = ttk.Frame(frame)
        top.pack(fill="x", padx=5, pady=5)

        # Режим одиночной игры
        single_frame = ttk.Frame(top)
        single_frame.pack(side="left", padx=5)

        ttk.Label(single_frame, text="Базовая игра:").pack(side="left")
        self.rec_game_var = tk.StringVar()
        self.rec_game_combo = ttk.Combobox(single_frame, textvariable=self.rec_game_var, width=25)
        self.rec_game_combo.pack(side="left", padx=5)

        ttk.Button(single_frame, text="Рекомендации", command=self.show_recommendations).pack(
            side="left", padx=2
        )
        ttk.Button(single_frame, text="С деталями", command=self.show_detailed_recommendations).pack(
            side="left", padx=2
        )
        ttk.Button(single_frame, text="Связанные игры", command=self.show_related_games).pack(
            side="left", padx=2
        )

        # Режим множественного выбора
        multi_frame = ttk.LabelFrame(top, text="Рекомендации по набору игр")
        multi_frame.pack(side="left", padx=5)

        self.multi_games_listbox = tk.Listbox(multi_frame, height=3, width=25, selectmode=tk.MULTIPLE)
        self.multi_games_listbox.pack(side="left", padx=2)

        ttk.Button(multi_frame, text="Рекомендации\nпо набору", command=self.show_multi_recommendations).pack(
            side="left", padx=2
        )

        # Общие кнопки
        buttons_frame = ttk.Frame(top)
        buttons_frame.pack(side="right", padx=5)

        ttk.Button(buttons_frame, text="Обновить", command=self.refresh_games_combobox).pack(
            side="left", padx=2
        )
        ttk.Button(buttons_frame, text="Только фильтры", command=self.show_filtered_games_only).pack(
            side="left", padx=2
        )
        ttk.Button(buttons_frame, text="Цепочка фильтров", command=self.show_filter_chain).pack(
            side="left", padx=2
        )
        
        # Кнопки экспорта/импорта
        export_frame = ttk.Frame(frame)
        export_frame.pack(fill="x", padx=5, pady=5)
        ttk.Button(export_frame, text="Сохранить рекомендации в файл", 
                  command=self.export_recommendations).pack(side="left", padx=5)
        ttk.Button(export_frame, text="Загрузить рекомендации из файла", 
                  command=self.import_recommendations).pack(side="left", padx=5)

        # Блок фильтров "под компанию и настроение"
        filters = ttk.LabelFrame(frame, text="Фильтры (необязательно)")
        filters.pack(fill="x", padx=5, pady=5)

        self.filter_genre_var = tk.StringVar()
        self.filter_type_var = tk.StringVar()
        self.filter_theme_var = tk.StringVar()
        self.filter_mech_var = tk.StringVar()

        ttk.Label(filters, text="Жанр").grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.filter_genre_cb = ttk.Combobox(filters, textvariable=self.filter_genre_var, state="readonly", width=20)
        self.filter_genre_cb.grid(row=0, column=1, padx=2, pady=2)

        ttk.Label(filters, text="Тип игры").grid(row=0, column=2, sticky="w", padx=2, pady=2)
        self.filter_type_cb = ttk.Combobox(filters, textvariable=self.filter_type_var, state="readonly", width=20)
        self.filter_type_cb.grid(row=0, column=3, padx=2, pady=2)

        ttk.Label(filters, text="Тема").grid(row=1, column=0, sticky="w", padx=2, pady=2)
        self.filter_theme_cb = ttk.Combobox(filters, textvariable=self.filter_theme_var, state="readonly", width=20)
        self.filter_theme_cb.grid(row=1, column=1, padx=2, pady=2)

        ttk.Label(filters, text="Механики (содержит)").grid(row=1, column=2, sticky="w", padx=2, pady=2)
        self.filter_mech_cb = ttk.Combobox(filters, textvariable=self.filter_mech_var, state="readonly", width=20)
        self.filter_mech_cb.grid(row=1, column=3, padx=2, pady=2)

        # Диапазоны численных параметров
        self.filter_min_players = tk.IntVar()
        self.filter_max_players = tk.IntVar()
        self.filter_min_duration = tk.IntVar()
        self.filter_max_duration = tk.IntVar()
        self.filter_min_complexity = tk.DoubleVar()
        self.filter_max_complexity = tk.DoubleVar()

        ttk.Label(filters, text="Игроки от").grid(row=2, column=0, sticky="w", padx=2, pady=2)
        ttk.Spinbox(filters, from_=1, to=20, textvariable=self.filter_min_players, width=5).grid(
            row=2, column=1, sticky="w", padx=2, pady=2
        )
        ttk.Label(filters, text="до").grid(row=2, column=2, sticky="e")
        ttk.Spinbox(filters, from_=1, to=20, textvariable=self.filter_max_players, width=5).grid(
            row=2, column=3, sticky="w", padx=2, pady=2
        )

        ttk.Label(filters, text="Длительность (мин) от").grid(row=3, column=0, sticky="w", padx=2, pady=2)
        ttk.Spinbox(filters, from_=0, to=600, textvariable=self.filter_min_duration, width=5).grid(
            row=3, column=1, sticky="w", padx=2, pady=2
        )
        ttk.Label(filters, text="до").grid(row=3, column=2, sticky="e")
        ttk.Spinbox(filters, from_=0, to=600, textvariable=self.filter_max_duration, width=5).grid(
            row=3, column=3, sticky="w", padx=2, pady=2
        )

        ttk.Label(filters, text="Сложность от").grid(row=4, column=0, sticky="w", padx=2, pady=2)
        ttk.Spinbox(filters, from_=0, to=10, increment=0.5, textvariable=self.filter_min_complexity, width=5).grid(
            row=4, column=1, sticky="w", padx=2, pady=2
        )
        ttk.Label(filters, text="до").grid(row=4, column=2, sticky="e")
        ttk.Spinbox(filters, from_=0, to=10, increment=0.5, textvariable=self.filter_max_complexity, width=5).grid(
            row=4, column=3, sticky="w", padx=2, pady=2
        )

        for col in range(4):
            filters.columnconfigure(col, weight=1)

        self.rec_text = tk.Text(frame, wrap="word")
        self.rec_text.pack(fill="both", expand=True, padx=5, pady=5)

    def refresh_games_combobox(self):
        games = [self.games_list.get(i) for i in range(self.games_list.size())]
        # Добавляем опцию "(без базовой игры)" в начало списка
        games_with_none = ["(без базовой игры)"] + games
        self.rec_game_combo["values"] = games_with_none
        if games and not self.rec_game_var.get():
            self.rec_game_var.set("(без базовой игры)")
        
        # Обновляем список для множественного выбора
        self.multi_games_listbox.delete(0, tk.END)
        for game in games:
            self.multi_games_listbox.insert(tk.END, game)

        # автодополнение по префиксу для базовой игры
        # Удаляем старый обработчик, если есть
        try:
            self.rec_game_combo.unbind("<KeyRelease>")
        except:
            pass
        
        def on_keyrelease(event):
            text = self.rec_game_combo.get()
            # Включаем опцию "(без базовой игры)" в фильтрацию
            all_games = ["(без базовой игры)"] + games
            if text:
                filtered = [g for g in all_games if g.lower().startswith(text.lower())]
            else:
                filtered = all_games
            self.rec_game_combo["values"] = filtered
        self.rec_game_combo.bind("<KeyRelease>", on_keyrelease)

        # Обновляем значения фильтров на основе текущих игр
        genres = set()
        types = set()
        themes = set()
        mechs = set()
        for name in games:
            game = self.db.get_game(name)
            if not game:
                continue
            g = game.get_genre()
            if g:
                genres.add(g)
            t = game.get_game_type()
            if t:
                types.add(t)
            theme = game.get_feature("Тема")
            if theme:
                themes.add(theme)
            m = game.get_mechanics()
            if m:
                mechs.add(m)

        def _values(items):
            vals = sorted(items)
            return ["(любой)"] + vals if vals else ["(любой)"]

        self.filter_genre_cb["values"] = _values(genres)
        self.filter_type_cb["values"] = _values(types)
        self.filter_theme_cb["values"] = _values(themes)
        self.filter_mech_cb["values"] = _values(mechs)

        # Сбрасываем выбранные фильтры
        self.filter_genre_var.set("(любой)")
        self.filter_type_var.set("(любой)")
        self.filter_theme_var.set("(любой)")
        self.filter_mech_var.set("(любой)")
        self.filter_min_players.set(0)
        self.filter_max_players.set(0)
        self.filter_min_duration.set(0)
        self.filter_max_duration.set(0)
        self.filter_min_complexity.set(0.0)
        self.filter_max_complexity.set(0.0)

    def show_recommendations(self):
        base = self.rec_game_var.get()
        
        # Обработка опции "(без базовой игры)"
        if base == "(без базовой игры)":
            base = ""

        # Собираем список всех игр и применяем фильтры
        games = [self.games_list.get(i) for i in range(self.games_list.size())]
        filtered_names = []
        filters_used = False

        # Значения фильтров
        genre_f = self.filter_genre_var.get()
        if genre_f == "(любой)":
            genre_f = ""
        else:
            filters_used = True
        type_f = self.filter_type_var.get()
        if type_f == "(любой)":
            type_f = ""
        else:
            filters_used = True
        theme_f = self.filter_theme_var.get()
        if theme_f == "(любой)":
            theme_f = ""
        else:
            filters_used = True
        mech_f = self.filter_mech_var.get()
        if mech_f == "(любой)":
            mech_f = ""
        else:
            filters_used = True

        min_pl = self.filter_min_players.get() or 0
        max_pl = self.filter_max_players.get() or 0
        min_dur = self.filter_min_duration.get() or 0
        max_dur = self.filter_max_duration.get() or 0
        min_cpl = self.filter_min_complexity.get() or 0.0
        max_cpl = self.filter_max_complexity.get() or 0.0

        if min_pl or max_pl or min_dur or max_dur or min_cpl or max_cpl:
            filters_used = True

        for name in games:
            game = self.db.get_game(name)
            if not game:
                continue

            if genre_f and genre_f not in (game.get_genre() or ""):
                continue
            if type_f and type_f not in (game.get_game_type() or ""):
                continue
            theme = game.get_feature("Тема")
            if theme_f and theme_f not in (theme or ""):
                continue
            if mech_f and mech_f not in (game.get_mechanics() or ""):
                continue

            # Фильтр по количеству игроков
            min_p = game.get_min_players()
            max_p = game.get_max_players()
            if min_pl and max_pl:
                if max_p < min_pl or min_p > max_pl:
                    continue

            # Фильтр по длительности
            dur = game.get_duration()
            if (min_dur and dur and dur < min_dur) or (max_dur and dur and dur > max_dur):
                continue

            # Фильтр по сложности (пытаемся интерпретировать как число)
            cpl_str = game.get_complexity()
            if cpl_str:
                try:
                    cpl_val = float(cpl_str.replace(",", "."))
                except ValueError:
                    cpl_val = 0.0
            else:
                cpl_val = 0.0
            if (min_cpl and cpl_val and cpl_val < min_cpl) or (max_cpl and cpl_val and cpl_val > max_cpl):
                continue

            filtered_names.append(name)

        # Если фильтры были заданы и ничего не найдено, показываем сообщение.
        if filters_used and not filtered_names and not base:
            self.rec_text.delete("1.0", tk.END)
            self.rec_text.insert(
                tk.END,
                "По заданным фильтрам игры не найдены.\n"
                "Попробуйте ослабить ограничения или выбрать другие параметры.",
            )
            return

        allowed = set(filtered_names) if filters_used else set(games)

        self.rec_text.delete("1.0", tk.END)

        # Режим 1: только фильтры, без базовой игры
        if not base and filters_used:
            if not allowed:
                self.rec_text.insert(tk.END, "По заданным фильтрам игры не найдены.")
                return
            for i, name in enumerate(sorted(allowed), start=1):
                game = self.db.get_game(name)
                if not game:
                    continue
                line = (
                    f"{i}. {game.get_name()} — игроки {game.get_min_players()}–{game.get_max_players()}, "
                    f"сложность {game.get_complexity()}, длительность {game.get_duration()} мин, жанр {game.get_genre()}\n"
                )
                self.rec_text.insert(tk.END, line)
            return

        # Режим 2: классические рекомендации от выбранной игры (с учётом фильтров)
        if not base and not filters_used:
            messagebox.showwarning("Нет параметров", "Выберите базовую игру или задайте фильтры.")
            return

        recs = self.db.get_recommendations(base, max_results=20)
        if not recs:
            self.rec_text.insert(tk.END, "Рекомендации не найдены.")
            return

        shown = 0
        for i, game in enumerate(recs, start=1):
            if game.get_name() not in allowed:
                continue
            line = (
                f"{shown + 1}. {game.get_name()} — игроки {game.get_min_players()}–{game.get_max_players()}, "
                f"сложность {game.get_complexity()}, длительность {game.get_duration()} мин, жанр {game.get_genre()}\n"
            )
            self.rec_text.insert(tk.END, line)
            shown += 1

        if shown == 0:
            self.rec_text.insert(
                tk.END,
                "Игры, удовлетворяющие фильтрам и рекомендациям, не найдены.\n"
                "Показаны бы были игры: " + ", ".join(sorted(allowed)),
            )

    def show_multi_recommendations(self):
        """Показать рекомендации на основе нескольких базовых игр."""
        selected_indices = self.multi_games_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Не выбраны игры", "Выберите хотя бы одну игру из списка для рекомендаций.")
            return

        selected_games = [self.multi_games_listbox.get(i) for i in selected_indices]
        
        self.rec_text.delete("1.0", tk.END)
        self.rec_text.insert(tk.END, f"Рекомендации на основе игр: {', '.join(selected_games)}\n\n")

        # Собираем рекомендации для каждой игры и объединяем
        all_recommendations = {}  # game_name -> (count, similarity_sum)
        
        for base_game in selected_games:
            recs = self.db.get_recommendations(base_game, max_results=20)
            for game in recs:
                name = game.get_name()
                if name not in selected_games:  # Исключаем базовые игры
                    if name not in all_recommendations:
                        all_recommendations[name] = {"count": 0, "game": game}
                    all_recommendations[name]["count"] += 1

        if not all_recommendations:
            self.rec_text.insert(tk.END, "Рекомендации не найдены.")
            return

        # Сортируем по количеству упоминаний (игры, рекомендованные для нескольких базовых игр, выше)
        sorted_recs = sorted(all_recommendations.items(), key=lambda x: x[1]["count"], reverse=True)

        shown = 0
        for name, data in sorted_recs[:20]:  # Показываем топ-20
            game = data["game"]
            count = data["count"]
            count_text = f" (рекомендовано для {count} из {len(selected_games)} игр)" if count > 1 else ""
            line = (
                f"{shown + 1}. {game.get_name()}{count_text} — игроки {game.get_min_players()}–{game.get_max_players()}, "
                f"сложность {game.get_complexity()}, длительность {game.get_duration()} мин, жанр {game.get_genre()}\n"
            )
            self.rec_text.insert(tk.END, line)
            shown += 1

    def show_related_games(self):
        """Показать все игры, связанные с выбранной базовой игрой."""
        base = self.rec_game_var.get().strip()
        
        # Обработка опции "(без базовой игры)"
        if not base or base == "(без базовой игры)":
            messagebox.showwarning("Не выбрана игра", "Выберите базовую игру из списка.")
            return
        
        # Проверяем, существует ли игра в базе данных
        base_game = self.db.get_game(base)
        if not base_game:
            messagebox.showerror("Ошибка", f"Игра '{base}' не найдена в базе данных.")
            return
        
        # Находим все игры, связанные с базовой игрой
        related_games = []
        all_games = [self.games_list.get(i) for i in range(self.games_list.size())]
        
        for game_name in all_games:
            if game_name != base:
                # Проверяем связь в обоих направлениях (A-B и B-A)
                if self.db.are_similar(base, game_name):
                    related_games.append(game_name)
        
        # Выводим результаты
        self.rec_text.delete("1.0", tk.END)
        
        if related_games:
            self.rec_text.insert(tk.END, f"Игры, связанные с '{base}':\n")
            self.rec_text.insert(tk.END, "=" * 60 + "\n\n")
            
            for i, game_name in enumerate(sorted(related_games), 1):
                game = self.db.get_game(game_name)
                if game:
                    rating = game.get_average_rating()
                    rating_str = f" (рейтинг: {rating:.2f})" if rating > 0 else ""
                    self.rec_text.insert(tk.END, f"{i}. {game_name}{rating_str}\n")
                    
                    # Дополнительная информация об игре
                    if game.get_genre():
                        self.rec_text.insert(tk.END, f"   Жанр: {game.get_genre()}\n")
                    if game.get_game_type():
                        self.rec_text.insert(tk.END, f"   Тип: {game.get_game_type()}\n")
                    if game.get_complexity():
                        self.rec_text.insert(tk.END, f"   Сложность: {game.get_complexity()}\n")
                    self.rec_text.insert(tk.END, "\n")
            
            self.rec_text.insert(tk.END, f"\nВсего найдено связанных игр: {len(related_games)}\n")
        else:
            self.rec_text.insert(tk.END, f"Для игры '{base}' не найдено связанных игр.\n\n")
            self.rec_text.insert(tk.END, "Чтобы добавить связи, используйте:\n")
            self.rec_text.insert(tk.END, "Игры → Управление похожими играми\n")

    def show_detailed_recommendations(self):
        """Показать рекомендации с детализацией вклада параметров."""
        base = self.rec_game_var.get()
        if not base:
            messagebox.showwarning("Не выбрана игра", "Выберите базовую игру для рекомендаций.")
            return

        self.rec_text.delete("1.0", tk.END)
        self.rec_text.insert(tk.END, f"Детализированные рекомендации для игры: {base}\n")
        self.rec_text.insert(tk.END, "=" * 60 + "\n\n")

        # Получаем обычные рекомендации (getDetailedRecommendations требует C API)
        recs = self.db.get_recommendations(base, max_results=10)
        if not recs:
            self.rec_text.insert(tk.END, "Рекомендации не найдены.")
            return

        # Показываем рекомендации с дополнительной информацией
        for i, game in enumerate(recs, start=1):
            self.rec_text.insert(tk.END, f"{i}. {game.get_name()}\n")
            self.rec_text.insert(tk.END, f"   Игроки: {game.get_min_players()}–{game.get_max_players()}\n")
            self.rec_text.insert(tk.END, f"   Сложность: {game.get_complexity()}\n")
            self.rec_text.insert(tk.END, f"   Длительность: {game.get_duration()} мин\n")
            self.rec_text.insert(tk.END, f"   Жанр: {game.get_genre()}\n")
            self.rec_text.insert(tk.END, f"   Тип: {game.get_game_type()}\n")
            self.rec_text.insert(tk.END, f"   Механики: {game.get_mechanics()}\n")
            
            # Сравнение с базовой игрой
            base_game = self.db.get_game(base)
            if base_game:
                self.rec_text.insert(tk.END, "   Сравнение с базовой игрой:\n")
                if game.get_genre() == base_game.get_genre() and game.get_genre():
                    self.rec_text.insert(tk.END, "   ✓ Одинаковый жанр\n")
                if game.get_game_type() == base_game.get_game_type() and game.get_game_type():
                    self.rec_text.insert(tk.END, "   ✓ Одинаковый тип игры\n")
                # Проверка диапазона игроков
                if (game.get_min_players() <= base_game.get_max_players() and 
                    game.get_max_players() >= base_game.get_min_players()):
                    self.rec_text.insert(tk.END, "   ✓ Пересекающийся диапазон игроков\n")
            
            avg_rating = game.get_average_rating()
            if avg_rating > 0:
                self.rec_text.insert(tk.END, f"   Средний рейтинг: {avg_rating:.2f}\n")
            
            self.rec_text.insert(tk.END, "\n")

            self.rec_text.insert(tk.END, "\n")
            self.rec_text.insert(tk.END, "Примечание: Для полной детализации вклада параметров требуется\n")
            self.rec_text.insert(tk.END, "метод getDetailedRecommendations в C API.\n")

    def export_recommendations(self):
        """Экспортировать рекомендации в файл."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")],
            title="Сохранить рекомендации"
        )
        if not filename:
            return

        try:
            # Собираем рекомендации для всех игр
            recommendations_data = {}
            games = [self.games_list.get(i) for i in range(self.games_list.size())]
            
            for game_name in games:
                recs = self.db.get_recommendations(game_name, max_results=10)
                if recs:
                    recommendations_data[game_name] = [
                        {
                            "name": game.get_name(),
                            "players": f"{game.get_min_players()}-{game.get_max_players()}",
                            "complexity": game.get_complexity(),
                            "duration": game.get_duration(),
                            "genre": game.get_genre(),
                            "type": game.get_game_type(),
                            "mechanics": game.get_mechanics(),
                            "rating": game.get_average_rating(),
                        }
                        for game in recs
                    ]

            # Сохраняем в JSON
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(recommendations_data, f, ensure_ascii=False, indent=2)

            messagebox.showinfo("Успех", f"Рекомендации сохранены в файл:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить рекомендации:\n{str(e)}")

    def import_recommendations(self):
        """Импортировать рекомендации из файла."""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")],
            title="Загрузить рекомендации"
        )
        if not filename:
            return

        try:
            with open(filename, "r", encoding="utf-8") as f:
                recommendations_data = json.load(f)

            # Показываем информацию о загруженных рекомендациях
            total_games = len(recommendations_data)
            total_recs = sum(len(recs) for recs in recommendations_data.values())
            
            messagebox.showinfo(
                "Успех",
                f"Рекомендации загружены из файла:\n{filename}\n\n"
                f"Игр с рекомендациями: {total_games}\n"
                f"Всего рекомендаций: {total_recs}\n\n"
                "Примечание: Для полного импорта требуется метод importRecommendations в C API."
            )
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить рекомендации:\n{str(e)}")

    def show_filter_chain(self):
        """Применить цепочку фильтров (рейтинг, признаки, схожесть)."""
        dialog = tk.Toplevel(self)
        dialog.title("Цепочка фильтров")
        dialog.geometry("500x400")

        ttk.Label(dialog, text="Выберите фильтры для применения:", 
                 font=("Segoe UI", 10, "bold")).pack(pady=10)

        # Фильтр по рейтингу
        rating_frame = ttk.LabelFrame(dialog, text="Фильтр по рейтингу")
        rating_frame.pack(fill="x", padx=10, pady=5)

        chain_use_rating = tk.BooleanVar(value=False)
        ttk.Checkbutton(rating_frame, text="Использовать фильтр по рейтингу", 
                       variable=chain_use_rating).pack(anchor="w", padx=5, pady=2)
        
        ttk.Label(rating_frame, text="Минимальный рейтинг:").pack(anchor="w", padx=5, pady=2)
        chain_min_rating = tk.DoubleVar(value=3.0)
        ttk.Scale(rating_frame, from_=1.0, to=5.0, orient="horizontal",
                 variable=chain_min_rating).pack(fill="x", padx=5, pady=2)

        # Фильтр по признакам
        feature_frame = ttk.LabelFrame(dialog, text="Фильтр по признакам")
        feature_frame.pack(fill="x", padx=10, pady=5)

        chain_use_feature = tk.BooleanVar(value=False)
        ttk.Checkbutton(feature_frame, text="Использовать фильтр по признакам", 
                       variable=chain_use_feature).pack(anchor="w", padx=5, pady=2)
        
        ttk.Label(feature_frame, text="Название признака:").pack(anchor="w", padx=5, pady=2)
        chain_feature_name = tk.StringVar()
        ttk.Entry(feature_frame, textvariable=chain_feature_name, width=30).pack(fill="x", padx=5, pady=2)
        
        ttk.Label(feature_frame, text="Значение признака:").pack(anchor="w", padx=5, pady=2)
        chain_feature_value = tk.StringVar()
        ttk.Entry(feature_frame, textvariable=chain_feature_value, width=30).pack(fill="x", padx=5, pady=2)

        # Фильтр по схожести
        similarity_frame = ttk.LabelFrame(dialog, text="Фильтр по схожести")
        similarity_frame.pack(fill="x", padx=10, pady=5)

        chain_use_similarity = tk.BooleanVar(value=False)
        ttk.Checkbutton(similarity_frame, text="Использовать фильтр по схожести", 
                       variable=chain_use_similarity).pack(anchor="w", padx=5, pady=2)
        
        ttk.Label(similarity_frame, text="Базовая игра для схожести:").pack(anchor="w", padx=5, pady=2)
        chain_similarity_game = tk.StringVar()
        chain_game_combo = ttk.Combobox(similarity_frame, textvariable=chain_similarity_game, width=30)
        games_list = [self.games_list.get(i) for i in range(self.games_list.size())]
        chain_game_combo["values"] = games_list
        chain_game_combo.pack(fill="x", padx=5, pady=2)

        def apply_chain():
            """Применить цепочку фильтров."""
            games = [self.games_list.get(i) for i in range(self.games_list.size())]
            filtered_games = games.copy()

            # Применяем фильтры последовательно
            if chain_use_rating.get():
                min_rating = chain_min_rating.get()
                filtered_games = [
                    name for name in filtered_games
                    if self.db.get_game(name) and 
                    self.db.get_game(name).get_average_rating() >= min_rating
                ]

            if chain_use_feature.get() and filtered_games:
                feature_name = chain_feature_name.get().strip()
                feature_value = chain_feature_value.get().strip()
                if feature_name and feature_value:
                    filtered_games = [
                        name for name in filtered_games
                        if self.db.get_game(name) and 
                        self.db.get_game(name).get_feature(feature_name) == feature_value
                    ]

            if chain_use_similarity.get() and filtered_games:
                base_game = chain_similarity_game.get().strip()
                if base_game:
                    filtered_games = [
                        name for name in filtered_games
                        if name != base_game and self.db.are_similar(name, base_game)
                    ]

            # Показываем результаты
            self.rec_text.delete("1.0", tk.END)
            if filtered_games:
                self.rec_text.insert(tk.END, f"Результаты цепочки фильтров ({len(filtered_games)} игр):\n\n")
                for i, name in enumerate(sorted(filtered_games), start=1):
                    game = self.db.get_game(name)
                    if game:
                        line = (
                            f"{i}. {game.get_name()} — игроки {game.get_min_players()}–{game.get_max_players()}, "
                            f"сложность {game.get_complexity()}, рейтинг {game.get_average_rating():.2f}\n"
                        )
                        self.rec_text.insert(tk.END, line)
            else:
                self.rec_text.insert(tk.END, "По заданной цепочке фильтров игры не найдены.")

            dialog.destroy()

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(btn_frame, text="Применить", command=apply_chain).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side="right", padx=5)

    def show_filtered_games_only(self):
        """Показать игры только по фильтрам, без использования движка схожести."""
        # Собираем список всех игр и применяем фильтры
        games = [self.games_list.get(i) for i in range(self.games_list.size())]
        filtered_names = []

        # Значения фильтров
        genre_f = self.filter_genre_var.get()
        if genre_f == "(любой)":
            genre_f = ""
        type_f = self.filter_type_var.get()
        if type_f == "(любой)":
            type_f = ""
        theme_f = self.filter_theme_var.get()
        if theme_f == "(любой)":
            theme_f = ""
        mech_f = self.filter_mech_var.get()
        if mech_f == "(любой)":
            mech_f = ""

        min_pl = self.filter_min_players.get() or 0
        max_pl = self.filter_max_players.get() or 0
        min_dur = self.filter_min_duration.get() or 0
        max_dur = self.filter_max_duration.get() or 0
        min_cpl = self.filter_min_complexity.get() or 0.0
        max_cpl = self.filter_max_complexity.get() or 0.0

        for name in games:
            game = self.db.get_game(name)
            if not game:
                continue

            if genre_f and genre_f not in (game.get_genre() or ""):
                continue
            if type_f and type_f not in (game.get_game_type() or ""):
                continue
            theme = game.get_feature("Тема")
            if theme_f and theme_f not in (theme or ""):
                continue
            if mech_f and mech_f not in (game.get_mechanics() or ""):
                continue

            # Фильтр по количеству игроков
            min_p = game.get_min_players()
            max_p = game.get_max_players()
            if min_pl and max_pl:
                if max_p < min_pl or min_p > max_pl:
                    continue

            # Фильтр по длительности
            dur = game.get_duration()
            if (min_dur and dur and dur < min_dur) or (max_dur and dur and dur > max_dur):
                continue

            # Фильтр по сложности
            cpl_str = game.get_complexity()
            if cpl_str:
                try:
                    cpl_val = float(cpl_str.replace(",", "."))
                except ValueError:
                    cpl_val = 0.0
            else:
                cpl_val = 0.0
            if (min_cpl and cpl_val and cpl_val < min_cpl) or (max_cpl and cpl_val and cpl_val > max_cpl):
                continue

            filtered_names.append(name)

        self.rec_text.delete("1.0", tk.END)

        if not filtered_names:
            self.rec_text.insert(tk.END, "По заданным фильтрам игры не найдены.\n"
                              "Попробуйте ослабить ограничения или выбрать другие параметры.")
            return

        # Сортируем по среднему рейтингу (если есть)
        games_with_ratings = []
        for name in filtered_names:
            game = self.db.get_game(name)
            if game:
                avg_rating = game.get_average_rating()
                games_with_ratings.append((name, game, avg_rating))

        # Сортируем по рейтингу (убывание)
        games_with_ratings.sort(key=lambda x: x[2], reverse=True)

        for i, (name, game, rating) in enumerate(games_with_ratings, start=1):
            rating_str = f" (рейтинг: {rating:.2f})" if rating > 0 else ""
            line = (
                f"{i}. {game.get_name()}{rating_str} — игроки {game.get_min_players()}–{game.get_max_players()}, "
                f"сложность {game.get_complexity()}, длительность {game.get_duration()} мин, жанр {game.get_genre()}\n"
            )
            self.rec_text.insert(tk.END, line)

    # --- Вкладка "Статистика" ---

    def _build_statistics_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Статистика")

        # Выбор игрока для статистики
        top_frame = ttk.Frame(frame)
        top_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(top_frame, text="Игрок:").pack(side="left", padx=5)
        self.stats_player_var = tk.StringVar()
        self.stats_player_combo = ttk.Combobox(top_frame, textvariable=self.stats_player_var, width=30)
        self.stats_player_combo.pack(side="left", padx=5)
        
        # Настройка автозаполнения для списка игроков
        def setup_player_autocomplete():
            def on_keyrelease(event):
                text = self.stats_player_combo.get()
                player_values = [f"{name} ({pid})" for pid, name in self.players.items()]
                if text:
                    filtered = [v for v in player_values if text.lower() in v.lower()]
                else:
                    filtered = player_values
                self.stats_player_combo["values"] = filtered
            self.stats_player_combo.bind("<KeyRelease>", on_keyrelease)
        
        setup_player_autocomplete()
        ttk.Button(top_frame, text="Показать статистику", command=self.show_player_statistics).pack(
            side="left", padx=5
        )
        ttk.Button(top_frame, text="Общая статистика", command=self.show_general_statistics).pack(
            side="left", padx=5
        )

        # Область вывода статистики
        self.stats_text = tk.Text(frame, wrap="word", font=("Consolas", 10))
        self.stats_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Обновляем список игроков
        self._update_stats_players_list()

    def _update_stats_players_list(self):
        """Обновить список игроков для статистики."""
        player_values = [f"{name} ({pid})" for pid, name in self.players.items()]
        self.stats_player_combo["values"] = player_values
        # Обновляем автозаполнение
        def on_keyrelease(event):
            text = self.stats_player_combo.get()
            if text:
                filtered = [v for v in player_values if text.lower() in v.lower()]
            else:
                filtered = player_values
            self.stats_player_combo["values"] = filtered
        # Удаляем старые обработчики и добавляем новый
        self.stats_player_combo.unbind("<KeyRelease>")
        self.stats_player_combo.bind("<KeyRelease>", on_keyrelease)

    def show_player_statistics(self):
        """Показать статистику выбранного игрока."""
        player_text = self.stats_player_var.get().strip()
        if not player_text:
            messagebox.showwarning("Не выбран игрок", "Выберите игрока из списка.")
            return

        # Извлекаем ID игрока
        if "(" in player_text and player_text.endswith(")"):
            player_id = player_text.rsplit("(", 1)[1][:-1].strip()
            player_name = player_text.rsplit("(", 1)[0].strip()
        else:
            player_id = self._find_player_id_by_name(player_text)
            if not player_id:
                messagebox.showerror("Ошибка", f"Игрок '{player_text}' не найден.")
                return
            player_name = player_text

        self.stats_text.delete("1.0", tk.END)
        stats_lines = [
            f"=== Статистика игрока: {player_name} ({player_id}) ===\n",
            "",
        ]

        # Игры, в которые играл игрок
        player_games = []
        for match in self.matches:
            for player_info in match.get("players", []):
                # Поддерживаем старый формат (pid, name, result) и новый (pid, name, result, place)
                if len(player_info) >= 3:
                    pid, name, result = player_info[0], player_info[1], player_info[2]
                    if pid == player_id:
                        game_name = match["game"]
                        if game_name not in [g[0] for g in player_games]:
                            # Получаем рейтинг игрока в этой игре
                            rating = self.db.get_player_rating_in_game(player_id, game_name)
                            player_games.append((game_name, rating))

        if player_games:
            stats_lines.append("Игры, в которые играл игрок:")
            stats_lines.append("-" * 50)
            for i, (game_name, rating) in enumerate(sorted(player_games, key=lambda x: x[1], reverse=True), start=1):
                rating_str = f" (рейтинг: {rating:.2f})" if rating > 0 else ""
                stats_lines.append(f"{i}. {game_name}{rating_str}")
            stats_lines.append("")
        else:
            stats_lines.append("Игрок ещё не играл ни в одну игру.")
            stats_lines.append("")

        # Партии игрока
        player_matches = [m for m in self.matches 
                         if any(len(p) >= 1 and p[0] == player_id for p in m.get("players", []))]
        if player_matches:
            stats_lines.append(f"Всего партий: {len(player_matches)}")
            stats_lines.append("-" * 50)
            for match in sorted(player_matches, key=lambda x: x["date"], reverse=True)[:10]:
                # Находим результат игрока в этой партии
                player_result = None
                for player_info in match.get("players", []):
                    # Поддерживаем старый формат (pid, name, result) и новый (pid, name, result, place)
                    if len(player_info) >= 3:
                        pid, name, result = player_info[0], player_info[1], player_info[2]
                        if pid == player_id:
                            player_result = result
                            break
                result_str = f" (результат: {player_result:.1f})" if player_result is not None else ""
                stats_lines.append(f"{match['date']}: {match['game']}{result_str}")
            if len(player_matches) > 10:
                stats_lines.append(f"... и ещё {len(player_matches) - 10} партий")
            stats_lines.append("")

        self.stats_text.insert("1.0", "\n".join(stats_lines))

    def show_general_statistics(self):
        """Показать общую статистику базы данных."""
        self.stats_text.delete("1.0", tk.END)
        stats_lines = [
            "=== Общая статистика базы данных ===\n",
            "",
        ]

        # Статистика по играм
        games_count = self.games_list.size()
        stats_lines.append(f"Всего игр: {games_count}")
        
        # Игры с рейтингами
        games_with_ratings = 0
        total_ratings = 0
        for i in range(games_count):
            game_name = self.games_list.get(i)
            game = self.db.get_game(game_name)
            if game:
                ratings_count = game.get_ratings_count()
                if ratings_count > 0:
                    games_with_ratings += 1
                    total_ratings += ratings_count

        stats_lines.append(f"Игр с оценками: {games_with_ratings}")
        if games_with_ratings > 0:
            stats_lines.append(f"Всего оценок: {total_ratings}")
            stats_lines.append(f"Среднее количество оценок на игру: {total_ratings / games_with_ratings:.1f}")
        stats_lines.append("")

        # Статистика по игрокам
        players_count = len(self.players)
        stats_lines.append(f"Всего игроков: {players_count}")
        stats_lines.append("")

        # Статистика по партиям
        matches_count = len(self.matches)
        stats_lines.append(f"Всего партий: {matches_count}")
        if matches_count > 0:
            # Игры по популярности
            game_popularity = {}
            for match in self.matches:
                game_name = match["game"]
                game_popularity[game_name] = game_popularity.get(game_name, 0) + 1
            
            stats_lines.append("")
            stats_lines.append("Самые популярные игры:")
            stats_lines.append("-" * 50)
            for i, (game_name, count) in enumerate(
                sorted(game_popularity.items(), key=lambda x: x[1], reverse=True)[:10], 
                start=1
            ):
                stats_lines.append(f"{i}. {game_name} — {count} партий")
        stats_lines.append("")

        # Статистика рекомендаций
        try:
            rec_stats = self.db.get_recommendation_stats()
            if rec_stats:
                stats_lines.append("=== Статистика рекомендаций ===")
                stats_lines.append(f"Всего игр: {rec_stats.get('total_games', 0)}")
                stats_lines.append(f"Игр с рекомендациями: {rec_stats.get('games_with_recommendations', 0)}")
                stats_lines.append(f"Среднее количество рекомендаций: {rec_stats.get('average_recommendations_per_game', 0):.2f}")
                stats_lines.append(f"Средний балл схожести: {rec_stats.get('average_similarity_score', 0):.2f}")
        except Exception:
            pass

        self.stats_text.insert("1.0", "\n".join(stats_lines))

    # --- Общее ---

    def show_report(self):
        """Показать окно отчёта с детальной аналитикой и статистикой."""
        report_window = tk.Toplevel(self)
        report_window.title("Детальный отчёт по базе данных")
        report_window.geometry("900x700")

        notebook = ttk.Notebook(report_window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Вкладка "Общая статистика"
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="Общая статистика")

        general_text = tk.Text(general_frame, wrap="word", font=("Consolas", 9))
        general_text.pack(fill="both", expand=True, padx=5, pady=5)

        general_lines = ["=== ОБЩАЯ СТАТИСТИКА БАЗЫ ДАННЫХ ===\n\n"]
        
        # Статистика по играм
        games_count = self.games_list.size()
        general_lines.append(f"📊 Всего игр в базе: {games_count}\n")
        
        # Игры с рейтингами
        games_with_ratings = 0
        total_ratings = 0
        games_ratings = []
        for i in range(games_count):
            game_name = self.games_list.get(i)
            game = self.db.get_game(game_name)
            if game:
                ratings_count = game.get_ratings_count()
                if ratings_count > 0:
                    games_with_ratings += 1
                    total_ratings += ratings_count
                    avg_rating = game.get_average_rating()
                    games_ratings.append((game_name, avg_rating, ratings_count))

        general_lines.append(f"⭐ Игр с оценками: {games_with_ratings}")
        if games_with_ratings > 0:
            general_lines.append(f"📝 Всего оценок: {total_ratings}")
            general_lines.append(f"📈 Среднее количество оценок на игру: {total_ratings / games_with_ratings:.1f}\n")
            
            # Топ игр по рейтингу
            games_ratings.sort(key=lambda x: x[1], reverse=True)
            general_lines.append("🏆 Топ-5 игр по рейтингу:")
            for i, (name, rating, count) in enumerate(games_ratings[:5], start=1):
                general_lines.append(f"   {i}. {name} — {rating:.2f} ({count} оценок)")

        general_lines.append("\n")

        # Статистика по игрокам
        players_count = len(self.players)
        general_lines.append(f"👥 Всего игроков: {players_count}\n")

        # Статистика по партиям
        matches_count = len(self.matches)
        general_lines.append(f"🎲 Всего партий: {matches_count}")
        if matches_count > 0:
            # Игры по популярности
            game_popularity = {}
            for match in self.matches:
                game_name = match["game"]
                game_popularity[game_name] = game_popularity.get(game_name, 0) + 1
            
            general_lines.append("\n📊 Самые популярные игры:")
            for i, (game_name, count) in enumerate(
                sorted(game_popularity.items(), key=lambda x: x[1], reverse=True)[:10], 
                start=1
            ):
                general_lines.append(f"   {i}. {game_name} — {count} партий")

        general_lines.append("\n")

        # Статистика рекомендаций
        try:
            rec_stats = self.db.get_recommendation_stats()
            if rec_stats:
                general_lines.append("=== СТАТИСТИКА СИСТЕМЫ РЕКОМЕНДАЦИЙ ===\n")
                general_lines.append(f"Всего игр: {rec_stats.get('total_games', 0)}\n")
                general_lines.append(f"Игр с рекомендациями: {rec_stats.get('games_with_recommendations', 0)}\n")
                general_lines.append(f"Среднее количество рекомендаций: {rec_stats.get('average_recommendations_per_game', 0):.2f}\n")
                general_lines.append(f"Средний балл схожести: {rec_stats.get('average_similarity_score', 0):.2f}\n")
        except Exception:
            pass

        general_text.insert("1.0", "\n".join(general_lines))

        # Вкладка "Анализ игры"
        analysis_frame = ttk.Frame(notebook)
        notebook.add(analysis_frame, text="Анализ игры")

        top_frame = ttk.Frame(analysis_frame)
        top_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(top_frame, text="Игра:").pack(side="left", padx=5)
        report_game_var = tk.StringVar()
        report_game_combo = ttk.Combobox(top_frame, textvariable=report_game_var, width=30)
        games_list = [self.games_list.get(i) for i in range(self.games_list.size())]
        report_game_combo["values"] = games_list
        if games_list:
            report_game_var.set(games_list[0])
        report_game_combo.pack(side="left", padx=5)

        analysis_text = tk.Text(analysis_frame, wrap="word", font=("Consolas", 9))
        analysis_text.pack(fill="both", expand=True, padx=5, pady=5)

        def show_game_analysis():
            game_name = report_game_var.get()
            if not game_name:
                return
            game = self.db.get_game(game_name)
            if not game:
                return

            analysis_text.delete("1.0", tk.END)
            lines = [f"=== ДЕТАЛЬНЫЙ АНАЛИЗ ИГРЫ: {game_name} ===\n\n"]

            # Основная информация
            lines.append("📋 ОСНОВНАЯ ИНФОРМАЦИЯ:")
            lines.append(f"   Название: {game.get_name()}")
            lines.append(f"   Описание: {game.get_description()}")
            lines.append(f"   Игроки: {game.get_min_players()}–{game.get_max_players()}")
            lines.append(f"   Сложность: {game.get_complexity()}")
            lines.append(f"   Длительность: {game.get_duration()} мин")
            lines.append(f"   Тип игры: {game.get_game_type()}")
            lines.append(f"   Жанр: {game.get_genre()}")
            lines.append(f"   Механики: {game.get_mechanics()}")
            lines.append("")

            # Рейтинги
            avg_rating = game.get_average_rating()
            ratings_count = game.get_ratings_count()
            if ratings_count > 0:
                lines.append(f"⭐ РЕЙТИНГИ:")
                lines.append(f"   Средний рейтинг: {avg_rating:.2f}")
                lines.append(f"   Количество оценок: {ratings_count}")
                lines.append("")

            # Рекомендации
            lines.append("🔍 РЕКОМЕНДАЦИИ:")
            recs = self.db.get_recommendations(game_name, max_results=10)
            if recs:
                lines.append(f"   Найдено рекомендаций: {len(recs)}")
                lines.append("   Топ-5 рекомендаций:")
                for i, rec_game in enumerate(recs[:5], start=1):
                    rec_rating = rec_game.get_average_rating()
                    rating_str = f" (рейтинг: {rec_rating:.2f})" if rec_rating > 0 else ""
                    lines.append(f"      {i}. {rec_game.get_name()}{rating_str}")
            else:
                lines.append("   Рекомендации не найдены")
            lines.append("")

            # Партии
            game_matches = [m for m in self.matches if m["game"] == game_name]
            if game_matches:
                lines.append(f"🎲 ПАРТИИ:")
                lines.append(f"   Всего партий: {len(game_matches)}")
                lines.append("   Последние партии:")
                for match in sorted(game_matches, key=lambda x: x["date"], reverse=True)[:5]:
                    lines.append(f"      {match['date']}: {len(match.get('players', []))} игроков")
            else:
                lines.append("🎲 ПАРТИИ: Партий не было")

            analysis_text.insert("1.0", "\n".join(lines))

        ttk.Button(top_frame, text="Показать анализ", command=show_game_analysis).pack(side="left", padx=5)
        show_game_analysis()

        # Вкладка "Сравнение игр"
        compare_frame = ttk.Frame(notebook)
        notebook.add(compare_frame, text="Сравнение игр")

        compare_top = ttk.Frame(compare_frame)
        compare_top.pack(fill="x", padx=5, pady=5)

        ttk.Label(compare_top, text="Игра 1:").pack(side="left", padx=5)
        compare_game1_var = tk.StringVar()
        compare_game1_combo = ttk.Combobox(compare_top, textvariable=compare_game1_var, width=25)
        compare_game1_combo["values"] = games_list
        compare_game1_combo.pack(side="left", padx=5)

        ttk.Label(compare_top, text="Игра 2:").pack(side="left", padx=5)
        compare_game2_var = tk.StringVar()
        compare_game2_combo = ttk.Combobox(compare_top, textvariable=compare_game2_var, width=25)
        compare_game2_combo["values"] = games_list
        if len(games_list) > 1:
            compare_game2_var.set(games_list[1])
        compare_game2_combo.pack(side="left", padx=5)

        compare_text = tk.Text(compare_frame, wrap="word", font=("Consolas", 9))
        compare_text.pack(fill="both", expand=True, padx=5, pady=5)

        def show_comparison():
            game1_name = compare_game1_var.get()
            game2_name = compare_game2_var.get()
            if not game1_name or not game2_name:
                return
            game1 = self.db.get_game(game1_name)
            game2 = self.db.get_game(game2_name)
            if not game1 or not game2:
                return

            compare_text.delete("1.0", tk.END)
            lines = [f"=== СРАВНЕНИЕ ИГР ===\n"]
            lines.append(f"{game1_name} vs {game2_name}\n\n")

            # Сравнение параметров
            def compare_param(label, val1, val2):
                lines.append(f"{label}:")
                lines.append(f"   {game1_name}: {val1}")
                lines.append(f"   {game2_name}: {val2}")
                if val1 == val2:
                    lines.append("   ✓ Одинаковые")
                lines.append("")

            compare_param("Игроки", 
                        f"{game1.get_min_players()}–{game1.get_max_players()}",
                        f"{game2.get_min_players()}–{game2.get_max_players()}")
            compare_param("Сложность", game1.get_complexity(), game2.get_complexity())
            compare_param("Длительность", f"{game1.get_duration()} мин", f"{game2.get_duration()} мин")
            compare_param("Жанр", game1.get_genre() or "не указан", game2.get_genre() or "не указан")
            compare_param("Тип игры", game1.get_game_type() or "не указан", game2.get_game_type() or "не указан")

            # Схожесть
            are_similar = self.db.are_similar(game1_name, game2_name)
            lines.append("Схожесть:")
            lines.append(f"   {'✓ Игры похожи' if are_similar else '✗ Игры не похожи'}")
            lines.append("")

            # Рейтинги
            rating1 = game1.get_average_rating()
            rating2 = game2.get_average_rating()
            if rating1 > 0 or rating2 > 0:
                lines.append("Рейтинги:")
                lines.append(f"   {game1_name}: {rating1:.2f}" if rating1 > 0 else f"   {game1_name}: нет оценок")
                lines.append(f"   {game2_name}: {rating2:.2f}" if rating2 > 0 else f"   {game2_name}: нет оценок")

            compare_text.insert("1.0", "\n".join(lines))

        ttk.Button(compare_top, text="Сравнить", command=show_comparison).pack(side="left", padx=5)
        if len(games_list) > 1:
            show_comparison()

    def run_tests(self):
        """Запустить тесты через Python API и показать результаты."""
        test_window = tk.Toplevel(self)
        test_window.title("Тесты модели")
        test_window.geometry("800x600")

        # Верхняя панель с кнопками
        top_frame = ttk.Frame(test_window)
        top_frame.pack(fill="x", padx=10, pady=5)

        test_text = tk.Text(test_window, wrap="word", font=("Consolas", 9))
        test_text.pack(fill="both", expand=True, padx=10, pady=5)

        def run_python_tests():
            """Запустить тесты через Python API."""
            test_text.delete("1.0", tk.END)
            test_text.insert("1.0", "Запуск тестов через Python API...\n")
            test_text.insert(tk.END, "=" * 70 + "\n\n")

            test_results = []
            
            # Тест 1: Проверка базы данных
            try:
                games_count = self.db.games_count()
                test_results.append(("✓", "База данных", f"Игр в базе: {games_count}"))
            except Exception as e:
                test_results.append(("✗", "База данных", f"Ошибка: {str(e)}"))

            # Тест 2: Проверка рекомендаций
            try:
                games = [self.games_list.get(i) for i in range(self.games_list.size())]
                if games:
                    test_game = games[0]
                    recs = self.db.get_recommendations(test_game, max_results=5)
                    test_results.append(("✓", "Система рекомендаций", 
                                       f"Рекомендации для '{test_game}': {len(recs)} результатов"))
                else:
                    test_results.append(("⚠", "Система рекомендаций", "Нет игр для тестирования"))
            except Exception as e:
                test_results.append(("✗", "Система рекомендаций", f"Ошибка: {str(e)}"))

            # Тест 3: Проверка рейтингов
            try:
                games_with_ratings = 0
                for i in range(self.games_list.size()):
                    game_name = self.games_list.get(i)
                    game = self.db.get_game(game_name)
                    if game and game.get_ratings_count() > 0:
                        games_with_ratings += 1
                test_results.append(("✓", "Система рейтингов", 
                                   f"Игр с оценками: {games_with_ratings}"))
            except Exception as e:
                test_results.append(("✗", "Система рейтингов", f"Ошибка: {str(e)}"))

            # Тест 4: Проверка партий
            try:
                matches_count = len(self.matches)
                test_results.append(("✓", "Система партий", f"Всего партий: {matches_count}"))
            except Exception as e:
                test_results.append(("✗", "Система партий", f"Ошибка: {str(e)}"))

            # Тест 5: Проверка схожести
            try:
                games = [self.games_list.get(i) for i in range(self.games_list.size())]
                if len(games) >= 2:
                    are_sim = self.db.are_similar(games[0], games[1])
                    test_results.append(("✓", "Проверка схожести", 
                                       f"Метод are_similar работает: {are_sim}"))
                else:
                    test_results.append(("⚠", "Проверка схожести", "Недостаточно игр для теста"))
            except Exception as e:
                test_results.append(("✗", "Проверка схожести", f"Ошибка: {str(e)}"))

            # Выводим результаты
            for status, component, message in test_results:
                test_text.insert(tk.END, f"{status} {component}: {message}\n")

        ttk.Button(top_frame, text="Запустить тесты", command=run_python_tests).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Закрыть", command=test_window.destroy).pack(side="right", padx=5)

        # Запускаем тесты по умолчанию
        run_python_tests()

    def open_settings(self):
        SettingsDialog(self, self.db)


def start_universe(name: str, use_default_games: bool = False):
    universe = Universe(name)
    app = MainWindow(universe)

    if use_default_games:
        # Загружаем общую базу (топ-50) в текущую вселенную.
        try:
            from default_games import load_default_games

            added_names = load_default_games(app.db)
            for game_name in added_names:
                app.games_list.insert(tk.END, game_name)
            app.refresh_games_combobox()
        except Exception as exc:
            messagebox.showerror("Ошибка загрузки общей базы", str(exc))

    app.mainloop()


def main():
    root = tk.Tk()
    root.title("BoardGame Advisor — выбор вселенной")
    root.geometry("400x200")

    def new_universe():
        name = "Вселенная 1"
        root.destroy()
        start_universe(name, use_default_games=False)

    def new_universe_with_defaults():
        name = "Вселенная 1"
        root.destroy()
        start_universe(name, use_default_games=True)

    ttk.Label(
        root,
        text="Выберите режим работы",
        font=("Segoe UI", 12, "bold"),
    ).pack(pady=10)

    ttk.Button(root, text="Создать новую вселенную", command=new_universe).pack(
        fill="x", padx=40, pady=5
    )

    ttk.Button(
        root, text="Начать с общей базой (топ-50)", command=new_universe_with_defaults
    ).pack(fill="x", padx=40, pady=5)

    ttk.Button(root, text="Выход", command=root.destroy).pack(
        side="bottom", pady=10
    )

    root.mainloop()


if __name__ == "__main__":
    main()


