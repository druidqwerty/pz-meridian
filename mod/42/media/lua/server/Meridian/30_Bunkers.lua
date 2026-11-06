-- Persistent first-visit hordes, created only on already loaded interior floors.
local M = Meridian
local pending, order, tick = {}, {}, 0

local function playerNear(x, y, z)
    local players = isServer() and getOnlinePlayers() or nil
    local count = players and players:size() or getNumActivePlayers()
    for i = 0, count - 1 do
        local p = players and players:get(i) or getSpecificPlayer(i)
        if p and math.floor(p:getZ()) == z
                and (p:getX()-x)^2 + (p:getY()-y)^2 < 196 then return true end
    end
    return false
end

function M.queueBunkerSquare(square)
    if not M.authoritative() or not M.zombiesEnabled()
            or not M.option("BunkerHordes", true) then return end
    local x, y, z = square:getX(), square:getY(), square:getZ()
    local site = M.bunkerAt(x, y, z)
    if not site or not square:getRoom() or not square:TreatAsSolidFloor() then return end
    local key = M.bucketKey(site, x, y, z)
    if M.saved().seeded[key] or pending[key] then return end
    if #order >= 2048 then return end
    pending[key] = {x=x, y=y, z=z, site=site, attempts=0}
    order[#order+1] = key
end

local function seed(key, job)
    local cell = getCell()
    if not cell then return false end
    -- An unloaded candidate is retried when that square loads again.
    local square
    local bx, by = math.floor(job.x/8)*8, math.floor(job.y/8)*8
    for x = bx, bx+7 do
        for y = by, by+7 do
            local q = cell:getGridSquare(x, y, job.z)
            if q and M.contains(job.site, x, y) and q:getRoom()
                    and q:TreatAsSolidFloor() and not q:HasStairs()
                    and q:isFree(false) and not playerNear(x, y, job.z) then
                square = q
                break
            end
        end
        if square then break end
    end
    if not square then return false end
    if cell:getZombieList():size() >= 1600 then return false end
    local count = math.max(1, math.min(8, job.site.zombiesPerBucket or 3))
    local ok, zombies = pcall(addZombiesInOutfit,
        square:getX(), square:getY(), job.z, count, nil, 50)
    if not ok or not zombies or zombies:size() == 0 then return false end
    M.saved().seeded[key] = true
    M.bunkerSpawned = (M.bunkerSpawned or 0) + zombies:size()
    return true
end

function M.processBunkerQueue()
    if not M.authoritative() or not M.zombiesEnabled()
            or not M.option("BunkerHordes", true) then return end
    tick = tick + 1
    if tick % 60 ~= 0 then return end
    local processed = 0
    while #order > 0 and processed < 4 do
        local key = table.remove(order, 1)
        local job = pending[key]
        if job then
            job.attempts = job.attempts + 1
            if not M.saved().seeded[key] and not seed(key, job) and job.attempts < 3 then
                order[#order+1] = key
            else pending[key] = nil end
        end
        processed = processed + 1
    end
end

Events.LoadGridsquare.Add(M.queueBunkerSquare)
Events.OnTick.Add(M.processBunkerQueue)
