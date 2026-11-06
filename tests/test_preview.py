"""Regression for PZ42.21 pre-MetaGrid vector spawn-preview initialization."""
from pathlib import Path
import unittest
from lupa import LuaRuntime

SOURCE = Path(__file__).resolve().parents[1]/'mod/42/media/lua/client/Meridian/65_MapPreview.lua'


class Preview(unittest.TestCase):
    def test_only_meridian_pregame_preview_is_initialized(self):
        lua = LuaRuntime()
        lua.execute('''
            function require() end
            function print() end
            MainScreen={instance={inGame=false}}
            options={};layers={};originalCalls=0
            local layer={setMinZoom=function() end,setFilter=function() end,
                         addFill=function() end}
            style={clear=function() layers={} end,
                newPolygonLayer=function(s,id) layers[#layers+1]=id;return layer end}
            api={getStyleAPI=function() return style end,
                setBoolean=function(s,k,v) options[k]=v end,
                setBackgroundRGBA=function() end,
                getDataCount=function() return 1 end,isDataLoaded=function() return true end,
                setBoundsFromData=function() end,resetView=function() end}
            panel={javaObject={getAPIv1=function() return api end},mapAPI=api,
                getWidth=function() return 400 end,
                parent={listbox={selected=1,items={{item={dir="Meridian"}}}}}}
            MapUtils={initDefaultStyleV1=function() error("must remain untouched") end}
            oldStyle=MapUtils.initDefaultStyleV1
            MapSpawnSelectImage={prerender=function(s)
                originalCalls=originalCalls+1
                if not s.hasResetView and s.parent.listbox.items[1].item.dir=="Meridian"
                        and not MainScreen.instance.inGame then error("invalid MetaGrid") end
            end}
        ''')
        lua.execute(SOURCE.read_text(encoding='utf-8-sig'))
        lua.execute('''
            MapSpawnSelectImage.prerender(panel)
            assert(panel.hasResetView and #layers==4 and options.HideUnvisited==false)
            assert(originalCalls==1 and MapUtils.initDefaultStyleV1==oldStyle)
            MapSpawnSelectImage.prerender(panel);assert(originalCalls==2 and #layers==4)
            panel.hasResetView=nil;panel.parent.listbox.items[1].item.dir="Muldraugh, KY"
            options={};MapSpawnSelectImage.prerender(panel)
            assert(not panel.hasResetView and not next(options) and originalCalls==3)
            MainScreen.instance.inGame=true;panel.parent.listbox.items[1].item.dir="Meridian"
            MapSpawnSelectImage.prerender(panel)
            assert(not panel.hasResetView and not next(options) and originalCalls==4)
        ''')


if __name__ == '__main__':
    unittest.main()
