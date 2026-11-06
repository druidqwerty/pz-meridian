-- Ordinary rooms retain vanilla loot. Secret caches supplement, never replace it.
local M = Meridian
local supplies = {
    food = {{"Base.TinnedBeans",6}, {"Base.CannedCorn",6}, {"Base.WaterBottle",4}},
    medical = {{"Base.Bandage",6}, {"Base.Disinfectant",2}, {"Base.Pills",2}},
    tools = {{"Base.Hammer",1}, {"Base.Screwdriver",1}, {"Base.NailsBox",3}, {"Base.Battery",4}},
    armory = {{"Base.Bullets9mmBox",6}, {"Base.Pistol",1}, {"Base.Torch",1}, {"Base.Battery",4}},
}
local aliases = {armystorage="armory", policestorage="armory", medicalstorage="medical",
    laboratory="medical", hospitalroom="medical", medical="medical", kitchen="food",
    bedroom="food", storage="tools", hall="tools"}

local function cacheAt(x, y, z, room)
    for _, cache in ipairs((M.Config and M.Config.caches) or {}) do
        if cache.x == x and cache.y == y and (cache.z or 0) == z then
            return cache.kind or "tools"
        end
    end
    if room == "meridiancache" then return "tools" end
    return nil
end

function M.fillSupplies(roomName, containerType, container)
    if not M.authoritative() or not M.option("SupplyCaches", true) or not container then return end
    local parent = container:getParent()
    local sq = parent and parent:getSquare()
    if not sq or not M.inWorld(sq:getX(), sq:getY()) then return end
    local kind = cacheAt(sq:getX(), sq:getY(), sq:getZ(), roomName)
    if not kind then return end
    local data = parent:getModData()
    if data.MeridianCacheFilled then return end
    -- Validate item scripts; a renamed vanilla item never produces error spam.
    local list = supplies[aliases[kind] or kind] or supplies.tools
    for _, entry in ipairs(list) do
        if getScriptManager():FindItem(entry[1]) then
            for i=1,entry[2] do container:AddItem(entry[1]) end
        end
    end
    data.MeridianCacheFilled = true
end

Events.OnFillContainer.Add(M.fillSupplies)
