"""Convert the HRA united-female v1.5 GLB (humanatlas.io) into the shared Atlas format.
Usage: python3 scripts/convert-female.py SOURCE.glb
The source has baked, aligned Y-up meter coordinates and per-mesh ontology metadata in
node.extras; no external metadata file is needed. Only a stage shift is applied.
Source and attribution: public/ATTRIBUTION.md.
"""
import sys,json,re,struct
from pathlib import Path
from array import array
root=Path(__file__).resolve().parents[1]
source=Path(sys.argv[1]).read_bytes()
jl=struct.unpack_from('<I',source,12)[0];doc=json.loads(source[20:20+jl]);binstart=20+jl+8;binary=memoryview(source)[binstart:]
out=root/'public/models';out.mkdir(parents=True,exist_ok=True)
formats={5126:('f',4),5125:('I',4),5123:('H',2),5121:('B',1)}
widths={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}
def read(index):
    a=doc['accessors'][index];view=doc['bufferViews'][a['bufferView']];fmt,sz=formats[a['componentType']];width=widths[a['type']]
    offset=view.get('byteOffset',0)+a.get('byteOffset',0);stride=view.get('byteStride',width*sz)
    if stride==width*sz:
        v=array(fmt);v.frombytes(binary[offset:offset+a['count']*width*sz]);return v
    values=array(fmt)
    for i in range(a['count']):values.extend(struct.unpack_from('<'+fmt*width,binary,offset+i*stride))
    return values

nodes=doc['nodes']
parent={}
for i,n in enumerate(nodes):
    for c in n.get('children',[]):parent[c]=i
SYSTEM_RE=re.compile(r'^VH_F_(\w+)_system$')
root_children={c for c in nodes[0].get('children',[])}
system_roots={i:SYSTEM_RE.match(nodes[i]['name']).group(1) for i in root_children if SYSTEM_RE.match(nodes[i]['name'])}
def base_system(i):
    # Only the direct children of the root are real system groupings; deeper nodes can
    # coincidentally match the "*_system" name pattern without being one (e.g. a mislabeled
    # "trachea_of_respiratory_system" leaf), so keep climbing past those.
    while i in parent:
        i=parent[i]
        if i in system_roots:return system_roots[i]
    return 'connective'
def under_placenta(i):
    while i in parent:
        i=parent[i]
        if nodes[i].get('name')=='VH_F_placenta':return True
    return False
def derive_system(i,label,name):
    context=f'{label} {name}'.lower()
    if under_placenta(i):return 'pregnancy'
    base=base_system(i)
    if base=='circulatory':return 'venous' if any(v in context for v in ['vein','venous','vena_']) else 'cardiac' if 'heart' in context else 'arterial'
    if base=='nervous' and any(v in context for v in ['eye','ear','retina','lens','optic']):return 'sensory'
    return base

parts=[];chunks=[];blob=bytearray();triangles=0
raw={}  # nodeIndex -> (positions array, normals array, indices array)
for i,node in enumerate(nodes):
    if 'mesh' not in node:continue
    assert not any(k in node for k in ['matrix','translation','rotation','scale']),node['name']
    positions=array('f');normals=array('f');indices=array('I')
    for primitive in doc['meshes'][node['mesh']]['primitives']:
        assert primitive.get('mode',4)==4
        pos=read(primitive['attributes']['POSITION']);norm=read(primitive['attributes']['NORMAL']);ind=read(primitive['indices']);base=len(positions)//3
        positions.extend(pos);normals.extend(norm);indices.extend(v+base for v in ind)
    raw[i]=(positions,normals,indices);triangles+=len(indices)//3

shift=-min(raw[i][0][a] for i in raw for a in range(1,len(raw[i][0]),3))
nodeparts={}
for i,node in enumerate(nodes):
    if i not in raw:continue
    positions,normals,indices=raw[i]
    for a in range(1,len(positions),3):positions[a]+=shift
    normals16=array('h',(max(-32767,min(32767,round(v*32767))) for v in normals))
    extras=node.get('extras',{});label=extras.get('label') or node['name']
    if label.strip() in ['','-','None','NA']:label=node['name']
    name=re.sub(r'^VH_F_','',node['name']).replace('_',' ')
    ontology=(extras.get('ontologyid') or '').strip()
    conceptId=ontology.replace(':','') if ontology and ontology not in ['-','None','NA'] else 'HRA:'+node['name']
    system=derive_system(i,label,node['name'])
    if len(blob)>6_000_000:
        (out/f'source-female-{len(chunks)}.bin').write_bytes(blob);chunks.append({'url':f'/models/source-female-{len(chunks)}.bin','bytes':len(blob)});blob=bytearray()
    def append(values,fmt):
        while len(blob)%4:blob.append(0)
        offset=len(blob);blob.extend(array(fmt,values).tobytes());return offset
    po=append(positions,'f');no=append(normals16,'h');io=append(indices,'I')
    bounds=[[min(positions[a::3]) for a in range(3)],[max(positions[a::3]) for a in range(3)]]
    part={'id':node['name'],'name':label,'conceptId':conceptId,'system':system,'chunk':len(chunks),'positions':po,'normals':no,'indices':io,'vertexCount':len(positions)//3,'indexCount':len(indices),'bounds':bounds}
    parts.append(part);nodeparts[i]=part['id']
(out/f'source-female-{len(chunks)}.bin').write_bytes(blob);chunks.append({'url':f'/models/source-female-{len(chunks)}.bin','bytes':len(blob)})

def descendants(i):
    n=nodes[i];return ([nodeparts[i]] if i in nodeparts else [])+[p for child in n.get('children',[]) for p in descendants(child)]
concepts=[];seen=set()
for i,node in enumerate(nodes):
    elements=descendants(i)
    if not elements:continue
    label=node.get('extras',{}).get('label') or node.get('name','Structure')
    name=re.sub(r'^VH_F_','',label if label.strip() not in ['','-','None','NA'] else node.get('name','Structure')).replace('_',' ')
    identity=(name,tuple(elements))
    if identity in seen:continue
    seen.add(identity);concepts.append({'id':'HRA:'+node.get('name',str(i)),'name':name,'elements':elements})

atlas={'version':'HRA united-female v1.5','sex':'female','source':'Human Reference Atlas','scope':'Female reference assembly · partial skeleton and muscle coverage','parts':parts,'concepts':concepts,'chunks':chunks,'triangles':triangles}
(out/'atlas-female.json').write_text(json.dumps(atlas,separators=(',',':')))
print(json.dumps({'parts':len(parts),'concepts':len(concepts),'triangles':triangles,'bytes':sum(c['bytes'] for c in chunks),'stageShift':shift,'systems':sorted(set(p['system'] for p in parts))}))
