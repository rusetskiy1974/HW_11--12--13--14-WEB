HW_11 -> 12 PYTHON WEB

docker-compose.yaml --створюємо контейнер для Postgres

ЗА ДОПОМОГОЮ DBEAVER АБО ІНШОГО ЗАСТОСУНКУ ПІДКЛЮЧАЄМОСЯ ДО БАЗИ POSTGRESS LOGIN: postgres, PASSWORD: 567234

СТВОРЮЄМО НОВУ БАЗУ => hw11

В ТЕРМІНАЛІ => alembic upgrade head  ЗАСТОСОВУЄМО МІГРАЦІЮ  

В ТЕРМІНАЛІ => uvicorn main:app --host localhost --port 8000 --reload  ЗАПУСКАЄМО СЕРВЕР

В БРАУЗЕРІ на localhost:8000/docs  ПРАЦЮЄМО З ЗАСТОСУНКОМ



