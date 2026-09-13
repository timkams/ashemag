"""Convert Z-Anatomy OBJ exports (assimp export of the PC-Version FBX files) into atlas chunks.
Usage: python3 scripts/convert-zanatomy.py OBJ_DIRECTORY
Then: node scripts/optimize-anatomy.mjs zanatomy.json && node scripts/compress-models.mjs zanatomy.json
Source: https://github.com/LluisV/Z-Anatomy (CC BY-SA 4.0). Units cm, Y-up, +x = anatomical left, +z = anterior (same frame as BodyParts3D here).
Blender label cubes (.j groups, 6 faces) and reference planes/regions are skipped; material splits (.001/.002) of one object are merged.
"""
import sys,json,re,math
from pathlib import Path
from array import array
from collections import defaultdict
root=Path(__file__).resolve().parents[1];source=Path(sys.argv[1]);out=root/'public/models'
FILES={'SkeletalSystem100':'skeletal','MuscularSystem100':'muscular','NervousSystem100':'nervous','CardioVascular41':'vascular','VisceralSystem100':'visceral','Joints100':'connective','LymphoidOrgans100':'lymphatic'}
def system(file,name):
    n=name.lower();base=FILES[file]
    if base=='vascular':
        if 'lymph' in n:return 'lymphatic'
        if re.search(r'vein|venous|sinus|vena cava|plexus',n):return 'venous'
        if re.search(r'heart|atrium|ventricle|myocard|pericard|valve|chordae|papillary|septum|auricle|trabecul|conus|fossa ovalis|endocard|epicard|apex|coronary sulcus|interventricular sulcus',n) and 'artery' not in n:return 'cardiac'
        return 'arterial'
    if base=='visceral':
        if re.search(r'lung|bronch|trache|pleura|larynx|glott|vocal|pharyn|nasal|nose|sinus|epiglott|cricoid|thyroid cartilage|arytenoid|diaphragm',n):return 'respiratory'
        if re.search(r'kidney|renal|ureter|bladder|urethra|calyx|pelvis of',n):return 'urinary'
        if re.search(r'testis|testic|epididym|deferens|seminal|prostate|penis|scrot|spermatic|ovar|uter|vagin|tube|bulbourethral',n):return 'reproductive'
        if re.search(r'thyroid|parathyroid|adrenal|suprarenal|pituitary|hypophys|pineal|islet',n):return 'endocrine'
        return 'digestive'
    if base=='muscular' and re.search(r'fascia|retinacul|sheath|aponeurosis|membrane|arch|septum',n):return 'connective'
    if base=='nervous' and re.search(r'eye|retina|lens|iris|cornea|sclera|choroid|ciliary|zonul|vitreous|pupil|lacrimal|conjunctiv|cochlea|tympan|auditory|ossicle|malleus|incus|stapes|semicircular|vestib|labyrinth|auricle|ear',n):return 'sensory'
    return base
def display(name):
    name=name.replace("'",'').strip()
    m=re.match(r'^(.*)\.([lr])$',name)
    if m:return ('Left ' if m[2]=='l' else 'Right ')+m[1][0].lower()+m[1][1:]
    return name
bp=json.loads((out/'atlas.json').read_text());fma={c['name'].lower():c['id'] for c in bp['concepts']}
parts=[];chunks=[];blob=bytearray();chunk=0;total=0
def flush():
    global blob,chunk
    (out/f'zanatomy-src-{chunk}.bin').write_bytes(blob);chunks.append({'url':f'/models/zanatomy-src-{chunk}.bin','bytes':len(blob)});blob=bytearray();chunk+=1
def append(values,fmt):
    while len(blob)%4:blob.append(0)
    offset=len(blob);blob.extend(array(fmt,values).tobytes());return offset
for file,_ in FILES.items():
    V=array('f');N=array('f');groups=defaultdict(lambda:array('i'));counts=defaultdict(int);cur=None;order=[]
    with open(source/f'{file}.obj',errors='ignore') as fh:
        for line in fh:
            if line.startswith('v '):V.extend(map(float,line.split()[1:4]))
            elif line.startswith('vn '):N.extend(map(float,line.split()[1:4]))
            elif line.startswith('g '):
                g=line[2:].strip();cur=re.sub(r'\.\d{3}$','',g)
                if cur not in counts:order.append(cur)
            elif line.startswith('f ') and cur is not None:
                idx=[(int(t.split('/')[0]),int(t.split('//')[1]) if '//' in t else (int(t.split('/')[2]) if t.count('/')==2 and t.split('/')[2] else 0)) for t in line.split()[1:]]
                counts[cur]+=1;fl=groups[cur]
                for j in range(1,len(idx)-1):fl.extend([idx[0][0],idx[0][1],idx[j][0],idx[j][1],idx[j+1][0],idx[j+1][1]])
    nv=len(V)//3
    for g in order:
        if g.endswith('.j') or counts[g]<=6:continue
        fl=groups[g];remap={};pos=array('f');nrm=array('h');ind=array('I')
        for k in range(0,len(fl),2):
            vi,ni=fl[k],fl[k+1];vi=vi-1 if vi>0 else nv+vi;ni=ni-1 if ni>0 else len(N)//3+ni
            key=(vi,ni);j=remap.get(key)
            if j is None:
                j=len(remap);remap[key]=j;pos.extend([V[vi*3]*.01,V[vi*3+1]*.01,V[vi*3+2]*.01])
                if 0<=ni*3+2<len(N):x,y,z=N[ni*3],N[ni*3+1],N[ni*3+2]
                else:x,y,z=0,1,0
                l=math.hypot(x,y,z) or 1;nrm.extend([round(x/l*32767),round(y/l*32767),round(z/l*32767)])
            ind.append(j)
        if len(blob)>7_000_000:flush()
        po=append(pos,'f');no=append(nrm,'h');io=append(ind,'I')
        name=display(g);bounds=[[min(pos[i::3]) for i in range(3)],[max(pos[i::3]) for i in range(3)]]
        cid=fma.get(name.lower()) or 'ZA-'+re.sub(r'[^a-z0-9]+','-',name.lower()).strip('-')
        parts.append({'id':f'ZA{len(parts)+1:04d}','name':name,'conceptId':cid,'system':system(file,name),'chunk':chunk,'positions':po,'normals':no,'indices':io,'vertexCount':len(pos)//3,'indexCount':len(ind),'bounds':bounds})
        total+=len(ind)//3
    print(file,'parts so far',len(parts),'triangles',total,file=sys.stderr)
flush()
concepts=defaultdict(lambda:{'elements':[]})
for p in parts:c=concepts[p['conceptId']];c.setdefault('name',p['name']);c['elements'].append(p['id'])
for p in parts:
    m=re.match(r'^(Left|Right) (.+)$',p['name'])
    if m:
        base=m[2][0].upper()+m[2][1:];cid=fma.get(base.lower()) or 'ZA-'+re.sub(r'[^a-z0-9]+','-',base.lower()).strip('-')
        c=concepts[cid];c.setdefault('name',base)
        if p['id'] not in c['elements']:c['elements'].append(p['id'])
manifest={'version':'Z-Anatomy 2024 (PC-Version FBX export)','source':'https://github.com/LluisV/Z-Anatomy','scope':'Bones, joints, muscles, vessels, nerves, viscera, and lymphoid organs. Label markers and reference planes omitted.','parts':parts,'chunks':chunks,'triangles':total,'concepts':[{'id':k,'name':v['name'],'elements':v['elements']} for k,v in concepts.items()]}
(out/'zanatomy.json').write_text(json.dumps(manifest,separators=(',',':')))
from collections import Counter
print(json.dumps({'parts':len(parts),'concepts':len(concepts),'triangles':total,'bytes':sum(c['bytes'] for c in chunks),'chunks':len(chunks),'systems':Counter(p['system'] for p in parts),'fmaMatched':sum(1 for p in parts if p['conceptId'].startswith('FMA'))},indent=1))
