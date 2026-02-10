project2_Mandrygina_Olga_M25-555

# Primitive DB

Домашнее задание "Примитивная база данных"


Запуск - 

poetry run project


Описание команд

1. Управление таблицами

***Процесс работы с таблицей***

Функции:

1. create_table - создать таблицу

Пример -  create_table имя_таблицы столбец1:тип столбец2:тип

2. list_tables - показать список всех таблиц

Пример - list_tables

3. удалить таблицу - drop_table

Пример - drop_table имя_таблицы

4. Создать запись - insert into имя_таблицы values( значение1, значение2, ...)

Пример - insert into users values ( Sergei, 28, true)

5. Прочитать записи по условию - select from имя_таблицы where столбец = значение 

Пример - 
    
    select from имя_таблицы - прочитать  все записи.

    select from имя_таблицы where age = 28 

6. Обновить запись - update имя_таблицы set столбец1 = новое_значение where столбец_условия = значение_условия

Пример - update имя_таблицы set столбец1 = новое_значение where столбец_условия = значение_условия

update users set age = 29 where job_title = zavhoz

7. Удалить запись - delete from имя_таблицы where столбец = значение

Пример -  delete from users where age = 26

8. Вывести информацию о таблице - info имя_таблицы

Пример - info users

Общие команды

9. exit - выход из программы

Пример - exit

10. help - справочная информация

Пример - help


Далее ASCIINEMA

https://asciinema.org/a/5NJJsGa55MwPEQUk



