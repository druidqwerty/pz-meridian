-- One service SUV per world, at the expedition departure point.
local M = Meridian
local waiting, attempts, tick = nil, 0, 0

local function spawn(player)
    local cfg = M.Config and M.Config.starterVehicle
    if not cfg or not player or not M.authoritative() then return true end
    if not M.option("StarterVehicle", true) or M.saved().starterVehicle then return true end
    if not M.inWorld(player:getX(), player:getY()) then return true end
    local square = getCell():getGridSquare(cfg.x, cfg.y, cfg.z or 0)
    if not square then return false end
    if square:getVehicleContainer() then
        -- Never create overlapping vehicles if a save or another mod supplied one.
        M.saved().starterVehicle = true
        return true
    end
    if not square:isFree(false) or square:HasStairs() then return false end
    local ok, car = pcall(addVehicleDebug, cfg.script or "Base.SUV", IsoDirections.N, nil, square)
    if not ok or not car then return false end
    M.saved().starterVehicle = true
    local prepared, err = pcall(function()
        car:repair()
        local tank = car:getPartById("GasTank")
        if tank then tank:setContainerContentAmount(tank:getContainerCapacity()) end
        player:getInventory():AddItem(car:createVehicleKey())
    end)
    if not prepared then print("[Meridian] Starter SUV preparation failed: " .. tostring(err)) end
    return true
end

function M.startExpedition(player)
    if not M.authoritative() then return end
    if not spawn(player) then waiting, attempts = player, 0 end
end

local function retry()
    if not waiting then return end
    tick = tick + 1
    if tick % 60 ~= 0 then return end
    attempts = attempts + 1
    if spawn(waiting) or attempts >= 30 then waiting = nil end
end

local function nearbyStarter()
    if not M.authoritative() then return end
    local cfg = M.Config and M.Config.starterVehicle
    if not cfg or M.saved().starterVehicle then return end
    local players = isServer() and getOnlinePlayers() or nil
    local count = players and players:size() or getNumActivePlayers()
    for i=0,count-1 do
        local player = players and players:get(i) or getSpecificPlayer(i)
        if player and (player:getX()-cfg.x)^2 + (player:getY()-cfg.y)^2 < 65536 then
            if spawn(player) then return end
        end
    end
end

Events.OnNewGame.Add(M.startExpedition)
Events.OnTick.Add(retry)
Events.OnGameStart.Add(nearbyStarter)
Events.EveryOneMinute.Add(nearbyStarter)
