Отредактируйте metadata/samples.csv: файл должен содержать колонки ID,Population, а идентификаторы должны совпадать с образцами в BCF. Допустимые названия популяций: Ashkenazi Jews, Georgian Jews, Mountain Jews. Mountain Jews = Azerbaijan Jews. 
Соберите Docker-образ и запустите анализ:
docker build --no-cache -t jews-demography:latest .
bash run_docker.sh select 8
Workflow автоматически выполняет QC, удаляет родственников, выбирает проекции SFS, строит SFS и сравнивает модели S0/T1/T2/T3 по AIC. Выбранные проекции сохраняются в results/sfs/selected_projections.tsv.
Основные настройки находятся в config/config.yaml. При запуске используются заданные число повторов и количество процессов; увеличивайте их только при наличии дополнительных CPU/RAM и достаточного времени расчёта. Проекции выбираются автоматически (auto) с сохранением 99% от максимального числа сегрегирующих сайтов. Рекомендации по выбору параметров приведены в docs/PARAMETERS_RU.md.
