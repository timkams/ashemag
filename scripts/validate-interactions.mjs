import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createExplosionLayout} from '../app/explosion-layout.ts';
import {PointerTap} from '../app/pointer-tap.ts';
import {atlasTools} from '../app/agent-tools.ts';
import {DEFAULT_VISIBLE,SYSTEMS,explanation} from '../app/anatomy.ts';

for (const file of ['atlas.json']) {
  const atlas=JSON.parse(await readFile(new URL(`../public/models/${file}`,import.meta.url)));
  const groups=[atlas.parts,...[...new Set(atlas.parts.map(p=>p.system))].map(system=>atlas.parts.filter(p=>p.system===system))];
  for(const group of groups) for(const aspect of [.46,1,1.7]) {
    const layout=createExplosionLayout(group,aspect),cells=[...layout.cells.values()];
    assert.equal(cells.length,group.length);
    for(let i=0;i<cells.length;i++) {
      const a=cells[i];
      assert.ok(Math.abs(a.x)+a.width/2<=layout.width/2+1e-8);
      assert.ok(Math.abs(a.y)+a.height/2<=layout.height/2+1e-8);
      for(let j=i+1;j<cells.length;j++) {
        const b=cells[j];
        assert.ok(Math.abs(a.x-b.x)>=(a.width+b.width)/2-1e-8 || Math.abs(a.y-b.y)>=(a.height+b.height)/2-1e-8,'Exploded pieces overlap');
      }
    }
  }
  let selected=null;
  const [find,inspect]=atlasTools(atlas,c=>{selected=c;});
  const results=find.execute({query:'femur'});
  assert.ok(results.length>0);
  inspect.execute({id:results[0].id});
  const previous=selected;
  assert.throws(()=>inspect.execute({id:'nonexistent-structure'}));
  assert.equal(selected,previous);
  assert.throws(()=>find.execute({query:' '}));
  // BodyParts3D identifies these meshes as right/left iliotibial tracts and
  // places both beneath zone of fascia lata, not bone (GitHub issue #423).
  // https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_element_parts.txt
  // https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_inclusion_relation_list.txt
  const connective=SYSTEMS.find(system=>system.id==='connective');
  assert.ok(connective&&DEFAULT_VISIBLE.includes(connective.id));
  for(const [id,conceptId,name] of [
    ['FJ1423','FMA58776','Right iliotibial tract'],
    ['FJ1423M','FMA58777','Left iliotibial tract'],
  ]) {
    const part=atlas.parts.find(part=>part.id===id);
    assert.ok(part,`${id}: iliotibial tract mesh is missing`);
    assert.equal(part.conceptId,conceptId);
    assert.equal(part.name,name);
    assert.equal(part.system,'connective',`${id}: iliotibial tract must be in Connective tissue, not Skeleton`);
    assert.equal(explanation(part.name,part.system),connective.description);
    assert.ok(find.execute({query:conceptId}).some(result=>result.id===conceptId));
    inspect.execute({id:conceptId});
    assert.deepEqual(selected.elements,[id]);
  }
  console.log('Both iliotibial tracts are in Connective tissue and remain searchable and selectable.');
  console.log(`${file}: packing at desktop/mobile aspect ratios and search/inspection contracts passed.`);
}
const tap=new PointerTap();
tap.down(1,10,10,5);assert.equal(tap.up(1,12,11),true);
tap.down(1,10,10,5);tap.move(1,40,10);assert.equal(tap.up(1,10,10),false);
tap.down(1,10,10,12);tap.down(2,20,20,12);assert.equal(tap.up(2,20,20),false);assert.equal(tap.up(1,10,10),false);
tap.down(1,10,10,5);tap.cancel(1);assert.equal(tap.up(1,10,10),false);
tap.down(1,10,10,5);assert.equal(tap.up(1,10,10),true);
assert.equal(createExplosionLayout([]).cells.size,0);
console.log('Tap, drag, multitouch, cancellation, and empty-view checks passed.');
