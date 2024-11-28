# Лабораторная работа №2 по дисциплине ОМИС
# Реализация объектной модели
### Тема:
Платформа для создания и управления корпоративным блогом
### Описание:
Лабораторная работа выполнена по варианту студента Абушкевича А.А., студента группы 221701. Результат выполнения студентом этапа проектирования доступен по ссылке https://docs.google.com/document/d/1OBSEMgihX_cZQn7unwesAZ21WXYvC1lkHQMzoo5rc8Y/edit?tab=t.0

Программа реализована с использованием шаблона проектирования MVC. Реализация модели находится в файле model.py, контроллера - controller.py, представления - view.py

### Ход работы:
Для корректной работы программы после клонирования репозитория и запуске его в удобной среде разработки(рекомендуется PyCharm) сразу настроить базу данных PostgreSQL. Для этого необходимо сначала установить PostgreSQL с официального интернет-ресурса https://www.postgresql.org/download/

После настройки бд необходимо запустить файл **db.sql** - он содержит основные таблицы для работы с приложением. 

В случае, если появится необходимость сбросить изменения в таблицах до того уровня, на котором они были изначально, запустить скрипт **drop_tables.sql**.

Исполняемый файл - **interface.py**.

В директории **templates** находятся html-шаблоны.

По пути **static/uploads** находятся изображения и видео, которые можно устанавливать в поле **media_path** при создании поста.

### Основные окна программы:

1. ## Окно авторизации:
  ![image](https://github.com/user-attachments/assets/b8af5f79-44e3-4b88-9176-ef931f602e5b)

2. ## Окно регистрации:
   ![image](https://github.com/user-attachments/assets/30cb6d3b-e53a-4687-84f7-5d915130eb07)

   ![image](https://github.com/user-attachments/assets/3b36bf27-0341-46d4-b964-d99988048899)

3. ## Окно для администратора:
   ![image](https://github.com/user-attachments/assets/11f2f257-8526-40dc-b4e7-6a4ebdda2d56)

4. Окно для создания блога(администратор):
   ![image](https://github.com/user-attachments/assets/9bcb31ed-2036-46ad-8c6b-930a8b69e210)

5. Окно для удаления блога(администратор):
   ![image](https://github.com/user-attachments/assets/6223f91b-2d10-4aa8-a25b-9726d9f75fce)

6. Окно для просмотра контента блога(администратор):
   ![image](https://github.com/user-attachments/assets/74936cc1-b8c8-4476-91a2-ff9fb9425b9a)

   ![image](https://github.com/user-attachments/assets/5f755ede-4310-49d4-8228-2fe8df7c3563)

7. Окно для управления ролями пользователей(администратор):
   ![image](https://github.com/user-attachments/assets/8e5ffe2e-00e4-4748-a1b9-2d03b779a315)

8. Окно для просмотра и управления постами, находящимися на модерации(администратор):
   ![image](https://github.com/user-attachments/assets/2525e310-a706-4428-9872-b5566060e094)

9. ## Окно для автора:
    ![image](https://github.com/user-attachments/assets/f4af74ac-55cc-4ebe-81f5-b6130ce8ee5e)

10. Окно для создания нового поста(автор):
    ![image](https://github.com/user-attachments/assets/08321ece-6618-41d1-a372-66bd97082bb5)

11. Окно для удаления поста(автор):
    ![image](https://github.com/user-attachments/assets/7c4eee17-ed5f-45f5-8ef0-593eec6ad9b0)

    ![image](https://github.com/user-attachments/assets/cc27c2aa-4b8d-40bc-b3a2-5e84cf9f08ef)

12. Окно для просмотра опубликованных текущим автором постов(автор):
    ![image](https://github.com/user-attachments/assets/8a426cf3-4052-488b-bcfb-97e26c134b1b)

13. Окно для просмотра постов на модерации(автор):
    ![image](https://github.com/user-attachments/assets/33fafd36-a079-40f6-a2b5-ae844bedbeba)

14. Главное меню просмотра постов в блоге(автор):
    ![image](https://github.com/user-attachments/assets/31846e38-a98b-41c9-a1df-599b4d0c7b0c)

    При нажатии кнопки "Просмотреть пост":
    ![image](https://github.com/user-attachments/assets/cf20d006-5ffd-4153-a514-9480eeff7195)

    Раздел "Для Вас" - основывается на тегах тех постов, которым вы поставили лайк:
    ![image](https://github.com/user-attachments/assets/a9f7369f-88bf-4241-89db-5556ee1bc9f3)

15. ## Окно для читателя(его сразу перенаправляет на окно просмотра постов блога(для выбора другого блога необходимо нажать "<- Select another blog")):
    ![image](https://github.com/user-attachments/assets/ded5f25a-200a-47b0-b86b-e6564e034953)

16. Поиск поста(находить можно не вводя всё название, а даже по первому слову или букве. Поиск не является чувствительным к регистру):
    ![image](https://github.com/user-attachments/assets/dcf92e9e-3b66-4c6d-b129-f983d7fd3eef)
















