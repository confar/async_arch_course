# async_arch_course

Задания к курсу по асинхронной архитектуре https://education.borshev.com/architecture

cd final_project

поднимаем кафку
docker-compose up

поднимаем сервис аутентификации:
cd auth
база в докере: docker-compose -f docker-compose.local.yml up  
приложение: ENV_FILE=settings.env python app/main.py

поднимаем сервис тасков:
cd ../task_manager
база в докере: docker-compose -f docker-compose.local.yml up  
приложение: ENV_FILE=settings.env python app/main.py
консьюмер евентов: ENV_FILE=settings.env python app/event_consumer/main.py

поднимаем сервис биллинга/аналитики:
cd ../accounting
база в докере: docker-compose -f accounting/docker-compose.local.yml up  
приложение: ENV_FILE=settings.env python app/main.py
консьюмер евентов: ENV_FILE=settings.env python app/event_consumer/main.py