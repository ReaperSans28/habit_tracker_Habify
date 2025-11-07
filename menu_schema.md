```mermaid
flowchart TD
    A["Старт /start"] --> A1{{"Новый пользователь?"}}
    A1 -- Да --> N2{{"Имя валидно?"}}
    N2 -- Нет --> N3["Спросить имя<br>state: waiting_for_name"]
    N2 -- Да --> N4["db.users.add_user<br>start_new"]
    N4 --> ONB["Онбординг<br>onboarding_intro<br>кнопка: Создать первую привычку"]

    A1 -- Нет --> A2{{"Есть привычки?"}}
    A2 -- Нет --> ONB
    A2 -- Да --> MM["<b>Главное меню</b><br>Мои привычки<br>Добавить новую<br>Помощь"]

    N3 --> S1["state: waiting_for_name<br>ввод имени"]
    S1 --> E1{"Имя валидно?"}
    E1 -- Нет --> E2["name_invalid_retry"]
    E2 --> S1
    E1 -- Да --> N4

    ONB -- Создать первую привычку --> HP["habit_prompt<br>state: waiting_for_input"]
    MM -- Добавить новую --> HP

    HP --> VF{"Формат ок?<br>Время и дни ок?"}
    VF -- Нет --> FR["format_invalid_retry"] --> HP
    VF -- Да --> SAVE["db.habits.add_habit<br>or<br>db.habits.edit_habit"]

    SAVE --> MODE{{"Режим: редактирование?"}}
    MODE -- Да --> OPEN["<b>Карточка привычки</b><br>Отметить выполнение<br>Редактировать<br>Пауза/Включить<br>Удалить<br>Назад"]
    MODE -- Нет --> MM

    MM -- Мои привычки --> HLIST["Список привычек"]
    HLIST -- Открыть привычку --> OPEN

    %% действия карточки
    OPEN -- Отметить --> ACTION["Отметить выполнение<br>db.habit_actions.add_action"] --> OPEN
    OPEN -- Редактировать<br>(ввести заново тем же форматом) --> HP
    OPEN -- Пауза/Включить --> TOGGLE["изменить state<br>db.habits.change_active"] --> OPEN
    OPEN -- Удалить --> CONF["Подтверждение удаления"]
    CONF -- Удалить --> DELETE["db.habits.delete"] --> HLIST
    OPEN -- Назад --> HLIST
    CONF -- Отмена --> OPEN

    HLIST -- Назад --> MM
