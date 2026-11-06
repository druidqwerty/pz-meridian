"""Read-only native sprite-registry oracle; text tile metadata is insufficient.

Never use getSprite(name) to test existence: B42 AddSprite creates placeholders.
getNamedMap()/containsKey/get are verified native read-only lookups.
"""
CONTENT = r'''
local function inspectSpriteRegistry(names)
 local registry=IsoSpriteManager.instance:getNamedMap()
 local initialSize=registry:size()
 local negative="__MeridianPrivateOracle_MissingSpriteControl__"
 MeridianTest.check("sprite_registry_negative_control_absent",not registry:containsKey(negative))
 local missing,empty,trees=0,0,0
 for _,name in ipairs(names or {}) do
  if not registry:containsKey(name) then
   missing=missing+1; MeridianTest.record("sprite_registry_missing",name)
  else
   local sprite=registry:get(name)
   if not sprite or sprite:hasNoTextures() then
    local size=sprite and tonumber(sprite:getProperties():get("tree"))
    if sprite and sprite:getType()==IsoObjectType.tree and size and size>=1 and size<=8 then
     -- Native CellLoader exempts tree proxies from its ordinary texture check;
     -- NatureTrees/ErosionObj later replace them with seasonal stage artwork.
     trees=trees+1; MeridianTest.record("sprite_registry_native_seasonal_tree_proxy",name)
    else
     empty=empty+1; MeridianTest.record("sprite_registry_textureless",name)
    end
   end
  end
 end
 MeridianTest.record("sprite_registry_checked",#(names or {}))
 MeridianTest.record("sprite_registry_missing_count",missing)
 MeridianTest.record("sprite_registry_textureless_count",empty)
 MeridianTest.record("sprite_registry_seasonal_tree_proxy_count",trees)
 MeridianTest.check("all_native_sprites_registered",#(names or {})>0 and missing==0)
 MeridianTest.check("native_sprite_textures_or_verified_tree_proxy",empty==0)
 MeridianTest.check("sprite_registry_lookup_did_not_mutate",registry:size()==initialSize and not registry:containsKey(negative))
end
'''
