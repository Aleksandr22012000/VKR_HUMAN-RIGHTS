-- Pandoc Lua-фильтр: стили ВКР (центрирование, разрывы страниц, подписи).

local structural_keys = {
  ["ВВЕДЕНИЕ"] = true,
  ["ЗАКЛЮЧЕНИЕ"] = true,
  ["ОГЛАВЛЕНИЕ"] = true,
}

local function header_text(el)
  return pandoc.utils.stringify(el.content):gsub("%s+", " "):match("^%s*(.-)%s*$")
end

local function is_structural(text)
  local upper = text:upper()
  if structural_keys[upper] then return true end
  if upper:match("^СПИСОК ") then return true end
  return false
end

local function with_custom_style(el, style_name)
  local id = el.identifier or ""
  local classes = el.classes or {}
  local attrs = { ["custom-style"] = style_name }
  return pandoc.Para(el.content, pandoc.Attr(id, classes, attrs))
end

function Header(el)
  local text = header_text(el)
  local blocks = {}

  if el.classes:includes("chapter") or el.classes:includes("appendix") then
    table.insert(
      blocks,
      pandoc.RawBlock("openxml", "<w:p><w:r><w:br w:type=\"page\"/></w:r></w:p>")
    )
  end

  local id = el.identifier or ""
  local classes = el.classes or {}
  local attrs = {}

  if el.classes:includes("structural") or is_structural(text) then
    attrs["custom-style"] = "Structural"
  end

  table.insert(blocks, pandoc.Header(el.level, el.content, pandoc.Attr(id, classes, attrs)))
  return blocks
end

function Para(el)
  local text = pandoc.utils.stringify(el)

  if text:match("Таблица%s+%d") then
    return with_custom_style(el, "Table Caption")
  end
  if text:match("Рисунок%s+%d") then
    return with_custom_style(el, "Figure Caption")
  end
  return nil
end
