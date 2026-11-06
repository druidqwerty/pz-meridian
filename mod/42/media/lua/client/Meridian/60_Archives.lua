require "ISUI/ISPanelJoypad"
require "ISUI/ISRichTextPanel"
require "ISUI/ISModalRichText"

local M = Meridian

local function readArchive(playerNum, site)
    local player = getSpecificPlayer(playerNum)
    if not player or math.floor(player:getZ()) ~= (site.z or 0)
            or (player:getX()-site.x)^2 + (player:getY()-site.y)^2 > 64 then return end
    local core = getCore()
    local scale = math.max(1, core:getScreenWidth() / 1920)
    local w = math.min(core:getScreenWidth()-40, 620*scale)
    local h = math.min(core:getScreenHeight()-40, 340*scale)
    local modal = ISModalRichText:new((core:getScreenWidth()-w)/2,
        (core:getScreenHeight()-h)/2, w, h, getText(site.textKey), false, nil, nil, playerNum)
    modal:initialise()
    modal:addToUIManager()
    player:getModData().MeridianArchives = player:getModData().MeridianArchives or {}
    player:getModData().MeridianArchives[site.id] = true
end

local function context(playerNum, menu, worldobjects, test)
    if test then return end
    local player = getSpecificPlayer(playerNum)
    if not player then return end
    for _, site in ipairs((M.Config and M.Config.storySites) or {}) do
        if math.floor(player:getZ()) == (site.z or 0)
                and (player:getX()-site.x)^2 + (player:getY()-site.y)^2 <= 64 then
            menu:addOption(getText("UI_Meridian_ReadArchive"), playerNum, readArchive, site)
            break
        end
    end
end

local function reportCompatibility()
    print("[Meridian] Native vanilla geometry; optional Viewpoint=" .. tostring(Viewpoint ~= nil))
end

Events.OnFillWorldObjectContextMenu.Add(context)
Events.OnGameStart.Add(reportCompatibility)
