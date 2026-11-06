-- Persistent first-visit hordes, created only on already loaded interior floors.
local M = Meridian
local pending, order, tick, turn = {}, {}, 0, 0
local admissionPrunedAt = -1

local function pruneForAdmission()
    -- A saturated obsolete queue must not discard the new room's load events.
    -- At most one 2048-anchor pass in a tick, even during a square-load burst.
    if admissionPrunedAt == tick then return end
    admissionPrunedAt = tick
    local cell = getCell()
    if not cell then return end
    local retained, seeded = {}, M.saved().seeded
    for _, key in ipairs(order) do
        local job = pending[key]
        if job and not seeded[key] and cell:getGridSquare(job.x, job.y, job.z) then
            retained[#retained+1] = key
        else
            pending[key] = nil
        end
    end
    order = retained
end

local function playersNow()
    local result = {}
    local players = isServer() and getOnlinePlayers() or nil
    local count = players and players:size() or getNumActivePlayers()
    for i = 0, count - 1 do
        local p = players and players:get(i) or getSpecificPlayer(i)
        if p then result[#result+1] = {x=p:getX(), y=p:getY(), z=math.floor(p:getZ())} end
    end
    return result
end

local function playerNear(x, y, z, players)
    for _, p in ipairs(players) do
        if p.z == z and (p.x-x)^2 + (p.y-y)^2 < 196 then return true end
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
    if #order >= 2048 then pruneForAdmission() end
    if #order >= 2048 then return end
    turn = turn + 1
    pending[key] = {x=x, y=y, z=z, site=site, due=0, turn=turn}
    order[#order+1] = key
end

local function seed(key, job, players)
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
                    and q:isFree(false) and not playerNear(x, y, job.z, players) then
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
    local cell = getCell()
    if not cell then return end
    local players, eligible, retained = playersNow(), {}, {}
    local seeded = M.saved().seeded
    -- One bounded queue pass per 60 ticks, not a 64-square scan for every job.
    -- Unloaded jobs cannot hold up the newly explored floor. Their next square
    -- load can enqueue them again; only successful spawns become persistent.
    for _, key in ipairs(order) do
        local job = pending[key]
        if job and not seeded[key] and cell:getGridSquare(job.x, job.y, job.z) then
            retained[#retained+1] = key
            if job.due <= tick then
                local rank, distance, protected = 1e30, 1e30, false
                local bx, by = math.floor(job.x/8)*8, math.floor(job.y/8)*8
                local x, y = bx+3.5, by+3.5
                for _, p in ipairs(players) do
                    local dz, d = math.abs(p.z-job.z), (p.x-x)^2+(p.y-y)^2
                    if dz < rank or (dz == rank and d < distance) then rank, distance = dz, d end
                    local dx, dy = math.max(bx-p.x,0,p.x-bx-7), math.max(by-p.y,0,p.y-by-7)
                    if dz == 0 and dx*dx+dy*dy < 196 then protected = true end
                end
                eligible[#eligible+1] = {key=key, job=job, rank=rank,
                    protected=protected and 1 or 0, distance=distance}
            end
        else
            pending[key] = nil
        end
    end
    order = retained
    table.sort(eligible, function(a,b)
        if a.rank ~= b.rank then return a.rank < b.rank end
        -- Do not let buckets inside the safety exclusion monopolize proximity
        -- priority while an ordinary spawnable bucket just outside it waits.
        if a.protected ~= b.protected then return a.protected < b.protected end
        if a.distance ~= b.distance then return a.distance < b.distance end
        return a.job.turn < b.job.turn
    end)
    -- Three nearby jobs plus one oldest eligible job: active players get a
    -- prompt infection, but another floor/player is never indefinitely starved.
    local chosen, selected = {}, {}
    for i=1,math.min(3,#eligible) do
        chosen[#chosen+1] = eligible[i]; selected[eligible[i].key] = true
    end
    local oldest
    for _, entry in ipairs(eligible) do
        if not selected[entry.key] and (not oldest or entry.job.turn < oldest.job.turn) then oldest = entry end
    end
    if oldest then chosen[#chosen+1] = oldest end
    for _, entry in ipairs(chosen) do
        local job = entry.job
        if seed(entry.key, job, players) then
            pending[entry.key] = nil
        else
            -- Player proximity, a population cap or temporary blocking are not
            -- permanent failures. Retry while loaded even without another load
            -- event, and rotate retry age so one blocked bucket cannot monopolize.
            turn = turn + 1; job.turn = turn; job.due = tick + 120
        end
    end
end

Events.LoadGridsquare.Add(M.queueBunkerSquare)
Events.OnTick.Add(M.processBunkerQueue)
