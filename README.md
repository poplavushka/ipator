Список участников: Лиля Файзеева, Лена Миронова, Варя Николаева, Диана Хаялеева, Ася Анцупова.

Описание проекта: телеграм-бот, выполняющий функции игры “Акинатор” на материале базы данных PHOIBLE. Телеграм-бот угадывает задуманную пользователем фонему, задавая вопросы о ее признаках и некоторых других особенностях. Выбор отгадки построен на подсчете вероятностей по теореме Байеса. 

Репозиторий: https://github.com/poplavushka/ipator
В репозитории (в главной ветке) лежат файлы:
<li> be.py – код, который использовался для реорганизации всей информации, полученной из PHOIBLE (взят из открытого ресурса)
<li> bebe.csv – табличка, в которой лежат все сегменты, которые есть в PHOIBLE
<li> cons.csv – табличка, к которой код обращается, когда задает вопросы про согласные звуки
<li> sounds.csv – все звуки, которые описаны в базе данных PHOIBLE
<li> template.py – код с сайта, который мы брали за основу (взят из того же открытого ресурса)
<li> testing.py – “движок” нашего кода, который содержит функции по высчитыванию вероятностей
<li> vowels.csv – табличка, к которой код обращается, когда задает вопросы про гласные звуки
<li> requirements.txt – штуки, которые должны быть у вас на компьютере, чтобы код заработал
<li> first_version_ipator.py – первая версия бота
<li> finalbotipator_no_pep.py – финальная версия бота (не отформатированная по pep-8)
<li> peppedfinalbotipator.py – финальная версия бота, отформатированная по pep-8
<li> codewithsomecomments.py – финальный код с комментариями

Для создания бота также использовались:
<li> Stack Overflow
<li> Habr
<li> BotFather 

Как запустить код:
<li> Чтобы запустить код на своем компьютере, вы должны скачать файлы cons.csv и vowels.csv (чтобы у IPAtor’а была база данных, по которой он отгадывает), скачать библиотеки из requirements.txt, затем нужно запустить код из файла peppedfinalbotipator.py.


