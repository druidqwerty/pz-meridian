"""Test-only live interaction helpers; never copied into the product mod."""

CONTENT = r'''
require "Moveables/ISMoveablesAction"
require "Moveables/ISMoveableSpriteProps"
require "TimedActions/ISUnbarricadeAction"
require "TimedActions/ISInventoryTransferAction"
local salvageObject,salvageSquare
local unloadingObject,unloadingDeadline
local barricadeWindow,barricadeBefore
local function namedObject(data)
 local square=getCell():getGridSquare(data.x,data.y,data.z or 0)
 if not square then return nil,nil end
 for i=0,square:getObjects():size()-1 do
  local object=square:getObjects():get(i)
  if object:getSprite() and object:getSprite():getName()==data.sprite then return object,square end
 end
 return nil,square
end
local function beginSalvageUnload(data,label)
 local p=getPlayer()
 unloadingObject=namedObject(data)
 if not unloadingObject or unloadingObject:isObjectNoContainerOrEmpty() then return false end
 local container=unloadingObject:getContainer()
 if not container then return false end
 local items={}
 for i=0,container:getItems():size()-1 do table.insert(items,container:getItems():get(i)) end
 MeridianTest.record(label.."_unload_items",#items)
 ISTimedActionQueue.clear(p); p:setBlockMovement(false)
 for _,item in ipairs(items) do
  local action=ISInventoryTransferAction:new(p,item,container,p:getInventory())
  MeridianTest.check(label.."_transfer_valid",action:isValid())
  ISTimedActionQueue.add(action)
 end
 MeridianTest.record(label.."_unload_action","real_ISInventoryTransferAction_no_direct_clear")
 unloadingDeadline=getTimestampMs()+120000
 return true
end
local function salvageUnloadReady(label)
 if unloadingObject and unloadingObject:isObjectNoContainerOrEmpty() then
  MeridianTest.check(label.."_container_emptied_by_actions",true)
  unloadingObject=nil; return true
 end
 if getTimestampMs()>unloadingDeadline then
  MeridianTest.check(label.."_container_emptied_by_actions",false)
  return false
 end
 return nil
end
local function inspectMetalDoor(data,label)
 local object=namedObject(data)
 MeridianTest.check(label.."_metal_door_native",object and instanceof(object,"IsoDoor"))
 if not object then return end
 MeridianTest.record(label.."_metal_door_sprite",object:getSprite():getName())
 MeridianTest.record(label.."_metal_door_locked",object:isLocked())
 local was=object:IsOpen()
 object:ToggleDoor(getPlayer())
 MeridianTest.check(label.."_metal_door_opens",was~=object:IsOpen())
 if was~=object:IsOpen() then object:ToggleDoor(getPlayer()) end
end
local function beginSalvage(data,label)
 local p=getPlayer()
 salvageObject,salvageSquare=namedObject(data)
 MeridianTest.check(label.."_salvage_exists",salvageObject~=nil)
 if not salvageObject then return false end
 local props=ISMoveableSpriteProps.fromObject(salvageObject)
 MeridianTest.record(label.."_salvage_sprite",props.spriteName)
 MeridianTest.record(label.."_salvage_material",props.material)
 MeridianTest.check(label.."_no_movables_cheat",not p:isMovablesCheat() and not ISMoveableDefinitions.cheat)
 local definition=ISMoveableDefinitions:getInstance().getScrapDefinition(props.material)
 -- Supply the ordinary required tools in the private diagnostic inventory only.
 if definition then
  for _,key in ipairs({"tools","tools2"}) do
   local tools=definition[key]
   if tools and #tools>0 then
    local tool=p:getInventory():AddItem(tools[1])
    if not tool then MeridianTest.check(label.."_tool_available",false); return false end
    MeridianTest.record(label.."_diagnostic_tool",tools[1])
   end
  end
 end
 local result,chance=props:canScrapObject(p)
 MeridianTest.record(label.."_scrap_chance",chance)
 MeridianTest.check(label.."_normal_scrap_allowed",result.canScrap)
 if not result.canScrap then return false end
 ISTimedActionQueue.clear(p)
 p:setBlockMovement(false)
 local hammer=p:getInventory():getFirstTypeRecurse("Base.Hammer")
 if hammer then p:setPrimaryHandItem(hammer) end
 local action=ISMoveablesAction:new(p,salvageSquare,"scrap",data.sprite,salvageObject)
 MeridianTest.record(label.."_action_duration",action:getDuration())
 MeridianTest.check(label.."_normal_action_valid",action:isValid())
 ISTimedActionQueue.add(action)
 MeridianTest.record(label.."_salvage_action","real_ISMoveablesAction_scrap_no_direct_removal")
 return true
end
local function finishSalvage(label)
 local present=false
 if salvageSquare then
  for i=0,salvageSquare:getObjects():size()-1 do
   if salvageSquare:getObjects():get(i)==salvageObject then present=true end
  end
 end
 MeridianTest.check(label.."_salvage_removed_by_action",not present)
 salvageObject=nil;salvageSquare=nil
end
local function beginUnbarricade(data,label)
 local p=getPlayer()
 barricadeWindow=namedObject(data)
 if not barricadeWindow then MeridianTest.check(label.."_window_exists",false); return false end
 MeridianTest.record(label.."_barricade_same_square",barricadeWindow:getBarricadeOnSameSquare()~=nil)
 MeridianTest.record(label.."_barricade_opposite_square",barricadeWindow:getBarricadeOnOppositeSquare()~=nil)
 local barricade=barricadeWindow:getBarricadeForCharacter(p)
 MeridianTest.check(label.."_native_barricade",barricade and instanceof(barricade,"IsoBarricade"))
 if not barricade then return false end
 barricadeBefore=barricade:getNumPlanks()
 MeridianTest.record(label.."_barricade_planks_before",barricadeBefore)
 local tool=p:getInventory():AddItem((barricade:isMetal() or barricade:isMetalBar()) and "Base.BlowTorch" or "Base.Crowbar")
 if not tool then MeridianTest.check(label.."_tool_available",false); return false end
 p:setPrimaryHandItem(tool)
 ISTimedActionQueue.clear(p); p:setBlockMovement(false)
 local action=ISUnbarricadeAction:new(p,barricadeWindow)
 MeridianTest.check(label.."_unbarricade_action_valid",action:isValid())
 ISTimedActionQueue.add(action)
 MeridianTest.record(label.."_unbarricade_action","real_ISUnbarricadeAction_no_direct_removal")
 return true
end
local function finishUnbarricade(label)
 local barricade=barricadeWindow:getBarricadeForCharacter(getPlayer())
 local remaining=barricade and barricade:getNumPlanks() or 0
 MeridianTest.record(label.."_barricade_planks_after",remaining)
 MeridianTest.check(label.."_unbarricade_removed_by_action",not barricade or remaining<barricadeBefore)
 barricadeWindow=nil
end
'''
