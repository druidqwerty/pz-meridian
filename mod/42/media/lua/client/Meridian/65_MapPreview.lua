-- PZ 42.21's vector spawn preview initializes exploration fog before MetaGrid
-- exists. Only Meridian's pre-game preview needs a fog-free, independent style.
require "OptionScreens/MapSpawnSelect"

if not MapSpawnSelectImage.MeridianPreviewInstalled then
    MapSpawnSelectImage.MeridianPreviewInstalled = true
    local original = MapSpawnSelectImage.prerender

    local function isMeridianPreview(panel)
        if not MainScreen or not MainScreen.instance or MainScreen.instance.inGame then return false end
        local list = panel.parent and panel.parent.listbox
        local row = list and list.items and list.items[list.selected]
        local item = row and row.item
        return item and (item.dir == "Meridian"
            or (item.region and item.region.name == "Meridian"))
    end

    local function stylePreview(panel)
        local api = panel.javaObject:getAPIv1()
        local style = api:getStyleAPI()
        api:setBoolean("ImagePyramid", false)
        api:setBoolean("HideUnvisited", false)
        api:setBoolean("BlurUnvisited", false)
        api:setBoolean("UnvisitedGrid", false)
        api:setBackgroundRGBA(0.86, 0.87, 0.80, 1)
        style:clear()
        local definitions = {
            {"meridian-settlements", "landuse", "residential", 193, 193, 166},
            {"meridian-water", "water", "*", 76, 135, 160},
            {"meridian-roads", "highway", "*", 91, 91, 84},
            {"meridian-buildings", "building", "*", 184, 122, 82},
        }
        for _, d in ipairs(definitions) do
            local layer = style:newPolygonLayer(d[1])
            layer:setMinZoom(0)
            layer:setFilter(d[2], d[3])
            layer:addFill(0, d[4], d[5], d[6], 255)
            layer:addFill(24, d[4], d[5], d[6], 255)
        end
        panel.mapAPI:setBoundsFromData()
        panel.mapAPI:resetView()
        panel.hasResetView = true
        print("[Meridian] Standalone spawn preview initialized without exploration fog")
    end

    function MapSpawnSelectImage:prerender()
        if not self.hasResetView and isMeridianPreview(self) and self:getWidth() >= 1
                and self.mapAPI:getDataCount() > 0 and self.mapAPI:isDataLoaded() then
            stylePreview(self)
        end
        -- Retain vanilla initial-location zoom, rendering and every other map.
        return original(self)
    end
end
