"""World atlas style must use vectors without revealing unvisited terrain."""
from pathlib import Path
import unittest
from lupa import LuaRuntime

SOURCE = Path(__file__).resolve().parents[1]/'mod/42/media/lua/client/Meridian/70_VectorAtlas.lua'


class Atlas(unittest.TestCase):
    def test_vector_fallback_is_world_scoped_and_preserves_fog(self):
        lua = LuaRuntime()
        lua.execute('''
            function require() end
            MainScreen={instance={inGame=true}}
            activeDir="Meridian"; originalCalls=0; styleCalls=0; paperCalls=0
            function getLotDirectories() return {size=function() return 1 end,
                get=function(s,i) assert(i==0);return activeDir end} end
            options={HideUnvisited=true,BlurUnvisited=true,UnvisitedGrid=true}
            layers={};bounds=false
            local layer={setMinZoom=function(s,v) s.minZoom=v end,
                setFilter=function() end,addFill=function() end}
            local style={getLayerByName=function(s,n) return layer end,
                newPolygonLayer=function(s,n) layers[#layers+1]=n;return layer end}
            api={setBoolean=function(s,k,v) options[k]=v end,
                setBoundsFromData=function() bounds=true end,
                getStyleAPI=function() return style end}
            panel={Type="ISWorldMap",mapAPI=api}
            MapUtils={initDefaultStyleV3=function() originalCalls=originalCalls+1 end,
                initDefaultStyleV1=function() styleCalls=styleCalls+1 end,
                overlayPaper=function() paperCalls=paperCalls+1 end}
        ''')
        lua.execute(SOURCE.read_text(encoding='utf-8'))
        lua.execute('''
            MapUtils.initDefaultStyleV3(panel)
            assert(originalCalls==1 and styleCalls==1 and paperCalls==0 and bounds)
            assert(options.ImagePyramid==false and options.Features==true)
            assert(options.HideUnvisited and options.BlurUnvisited and options.UnvisitedGrid)
            activeDir="Muldraugh, KY";bounds=false;options={}
            MapUtils.initDefaultStyleV3(panel)
            assert(originalCalls==2 and styleCalls==1 and not bounds and not next(options))
            activeDir="Meridian";MainScreen.instance.inGame=false
            MapUtils.initDefaultStyleV3(panel)
            assert(originalCalls==3 and styleCalls==1 and not next(options))
            MainScreen.instance.inGame=true;panel.Type="ISMap"
            MapUtils.initDefaultStyleV3(panel)
            assert(originalCalls==4 and styleCalls==1 and not next(options))
            panel.Type="ISWorldMap"
            MapUtils.initDefaultStyleV3(panel)
            MapUtils.initDefaultStyleV3(panel)
            assert(originalCalls==6 and styleCalls==3 and options.ImagePyramid==false)
        ''')


if __name__ == '__main__': unittest.main()
