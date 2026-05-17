# md-to-docx

Конвертация Markdown (`.md`) в Word (`.docx`) с оформлением по требованиям ВКР (методические рекомендации СПбУТУиЭ, раздел 6).

## Возможности

- Предобработка MD после экспорта из Word (HYPERLINK, `**заголовки**`, экранирование)
- Шаблон `reference.docx`: Times New Roman 14 pt, интервал 1,5, поля 30/20/20/10 мм
- Lua-фильтр: разрывы страниц для глав/приложений, центрирование «ВВЕДЕНИЕ», подписи таблиц/рисунков
- Оглавление Word (`--toc`)
- Запасной движок HTML (без стилей ВКР)

## Требования

- Python 3.10+

## Установка

```bash
git clone https://github.com/Aleksandr22012000/VKR_HUMAN-RIGHTS.git
cd VKR_HUMAN-RIGHTS/md-to-docx

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python build_reference_docx.py   # создаёт assets/reference.docx
```

## Использование

```bash
# Базовая конвертация (предобработка + стили ВКР)
python md_to_docx.py document.md

# С оглавлением Word (рекомендуется для файлов из Word)
python md_to_docx.py document.md --toc

# Сохранить очищенный MD для проверки
python md_to_docx.py document.md --keep-temp

# Без предобработки
python md_to_docx.py document.md --no-preprocess

# Запасной движок
python md_to_docx.py document.md --engine html
```

### Пример: методические рекомендации

```bash
python md_to_docx.py "МУ_к_ВКР_2025.md" -o "МУ_к_ВКР_2025.docx" --toc --keep-temp
```

## Параметры

| Параметр | Описание |
|----------|----------|
| `input` | Исходный `.md` |
| `-o`, `--output` | Выходной `.docx` |
| `--toc` | Сгенерировать оглавление (удаляет HYPERLINK из экспорта Word) |
| `--no-preprocess` | Не очищать MD |
| `--keep-temp` | Сохранить `*.preprocessed.md` |
| `--reference-doc` | Путь к шаблону Word |
| `--lua-filter` | Путь к Lua-фильтру Pandoc |
| `--engine` | `pandoc` (по умолчанию) или `html` |

## Структура репозитория

```
md-to-docx/
├── md_to_docx.py           # CLI
├── md_preprocess.py        # предобработка Markdown
├── build_reference_docx.py # генерация шаблона стилей
├── assets/reference.docx   # шаблон Word
├── filters/vkr_docx.lua    # фильтр Pandoc
├── requirements.txt
└── example.md
```

## Ограничения

- Псевдотаблицы (строки подряд без `|`) не восстанавливаются автоматически — используйте GFM-таблицы в MD.
- Бланки с `___` сохраняются как текст; для форм нужна ручная правка в Word.
- Подстрочные сноски: задавайте в MD как `[^1]` (Pandoc) или добавляйте в Word после конвертации.

## Лицензия

MIT — см. [LICENSE](LICENSE).
