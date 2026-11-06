-- Meridian: original runtime policy. Geometry and bounds are build inputs.
Meridian = Meridian or {}
local M = Meridian

function M.option(name, fallback)
    local vars = SandboxVars and SandboxVars.MeridianLongWayHome
    if vars and vars[name] ~= nil then return vars[name] end
    return fallback
end

function M.contains(rect, x, y)
    return rect and x >= rect.x1 and x <= rect.x2
        and y >= rect.y1 and y <= rect.y2
end

function M.isSafeSurface(x, y, z)
    return z >= 0 and M.contains(M.Config and M.Config.safeCity, x, y)
end

function M.bunkerAt(x, y, z)
    if z >= 0 then return nil end
    for _, site in ipairs((M.Config and M.Config.bunkers) or {}) do
        if z >= (site.minZ or -4) and z <= (site.maxZ or -1)
                and M.contains(site, x, y) then return site end
    end
    return nil
end

function M.inWorld(x, y)
    local w = M.Config and M.Config.world
    return w and x >= w.minX and x <= w.maxX and y >= w.minY and y <= w.maxY
end

function M.authoritative()
    return not (isClient and isClient())
end

function M.bucketKey(site, x, y, z)
    return site.id .. ":" .. math.floor(x / 8) .. ":" .. math.floor(y / 8)
        .. ":" .. math.floor(z)
end

function M.zombiesEnabled()
    if SandboxVars and SandboxVars.Zombies == 6 then return false end
    local cfg = SandboxVars and SandboxVars.ZombieConfig
    return not (cfg and cfg.PopulationMultiplier == 0)
end

function M.saved()
    local state = ModData.getOrCreate("MeridianLongWayHome")
    state.seeded = state.seeded or {}
    return state
end
