-- Meridian ships vector geometry, not vanilla image pyramids. Keep exploration
-- fog and normal player controls; only this world's atlas style/bounds change.
require "ISUI/Maps/ISWorldMap"

local function isMeridianWorld()
    if not MainScreen or not MainScreen.instance or not MainScreen.instance.inGame then return false end
    local dirs = getLotDirectories()
    for i = 0, dirs:size() - 1 do
        if dirs:get(i) == "Meridian" then return true end
    end
    return false
end

if not MapUtils.MeridianVectorAtlasInstalled then
    MapUtils.MeridianVectorAtlasInstalled = true
    -- Vanilla rebuilds V3 on colorblind preference changes as well as first
    -- open. Hook that single style boundary, never prerender on every frame.
    local original = MapUtils.initDefaultStyleV3
    function MapUtils.initDefaultStyleV3(self)
        original(self)
        if self.Type ~= "ISWorldMap" or not isMeridianWorld() then return end
        MapUtils.initDefaultStyleV1(self)
        local api = self.mapAPI
        api:setBoolean("ImagePyramid", false)
        api:setBoolean("Features", true)
        -- Vanilla wilderness expands MetaGrid to -250..250 cells. Fitting that
        -- envelope hides the journey below vanilla road-layer visibility zoom.
        api:setBoundsFromData()
        local style = api:getStyleAPI()
        for _, name in ipairs({"road-primary", "road-secondary", "road-tertiary"}) do
            local layer = style:getLayerByName(name)
            if layer then layer:setMinZoom(0) end
        end
        local lake = style:newPolygonLayer("meridian-lakes")
        lake:setMinZoom(0)
        lake:setFilter("water", "lake")
        lake:addFill(0, 59, 141, 149, 255)
        lake:addFill(24, 59, 141, 149, 255)
        for _, kind in ipairs({"residential", "service"}) do
            local road = style:newPolygonLayer("meridian-" .. kind)
            road:setMinZoom(11)
            road:setFilter("highway", kind)
            road:addFill(0, 134, 125, 113, 255)
            road:addFill(24, 134, 125, 113, 255)
        end
        -- The vanilla caller adds the paper overlay after constructing style.
    end
end
