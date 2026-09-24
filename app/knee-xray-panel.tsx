import {useEffect,useRef,useState} from 'react';
import {Bone,ImagePlus,RefreshCw,ScanLine,Trash2,X} from 'lucide-react';
import {Button} from '@/components/ui/button';
import {Badge} from '@/components/ui/badge';
import {Spinner} from '@/components/ui/spinner';
import {MAX_XRAYS,MAX_XRAY_BYTES,XRAY_ACCEPT,analyzeKneeXrays,checkXrayFile,formatBytes,type KneeXrayResult} from './knee-xray';
const GRADES=[0,1,2,3,4] as const;
interface Xray {id:string;file:File;url:string;dimensions?:string;unreadable?:boolean}
interface Props {open:boolean;onClose:()=>void;onViewAnatomy?:()=>void}
let nextId=0;
const sameFile=(a:File,b:File)=>a.name===b.name&&a.size===b.size&&a.lastModified===b.lastModified;
/** Upload up to two knee X-rays. Stays mounted while hidden so selections survive switching panels. */
export default function KneeXrayPanel({open,onClose,onViewAnatomy}:Props){
 const [xrays,setXrays]=useState<Xray[]>([]),[errors,setErrors]=useState<string[]>([]),[results,setResults]=useState<KneeXrayResult[]>([]),[analyzing,setAnalyzing]=useState(false);
 const heading=useRef<HTMLHeadingElement>(null),addInput=useRef<HTMLInputElement>(null),replaceInput=useRef<HTMLInputElement>(null),replaceTarget=useRef<string|null>(null),latest=useRef(xrays),abort=useRef<AbortController|null>(null);
 latest.current=xrays;
 useEffect(()=>()=>{abort.current?.abort();latest.current.forEach(x=>URL.revokeObjectURL(x.url));},[]);
 useEffect(()=>{if(open)heading.current?.focus();},[open]);
 const create=(file:File):Xray=>({id:`xray-${++nextId}`,file,url:URL.createObjectURL(file)});
 const update=(id:string,patch:Partial<Xray>)=>setXrays(list=>list.map(x=>x.id===id?{...x,...patch}:x));
 const add=(files:File[])=>{
  const added:Xray[]=[],problems:string[]=[];
  for(const file of files){
   const problem=checkXrayFile(file)??([...xrays,...added].some(x=>sameFile(x.file,file))?`“${file.name}” is already selected.`:null);
   if(problem)problems.push(problem);
   else if(xrays.length+added.length>=MAX_XRAYS)problems.push(`Only ${MAX_XRAYS} X-rays can be analyzed at once, so “${file.name}” was not added.`);
   else added.push(create(file));
  }
  setXrays([...xrays,...added]);setErrors(problems);if(added.length)setResults([]);
 };
 const replace=(file:File|undefined)=>{
  const old=xrays.find(x=>x.id===replaceTarget.current);replaceTarget.current=null;if(!file||!old)return;
  const problem=checkXrayFile(file)??(xrays.some(x=>x!==old&&sameFile(x.file,file))?`“${file.name}” is already selected.`:null);
  if(problem){setErrors([problem]);return;}
  URL.revokeObjectURL(old.url);const next=create(file);setXrays(xrays.map(x=>x===old?next:x));setErrors([]);setResults([]);
 };
 const remove=(old:Xray)=>{URL.revokeObjectURL(old.url);setXrays(xrays.filter(x=>x!==old));setErrors([]);setResults([]);heading.current?.focus();};
 const unreadable=xrays.some(x=>x.unreadable);
 const analyze=async()=>{
  if(!xrays.length||unreadable)return;
  const controller=new AbortController();abort.current=controller;setAnalyzing(true);setErrors([]);setResults([]);
  try{
   const outcome=await analyzeKneeXrays(xrays.map(x=>x.file),controller.signal);
   if(outcome.status==='ok')setResults(outcome.results);else setErrors([outcome.message]);
  }
  catch(e){if(!(e instanceof DOMException&&e.name==='AbortError'))setErrors([e instanceof Error?e.message:'The X-rays could not be analyzed. Please try again.']);}
  finally{if(abort.current===controller){abort.current=null;setAnalyzing(false);}}
 };
 return <section className="xray-panel glass" hidden={!open} aria-label="Knee X-ray upload" aria-busy={analyzing} onKeyDown={e=>{if(e.key==='Escape')onClose();}}>
  <div className="panel-heading"><span className="xray-title"><h2 ref={heading} tabIndex={-1}>Knee X-rays</h2><Badge variant="secondary" className="small-number">{xrays.length}/{MAX_XRAYS}</Badge></span><Button variant="ghost" className="icon-button" onClick={onClose} aria-label="Close knee X-rays"><X size={18}/></Button></div>
  <p className="xray-note">Add up to {MAX_XRAYS} knee X-rays as PNG or JPEG. This is an educational proof of concept, not a diagnosis.</p>
  <div className="xray-slots">
   {xrays.map((x,i)=><figure className={`xray-slot ${x.unreadable?'is-error':''}`} key={x.id}>
    <div className="xray-preview">{x.unreadable?<span>Preview unavailable</span>:<img src={x.url} alt={`Knee X-ray ${i+1}: ${x.file.name}`} onLoad={e=>update(x.id,{dimensions:`${e.currentTarget.naturalWidth} × ${e.currentTarget.naturalHeight}`})} onError={()=>update(x.id,{unreadable:true})}/>}</div>
    <figcaption><strong title={x.file.name}>{x.file.name}</strong><span>{x.unreadable?'This file could not be read as an image.':[formatBytes(x.file.size),x.dimensions].filter(Boolean).join(' · ')}</span></figcaption>
    <div className="xray-actions"><Button variant="ghost" disabled={analyzing} aria-label={`Replace ${x.file.name}`} onClick={()=>{replaceTarget.current=x.id;replaceInput.current?.click();}}><RefreshCw size={14}/>Replace</Button><Button variant="ghost" disabled={analyzing} aria-label={`Remove ${x.file.name}`} onClick={()=>remove(x)}><Trash2 size={14}/>Remove</Button></div>
   </figure>)}
   {Array.from({length:MAX_XRAYS-xrays.length},(_,i)=><Button variant="ghost" className="xray-add" key={`empty-${i}`} disabled={analyzing} onClick={()=>addInput.current?.click()}><ImagePlus size={20}/><strong>Add X-ray</strong><span>PNG or JPEG · up to {formatBytes(MAX_XRAY_BYTES)}</span></Button>)}
  </div>
  {errors.length>0&&<div className="xray-errors" role="alert">{errors.map(m=><p key={m}>{m}</p>)}</div>}
  {results.length>0&&<div className="xray-results" role="status">
   {results.map((r,i)=><article className="xray-result" key={r.imageId}>
    <p className="xray-eyebrow">Patient X-ray</p>
    <div className="xray-result-image">{xrays[i]&&<img src={xrays[i].url} alt={`Knee X-ray: ${r.fileName}`}/>}</div>
    <p className="xray-result-status"><span className="xray-status-dot"/>Analysis complete</p>
    <p className="xray-eyebrow">AI assessment</p>
    <dl className="xray-assessment">
     <div><dt>{r.task}</dt></div>
     <div><dt>KL grade</dt><dd>{r.grade}</dd></div>
     <div><dt>Confidence</dt><dd>{Math.round(r.confidence*100)}%</dd></div>
    </dl>
    <p className="xray-subhead">Grade probabilities</p>
    <ul className="xray-probabilities">{GRADES.map(gi=>{
     const key=`grade${gi}` as keyof typeof r.probabilities,p=r.probabilities[key];
     return <li key={key}><span>Grade {gi}</span><span className="xray-bar"><span style={{width:`${Math.round(p*100)}%`}}/></span><span>{Math.round(p*100)}%</span></li>;
    })}</ul>
    {r.tkrRisk.aboveThreshold&&<p className="xray-tkr-flag">Elevated total-knee-replacement risk signal ({Math.round(r.tkrRisk.probability*100)}%).</p>}
    <p className="xray-model">Model: {r.model.name} ({r.model.checkpoint})</p>
    <ul className="xray-limitations">{r.limitations.map(l=><li key={l}>{l}</li>)}</ul>
    <p className="xray-disclaimer">AI-generated research result — not a medical diagnosis.</p>
    {onViewAnatomy&&<Button variant="ghost" className="xray-anatomy-link" onClick={onViewAnatomy}><Bone size={14}/>View knee anatomy in Human Atlas<span>General reference anatomy, not this patient</span></Button>}
   </article>)}
  </div>}
  <div className="xray-foot"><span aria-live="polite">{xrays.length} of {MAX_XRAYS} X-rays selected</span><Button className="primary-action xray-analyze" disabled={analyzing||!xrays.length||unreadable} onClick={analyze}>{analyzing?<Spinner aria-hidden/>:<ScanLine size={18}/>}<span>{analyzing?'Analyzing…':'Analyze Knee X-Rays'}</span></Button></div>
  <input ref={addInput} type="file" accept={XRAY_ACCEPT} multiple hidden onChange={e=>{const files=[...(e.currentTarget.files??[])];e.currentTarget.value='';add(files);}}/>
  <input ref={replaceInput} type="file" accept={XRAY_ACCEPT} hidden onChange={e=>{const file=e.currentTarget.files?.[0];e.currentTarget.value='';replace(file);}}/>
 </section>;
}
