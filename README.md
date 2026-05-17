# VKR_HUMAN-RIGHTS

Репозиторий выпускной квалификационной работы (направление «Юрист в сфере правозащитной деятельности»).

**GitHub:** [Aleksandr22012000/VKR_HUMAN-RIGHTS](https://github.com/Aleksandr22012000/VKR_HUMAN-RIGHTS)  
**Ветка для публикации:** `1-VER`

## Содержимое

| Файл / папка | Описание |
|--------------|----------|
| [ВКР_Мыльников_полный.md](ВКР_Мыльников_полный.md) | Текст ВКР в Markdown (ранняя версия) |
| [ВКР_Мыльников_итог_14.05_2.md](ВКР_Мыльников_итог_14.05_2.md) | Текст ВКР в Markdown (итог от 14.05, из DOCX) |
| [МУ_к_ВКР_2025.md](МУ_к_ВКР_2025.md) | Методические рекомендации по ВКР (СПбУТУиЭ, 2025) |
| [vkr_revision_requirements.md](vkr_revision_requirements.md) | Требования научного руководителя к доработке (май 2026) |
| [deep-research-report.md](deep-research-report.md) | Исследование: институт уполномоченных в России (статистика, 2021–2024) |
| [md-to-docx/](md-to-docx/) | Конвертация Markdown → Word (.docx) по методическим требованиям СПбУТУиЭ |

Исходный файл Word (`*.docx` в корне) в репозиторий не включается — храните локально или добавьте вручную при необходимости.

## Конвертация MD → DOCX

```bash
cd md-to-docx
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python md_to_docx.py ../ВКР_Мыльников_полный.md \
  -o ../ВКР_Мыльников_полный.docx \
  --toc --keep-temp
```

Подробности — в [md-to-docx/README.md](md-to-docx/README.md).

## Публикация на GitHub

После правок в репозитории:

```bash
./push_1-VER.sh
```

Скрипт отправляет ветку `1-VER` в `origin`. При первом push по HTTPS GitHub запросит логин и [Personal Access Token](https://github.com/settings/tokens) (пароль аккаунта для git push не используется).

### Первый коммит (если ещё не закоммичено)

```bash
git add README.md ВКР_Мыльников_полный.md vkr_revision_requirements.md md-to-docx push_1-VER.sh .gitignore
git commit -m "Добавить текст ВКР, конвертер md-to-docx и скрипт пуша"
./push_1-VER.sh
```
