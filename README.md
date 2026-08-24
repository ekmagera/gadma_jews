Репозиторий запускает воспроизводимый анализ демографических моделей ашкеназских (A), грузинских (G) и горских (M) евреев. Сравниваются одновременное разделение S0 и три последовательные топологии: T1 A|(G,M), T2 G|(A,M), T3 M|(A,G). Анализ выполняется только по аутосомам.

На компьютере нужны Git и Docker. В репозиторий нельзя загружать BCF, VCF, PLINK-файлы или индивидуальные генотипы.

До запуска подготовьте BCF, таблицу metadata/samples.csv с колонками ID,Population, название сборки референса, описание variant calling и callable BED-маску нейтральных аутосомных участков. ID в CSV должны совпадать с BCF. Допустимые названия групп: Ashkenazi Jews, Georgian Jews, Mountain Jews.

git clone https://github.com/ekmagera/gadma_jews
cd gadma_jews
docker build --no-cache -t jews-demography:latest .
cp /path/to/input.bcf raw/jews.bcf

Замените metadata/samples.csv своими метаданными. Launcher сам попробует sudo docker, если обычный Docker недоступен. Сам скрипт через sudo запускать не нужно.

bash run_docker.sh preview 8
cat results/qc/metadata_validation.txt
cat results/qc/autosomes.variant_counts.tsv
cat results/sfs/preview.txt

Проверьте, что остались только 22 аутосомы. Проекции выбираются отдельно для каждого нового набора данных. По умолчанию workflow автоматически берёт минимальную проекцию, сохраняющую не менее 99% максимального числа сегрегирующих сайтов.

bash run_docker.sh sfs 8
cat results/sfs/selected_projections.tsv
bash run_docker.sh smoke 4
cat results/smoke/model_evaluation.tsv

Проверьте selected_projections.tsv. В config/config.yaml можно выбрать режим auto, строгий максимум max или ручной manual. Правила выбора и параметры производительности описаны в docs/PARAMETERS_RU.md.

Smoke проверяет только чтение SFS и функции моделей. Если нужен только технический тест репозитория, на этом можно остановиться.

Для непрерывного расчёта можно сразу выполнить bash run_docker.sh select 8: Snakemake сам последовательно выполнит QC, preview, автоматический выбор проекций, построение SFS и оптимизацию моделей.

bash run_docker.sh select 8
cat results/model_selection/aic.tsv
cat results/model_selection/winner.txt

Select оптимизирует все свободные параметры четырёх топологий и сравнивает их по AIC. Если winner.txt содержит INCOMPLETE, дождитесь завершения всех repeats. Если он содержит BOUNDARY_REVIEW, измените gadma.bounds в config/config.yaml и заново запустите select для всех четырёх моделей.

bash run_docker.sh refine

Refine выполняет дополнительные независимые оптимизации выбранной топологии. После завершения проверьте GADMA.log победившей модели на достижение границ и большой разброс log-likelihood.

Для перевода результатов в размеры популяций и годы укажите в config/scaling_scenarios.yaml число callable нейтральных аутосомных оснований. Это не число SNP и не полный размер референса. Значения mutation rate, generation time и sequence length меняют только физическое масштабирование, но не likelihood, AIC или выбранную топологию.

bash run_docker.sh scale
bash run_docker.sh pack

Отправьте файл handoff_YYYYMMDD_HHMMSS.tar.gz. Отдельно сообщите сборку референса, источник callable mask и sequence length, описание variant calling, числа образцов до и после KING, CPU, RAM, фактическое время, внешний walltime, прерывания и ручные исключения.

Встроенного ограничения по времени нет. GADMA завершает каждый repeat по критерию сходимости. Количество запусков задают gadma.selection_repeats и gadma.refinement_repeats, параллельность — gadma.processes и аргумент cores. Полный расчёт может занимать несколько дней; внешний walltime должен быть задан с запасом, потому что незавершённая модель при повторном запуске начинается сначала.

Подробная инструкция и литературные источники находятся в docs/HANDOFF_RU.md, выбор параметров — в docs/PARAMETERS_RU.md.
