-- instinct.lua
-- Neural Expression Layer (Humanoid Response)

local Instinct = {}

-- utility: lembutkan kalimat
local function soften(text)
  return text
    :gsub("!", "…")
    :gsub("%.$", "…")
end

-- utility: refleksi empatik
local function reflect(text)
  return "Aku paham maksudmu. " .. text
end

-- MODE UTAMA
function Instinct.respond(mode, core)
  if mode == "reflective_lore" then
    return reflect(
      "Dalam konteks ini, jawabannya tidak hitam putih. "
      .. soften(core)
    )

  elseif mode == "structured_teaching" then
    return
      "Mari kita bahas pelan-pelan.\n\n"
      .. "Intinya:\n"
      .. "1. " .. core

  else
    return soften(core)
  end
end

return Instinct
