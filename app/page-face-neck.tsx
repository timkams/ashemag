// Deep Plane Browlift UI Component
// Add this to app/page.tsx layer-presets section (around line 38)
// This creates a specialized button for deep plane anatomical viewing

import {Button} from '@/components/ui/button';
import {FACE_NECK_REGIONS} from './face-neck-config';

/**
 * INSERTION POINT in app/page.tsx around line 38:
 * 
 * <div className="layer-presets">
 *   <Button variant="ghost" ...>All</Button>
 *   <Button variant="ghost" ...>Skeleton</Button>
 *   <Button variant="ghost" ...>Organs</Button>
 *   
 *   {/* INSERT THE FOLLOWING BUTTON: */}
 *   <Button 
 *     variant="ghost" 
 *     title="Deep Plane Browlift: Face & Neck anatomy for facial aesthetic surgery"
 *     aria-pressed={state.visible.length===7&&['skeletal','muscular','nervous','arterial','venous','connective','sensory'].every(id=>state.visible.includes(id as SystemId))} 
 *     onClick={()=>setState(s=>({...s,selected:[],isolate:false,visible:['skeletal','muscular','nervous','arterial','venous','connective','sensory']}))}
 *   >
 *     Deep Plane
 *   </Button>
 * </div>
 */

// Alternative: Full component to replace layer-presets section
export function FaceNeckLayerPresets({state, setState, activeSystems, SYSTEMS}: any) {
  return (
    <div className="layer-presets">
      <Button 
        variant="ghost" 
        aria-pressed={activeSystems.every((x: any) => state.visible.includes(x.id))} 
        onClick={() => setState((s: any) => ({...s, selected: [], isolate: false, visible: activeSystems.map((x: any) => x.id)}))}
      >
        All
      </Button>
      
      <Button 
        variant="ghost" 
        aria-pressed={state.visible.length === 1 && state.visible[0] === 'skeletal'} 
        onClick={() => setState((s: any) => ({...s, selected: [], isolate: false, visible: ['skeletal']}))}
      >
        Skeleton
      </Button>
      
      <Button 
        variant="ghost" 
        aria-pressed={state.visible.length === 6 && ['cardiac', 'respiratory', 'digestive', 'urinary', 'endocrine', 'reproductive'].every(id => state.visible.includes(id as any))} 
        onClick={() => setState((s: any) => ({...s, selected: [], isolate: false, visible: ['cardiac', 'respiratory', 'digestive', 'urinary', 'endocrine', 'reproductive']}))}
      >
        Organs
      </Button>
      
      {/* DEEP PLANE BROWLIFT PRESET */}
      <Button 
        variant="ghost" 
        title="Deep Plane Browlift: Complete face and neck anatomy for surgical planning"
        aria-pressed={state.visible.length === 7 && ['skeletal', 'muscular', 'nervous', 'arterial', 'venous', 'connective', 'sensory'].every(id => state.visible.includes(id as any))} 
        onClick={() => setState((s: any) => ({
          ...s, 
          selected: [], 
          isolate: false, 
          visible: ['skeletal', 'muscular', 'nervous', 'arterial', 'venous', 'connective', 'sensory']
        }))}
      >
        Deep Plane
      </Button>
    </div>
  );
}
