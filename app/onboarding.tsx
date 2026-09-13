import {useEffect,useState} from 'react';
import {Hand,MousePointerClick,ZoomIn} from 'lucide-react';
import {Button} from '@/components/ui/button';
const KEY='human-atlas-onboarded';
const STEPS=[
 {icon:Hand,title:'Rotate the body',body:'Drag with one finger or the left mouse button. Right-drag or two-finger drag pans. The ¾, F, S, B buttons jump to preset angles.'},
 {icon:ZoomIn,title:'Zoom in on detail',body:'Scroll or pinch to zoom. Use the Explode slider to pull structures apart by depth, or lay every piece out as an inventory.'},
 {icon:MousePointerClick,title:'Tap to inspect',body:'Tap any structure to name it and read about it. From there you can isolate it, focus the camera, hide it, or jump to adjacent structures. Press / to search.'},
];
/** Three-step controls tour shown once per browser. */
export default function Onboarding(){
 const [step,setStep]=useState(-1);
 useEffect(()=>{try{if(!localStorage.getItem(KEY))setStep(0);}catch{setStep(0);}},[]);
 const done=()=>{setStep(-1);try{localStorage.setItem(KEY,'1');}catch{/* private mode */}};
 if(step<0)return null;
 const s=STEPS[step],Icon=s.icon;
 return <div className="onboarding-backdrop" role="presentation" onClick={done}><div className="onboarding glass" role="dialog" aria-modal="true" aria-labelledby="onboarding-title" onClick={e=>e.stopPropagation()}>
  <div className="eyebrow">CONTROLS · {step+1} / {STEPS.length}</div>
  <div className="onboarding-icon"><Icon size={28}/></div>
  <h2 id="onboarding-title">{s.title}</h2><p>{s.body}</p>
  <div className="onboarding-dots">{STEPS.map((_,i)=><i key={i} className={i===step?'on':''}/>)}</div>
  <div className="onboarding-actions"><Button variant="ghost" onClick={done}>Skip</Button><Button className="primary-action" autoFocus onClick={()=>step+1<STEPS.length?setStep(step+1):done()}>{step+1<STEPS.length?'Next':'Start exploring'}</Button></div>
 </div></div>;
}
