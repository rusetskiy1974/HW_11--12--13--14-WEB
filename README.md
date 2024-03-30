HW_11 -> 12 PYTHON WEB

docker-compose.yaml --створюємо контейнер для Postgres

ЗА ДОПОМОГОЮ DBEAVER АБО ІНШОГО ЗАСТОСУНКУ ПІДКЛЮЧАЄМОСЯ ДО БАЗИ POSTGRESS LOGIN: postgres, PASSWORD: 567234

СТВОРЮЄМО НОВУ БАЗУ => hw11

В ТЕРМІНАЛІ => alembic upgrade head  ЗАСТОСОВУЄМО МІГРАЦІЮ  

В ТЕРМІНАЛІ => py main.py  ЗАПУСКАЄМО ДОДАТОК

В БРАУЗЕРІ на localhost:8000/docs  ПРАЦЮЄМО З ЗАСТОСУНКОМ

ДЛЯ ШЛЯХУ api/contacts/all СТВОРЕНО ДОСТУП ПО РОЛІ, 

В POSTGRES ДЛЯ КОРИСТУВАЧА  В РУЧНОМУ РЕЖИМІ ВИБРАТИ  РОЛЬ  admin або moderator

ЗА ЗАМОВЧУВАННЯМ УСІМ КОРИСТУВАЧАМ ПРИ РЕЄСТРАЦІЇ НАДАЄТЬСЯ РОЛЬ user



