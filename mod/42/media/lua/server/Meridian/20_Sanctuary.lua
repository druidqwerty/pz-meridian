-- No surface infection inside Meridian's walls. Negative floors are excluded.
local M = Meridian
M.sanctuaryRemoved = 0

function M.enforceSanctuary(zombie)
    if not M.authoritative() or not zombie then return end
    if not M.isSafeSurface(zombie:getX(), zombie:getY(), zombie:getZ()) then return end
    zombie:removeFromWorld()
    zombie:removeFromSquare()
    M.sanctuaryRemoved = M.sanctuaryRemoved + 1
end

function M.sweepSanctuary()
    if not M.authoritative() then return end
    local cell = getCell()
    if not cell then return end
    local zombies = cell:getZombieList()
    -- Iterate backwards because removeFromWorld mutates the cell's list.
    for i = zombies:size() - 1, 0, -1 do M.enforceSanctuary(zombies:get(i)) end
end

if Events.OnZombieUpdate then Events.OnZombieUpdate.Add(M.enforceSanctuary) end
Events.OnGameStart.Add(M.sweepSanctuary)
Events.EveryOneMinute.Add(M.sweepSanctuary)
