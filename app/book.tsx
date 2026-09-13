import {useMemo,useState} from 'react';
import {ChevronLeft,ChevronRight,X} from 'lucide-react';
import {Button} from '@/components/ui/button';
import {SYSTEMS,type Atlas,type Concept,type SceneState} from './anatomy';
interface Props {atlas:Atlas;state:SceneState;chosen:Concept|null;choose:(c:Concept)=>void;open:boolean;onClose:()=>void}
/** Browsable index of every named structure. Selecting a page isolates it in the scene and opens its detail sheet. */
export default function Book({atlas,chosen,choose,open,onClose}:Props){
 const [query,setQuery]=useState(''),[system,setSystem]=useState('');
 const partSystem=useMemo(()=>new Map(atlas.parts.map(p=>[p.id,p.system])),[atlas]);
 const pages=useMemo(()=>{const term=query.toLowerCase().trim();return atlas.concepts.filter(c=>(!system||c.elements.some(id=>partSystem.get(id)===system))&&(!term||c.name.toLowerCase().includes(term))).sort((a,b)=>a.name.localeCompare(b.name));},[atlas,query,system,partSystem]);
 const index=chosen?pages.findIndex(c=>c.id===chosen.id):-1;
 const step=(d:number)=>{const next=pages[index<0?0:index+d];if(next)choose(next);};
 return <section className={`layers-panel book-panel glass ${open?'mobile-open':''}`} aria-label="Anatomy book index">
  <div className="panel-heading"><span>Pages<small className="small-number"> {pages.length.toLocaleString()}</small></span><Button variant="ghost" className="mobile-only icon-button" onClick={onClose} aria-label="Close index"><X size={18}/></Button></div>
  <input className="book-search" value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search pages" aria-label="Filter pages"/>
  <select className="book-filter" value={system} onChange={e=>setSystem(e.target.value)} aria-label="Filter by system"><option value="">All systems</option>{SYSTEMS.filter(s=>atlas.parts.some(p=>p.system===s.id)).map(s=><option key={s.id} value={s.id}>{s.name}</option>)}</select>
  <div className="system-list book-list">{pages.slice(0,400).map(c=><Button variant="ghost" key={c.id} className={`book-page ${chosen?.id===c.id?'active':''}`} aria-current={chosen?.id===c.id} onClick={()=>{choose(c);onClose();}}><span>{c.name}</span><span className="small-number">{c.elements.length}</span></Button>)}{pages.length>400&&<p className="search-note">Showing 400 of {pages.length.toLocaleString()} pages. Type to narrow.</p>}</div>
  <div className="panel-foot"><Button variant="ghost" disabled={index<=0} onClick={()=>step(-1)} aria-label="Previous page"><ChevronLeft size={15}/>Prev</Button><span>{index>=0?`Page ${index+1}`:'Pick a page'}</span><Button variant="ghost" disabled={index>=pages.length-1} onClick={()=>step(1)} aria-label="Next page">Next<ChevronRight size={15}/></Button></div>
 </section>;
}
