"""Private native room-light oracle, inserted only into isolated playtest caches.

The probe never creates lights, changes power availability, spawns bulbs or calls
Room.createLights. It toggles the authored native switch and restores lab state.
Verified against installed B42.21 javap and vanilla ISToggleLightAction.
"""

CONTENT = r'''
local lightProbe
local function optionalLightValue(label,key,fn)
 local ok,value=pcall(fn)
 MeridianTest.record(label.."_"..key,ok and tostring(value) or "unavailable")
 return ok and value or nil
end
local function nativeLightSample(label)
 if not lightProbe then return nil end
 local s=lightProbe.roomSquare
 local value=optionalLightValue(label,"observer_lightlevel",function() return s:getLightLevel(0) end)
 -- Public Java fields are not exposed as Lua properties in B42. Do not inspect
 -- room.roomLights/RoomDef.lightsActive: even pcall emits native Lua stack traces.
 return value
end
local function restoreLighting(label)
 if not lightProbe then return end
 local state=lightProbe
 if state.object:isActivated()~=state.initial then state.object:toggle() end
 MeridianTest.check(label.."_switch_restored",state.object:isActivated()==state.initial)
 if state.torch then state.torch:setActivated(state.torchActive) end
 getGameTime():setTimeOfDay(state.time)
 MeridianTest.record(label.."_lab_time_restored",getGameTime():getTimeOfDay())
 MeridianTest.record(label.."_diagnostic_torch_restored",not state.torch or state.torch:isActivated()==state.torchActive)
 lightProbe=nil
end
MeridianTest.restoreLighting=restoreLighting
local function beginLighting(data,label)
 local object,square=namedObject(data)
 MeridianTest.check(label.."_authored_switch_native",object and instanceof(object,"IsoLightSwitch"))
 if not object or not instanceof(object,"IsoLightSwitch") then return false end
 local room=square:getRoom()
 MeridianTest.check(label.."_switch_in_room",room~=nil)
 if not room then return false end
 MeridianTest.check(label.."_room_has_light_switches",room:hasLightSwitches())
 local native=room:getLightSwitches(); local found=false
 for i=0,native:size()-1 do if native:get(i)==object then found=true end end
 MeridianTest.check(label.."_switch_registered_to_room",found)
 optionalLightValue(label,"switch_grid_power",function() return square:haveElectricity() end)
 optionalLightValue(label,"switch_can_switch",function() return object:canSwitchLight() end)
 local p=getPlayer(); local observer
 for radius=1,8 do
  for dx=-radius,radius do for dy=-radius,radius do
   local candidate=getCell():getGridSquare(data.x+dx,data.y+dy,data.z or 0)
   if not observer and candidate and candidate:getRoom()==room and candidate:isFree(false) then observer=candidate end
  end end
  if observer then break end
 end
 MeridianTest.check(label.."_observer_inside_switch_room",observer~=nil)
 if not observer then return false end
 -- This is explicitly a diagnostic viewpoint placement, not a traversal test.
 p:teleportTo(observer:getX()+0.5,observer:getY()+0.5,observer:getZ())
 MeridianTest.record(label.."_diagnostic_observer",observer:getX()..","..observer:getY()..","..observer:getZ())
 local torch=p:getPrimaryHandItem()
 if torch and not torch:canBeActivated() then torch=nil end
 lightProbe={object=object,room=room,roomSquare=observer,initial=object:isActivated(),
             time=getGameTime():getTimeOfDay(),torch=torch,torchActive=torch and torch:isActivated()}
 if torch then torch:setActivated(false) end
 getGameTime():setTimeOfDay(23)
 MeridianTest.check(label.."_night_diagnostic",getGameTime():getTimeOfDay()>22)
 MeridianTest.check(label.."_diagnostic_torch_off",not torch or not torch:isActivated())
 if not object:isActivated() then object:toggle() end
 MeridianTest.check(label.."_native_switch_on",object:isActivated())
 MeridianTest.record(label.."_native_action","authored_IsoLightSwitch_toggle_no_light_creation")
 return true
end
local function lightingOnFrame(label)
 if not lightProbe then return false end
 lightProbe.on=nativeLightSample(label.."_on")
 MeridianTest.check(label.."_on_state_persisted",lightProbe.object:isActivated())
 shot(label.."_night_native_light_on")
 return true
end
local function lightingSwitchOff(label)
 if not lightProbe then return end
 if lightProbe.object:isActivated() then lightProbe.object:toggle() end
 MeridianTest.check(label.."_native_switch_off",not lightProbe.object:isActivated())
end
local function lightingOffFrame(label)
 if not lightProbe then return end
 local off=nativeLightSample(label.."_off")
 MeridianTest.check(label.."_off_state_persisted",not lightProbe.object:isActivated())
 if type(off)=="number" and type(lightProbe.on)=="number" then
  MeridianTest.record(label.."_native_brightness_delta",lightProbe.on-off)
  -- Numerical brightness is recorded, not substituted for inspecting both images.
 end
 local delta=type(off)=="number" and type(lightProbe.on)=="number" and lightProbe.on-off or 0
 MeridianTest.check(label.."_native_illumination_observed",delta>0.01)
 shot(label.."_night_native_light_off")
end
'''
