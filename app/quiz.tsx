import {useEffect,useMemo,useState,type Dispatch,type SetStateAction} from 'react';
import {ArrowRight,Check,Layers3,MousePointerClick,Scissors,Shapes,Tag,X} from 'lucide-react';
import {Button} from '@/components/ui/button';
import {DEFAULT_VISIBLE,SYSTEMS,type Atlas,type Part,type SceneState,type SystemId} from './anatomy';
type Kind='tap'|'name'|'shape'|'system'|'side'|'peel';
const KINDS:{id:Kind;name:string;hint:string;icon:typeof Tag}[]=[
 {id:'tap',name:'Touch',hint:'Tap the named structure on the body.',icon:MousePointerClick},
 {id:'name',name:'Name',hint:'A structure is highlighted. Pick its name.',icon:Tag},
 {id:'shape',name:'Shape',hint:'Name the structure from its shape alone.',icon:Shapes},
 {id:'system',name:'System',hint:'Which system does the highlighted structure belong to?',icon:Layers3},
 {id:'side',name:'Left or right',hint:'Is the highlighted structure on the left or right?',icon:ArrowRight},
 {id:'peel',name:'Peel & find',hint:'The structure is buried. Hide systems, then tap it.',icon:Scissors},
];
const ROUND=5,DEEP:SystemId[]=['skeletal','arterial','venous','nervous','digestive','respiratory','urinary','endocrine','cardiac'],SOLID:SystemId[]=['skeletal','muscular','cardiac','digestive','respiratory','urinary','endocrine','sensory','reproductive'];
const size=(p:Part)=>(p.bounds[1][0]-p.bounds[0][0])*(p.bounds[1][1]-p.bounds[0][1])*(p.bounds[1][2]-p.bounds[0][2]);
const pick=<T,>(list:T[],n:number)=>{const copy=[...list];for(let i=copy.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[copy[i],copy[j]]=[copy[j],copy[i]];}return copy.slice(0,n);};
interface Question {target:Part;options:string[];answer:string}
interface Props {atlas:Atlas;state:SceneState;setState:Dispatch<SetStateAction<SceneState>>;onExit:()=>void}
/** Six five-question challenges built from the loaded atlas. Answers by tap read the scene selection. */
export default function Quiz({atlas,state,setState,onExit}:Props){
 const [kind,setKind]=useState<Kind|null>(null),[questions,setQuestions]=useState<Question[]>([]),[index,setIndex]=useState(0),[picked,setPicked]=useState<string|null>(null),[score,setScore]=useState(0);
 const pool=useMemo(()=>atlas.parts.filter(p=>p.system!=='integumentary'&&size(p)>4e-6&&DEFAULT_VISIBLE.includes(p.system)),[atlas]);
 const start=(k:Kind)=>{
  const solid=pool.filter(p=>SOLID.includes(p.system)&&size(p)>1.5e-5);const candidates=k==='side'?solid.filter(p=>/^(left|right) /i.test(p.name)):k==='peel'?pool.filter(p=>DEEP.includes(p.system)&&p.system!=='skeletal'):k==='tap'?solid:k==='system'?pool.filter(p=>size(p)>1.5e-5):solid;
  const qs=pick(candidates,ROUND).map(target=>{
   if(k==='system'){const others=pick(SYSTEMS.filter(s=>s.id!==target.system&&atlas.parts.some(p=>p.system===s.id)),3).map(s=>s.name);return {target,options:pick([SYSTEMS.find(s=>s.id===target.system)!.name,...others],4),answer:SYSTEMS.find(s=>s.id===target.system)!.name};}
   if(k==='side'){const answer=/^left /i.test(target.name)?'Left':'Right';return {target,options:['Left','Right'],answer};}
   const others=pick(pool.filter(p=>p.system===target.system&&p.name!==target.name),3).map(p=>p.name);return {target,options:pick([target.name,...others],4),answer:target.name};});
  setKind(k);setQuestions(qs);setIndex(0);setScore(0);setPicked(null);
 };
 const q=questions[index];
 useEffect(()=>{if(!q||!kind)return;const highlight=kind==='name'||kind==='system'||kind==='side'||kind==='shape';
  setState(s=>({...s,selected:highlight?[q.target.id]:[],isolate:kind==='shape',hidden:[],explode:0,visible:kind==='tap'||kind==='peel'?[...DEFAULT_VISIBLE]:kind==='shape'?s.visible:['skeletal'],focus:highlight?s.focus+1:s.focus,rotate:false,view:kind==='shape'?s.view:'three-quarter',reset:kind==='tap'||kind==='peel'?s.reset+1:s.reset}));},[q,kind,setState]);
 const tapped=state.selected[0];
 useEffect(()=>{if(!q||picked||(kind!=='tap'&&kind!=='peel')||!tapped)return;const hit=atlas.parts.find(p=>p.id===tapped);const right=!!hit&&(hit.id===q.target.id||hit.conceptId===q.target.conceptId||hit.name===q.target.name);setPicked(hit?.name??'?');if(right)setScore(n=>n+1);},[tapped,q,picked,kind,atlas]);
 const answer=(option:string)=>{if(picked)return;setPicked(option);if(option===q.answer)setScore(n=>n+1);if(kind==='shape')setState(s=>({...s,isolate:false}));};
 const next=()=>{setPicked(null);setIndex(i=>i+1);};
 if(!kind)return <section className="quiz-card glass" aria-label="Choose a challenge"><div className="eyebrow">SIX CHALLENGES · {ROUND} QUESTIONS EACH</div><h2>Test what you know</h2><div className="quiz-kinds">{KINDS.map(k=><Button key={k.id} variant="ghost" className="quiz-kind" onClick={()=>start(k.id)}><k.icon size={18}/><span><strong>{k.name}</strong><small>{k.hint}</small></span></Button>)}</div><Button variant="ghost" className="secondary-action" onClick={onExit}>Back to explorer</Button></section>;
 if(index>=questions.length)return <section className="quiz-card glass" role="status"><div className="eyebrow">{KINDS.find(k=>k.id===kind)!.name.toUpperCase()} · COMPLETE</div><h2>{score} / {questions.length}</h2><p>{score===questions.length?'Perfect round.':score>=3?'Solid. Try another challenge to keep the streak going.':'Keep exploring the atlas and come back.'}</p><div className="quiz-actions"><Button className="primary-action" onClick={()=>start(kind)}>Play again</Button><Button variant="ghost" className="secondary-action" onClick={()=>setKind(null)}>Other challenges</Button></div></section>;
 const correct=picked!==null&&(kind==='tap'||kind==='peel'?picked===q.target.name||atlas.parts.find(p=>p.id===tapped)?.conceptId===q.target.conceptId:picked===q.answer);
 return <section className="quiz-card glass" aria-live="polite">
  <div className="quiz-progress"><span className="eyebrow">{KINDS.find(k=>k.id===kind)!.name.toUpperCase()} · {index+1} / {questions.length}</span><span className="small-number">Score {score}</span><Button variant="ghost" className="icon-button" aria-label="Quit challenge" onClick={()=>setKind(null)}><X size={16}/></Button></div>
  {kind==='tap'||kind==='peel'?<><h2>Tap the <em>{q.target.name.toLowerCase()}</em></h2><p>{kind==='peel'?'It lies beneath other structures. Use the Systems panel to hide layers, then tap it.':'Orbit and zoom, then tap it on the body.'}</p>{picked&&<p className={`quiz-result ${correct?'good':'bad'}`}>{correct?<><Check size={14}/> Correct</>:<><X size={14}/> That was the {picked.toLowerCase()}. The answer is highlighted.</>}</p>}</>
  :<><h2>{kind==='system'?'Which system is this?':kind==='side'?'Which side of the body?':kind==='shape'?'What structure is this?':'What is the highlighted structure?'}</h2><div className="quiz-options">{q.options.map(o=><Button key={o} variant="ghost" className={`quiz-option ${picked?o===q.answer?'good':o===picked?'bad':'':''}`} disabled={!!picked} onClick={()=>answer(o)}>{o}</Button>)}</div></>}
  {picked&&<Button className="primary-action" autoFocus onClick={next}>{index+1<questions.length?'Next question':'See results'}<ArrowRight size={16}/></Button>}
 </section>;
}
