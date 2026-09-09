import {createContext,useContext,useEffect,useMemo,useState,type ReactNode} from 'react';
import {SYSTEMS,EXPLANATIONS,type SystemId} from './anatomy';

export type Lang='en'|'uz';
export const LANGS:Lang[]=['en','uz'];

// Interface strings. English is the source; Uzbek (Latin) mirrors every key.
type Dict=Record<string,string>;
const UI:Record<Lang,Dict>={
 en:{
  'eyebrow.interactive':'INTERACTIVE ANATOMY',
  'app.title':'Human Atlas',
  'meta.pieces':'{count} modeled pieces',
  'aria.panels':'Explorer panels',
  'aria.searchAnatomy':'Search anatomy',
  'action.find':'Find a structure',
  'aria.about':'About this atlas',
  'aria.switchLang':'Switch language',
  'aria.layers':'Anatomical layers',
  'label.systems':'Systems',
  'aria.closeSystems':'Close systems',
  'preset.all':'All',
  'preset.skeleton':'Skeleton',
  'preset.organs':'Organs',
  'title.showOnly':'Show only {name}',
  'aria.show':'Show {name}',
  'label.visible':'{count} pieces visible',
  'action.hideAll':'Hide all',
  'aria.findAnatomy':'Find anatomy',
  'aria.closeSearch':'Close search',
  'search.placeholder':'Heart, femur, cranial nerve…',
  'aria.searchNamed':'Search named anatomical structures',
  'search.empty':'No structures match your search.',
  'count.pieces':'{count} pieces',
  'count.piece':'{count} piece',
  'search.noteRefine':'Showing up to 80 matches. Refine your search to find smaller structures.',
  'search.noteStart':'Start with a major organ, or search every named structure.',
  'aria.camera':'Camera controls',
  'view.three-quarter':'three-quarter',
  'view.front':'front',
  'view.side':'side',
  'view.back':'back',
  'title.view':'{view} view',
  'aria.pauseRotation':'Pause rotation',
  'aria.rotateBody':'Rotate body',
  'title.autoRotate':'Auto rotate',
  'aria.resetViewLayers':'Reset view and layers',
  'title.reset':'Reset',
  'caption.selected':'SELECTED STRUCTURE',
  'caption.inventory':'ANATOMICAL INVENTORY',
  'caption.separated':'SEPARATED STRUCTURES',
  'caption.adultMale':'ADULT HUMAN · MALE',
  'aria.openLayers':'Open system layers',
  'label.explode':'Explode anatomy',
  'slider.assembled':'Assembled',
  'slider.everyPiece':'Every piece',
  'aria.assembleReset':'Assemble and reset',
  'footer.pan':'Drag to pan',
  'footer.orbit':'Drag to orbit',
  'footer.zoom':'Pinch to zoom',
  'footer.inspect':'Tap to inspect',
  'action.sourceCredits':'Source & credits',
  'loading.preparing':'Preparing the anatomy',
  'loading.progress':'{progress}% · Loading {count} pieces',
  'error.reload':'Reload viewer',
  'error.catalogue':'The anatomy catalogue could not be loaded.',
  'detail.anatomy':'ANATOMY',
  'detail.systemOverview':'System overview · structure identified from source anatomy',
  'detail.atlasRef':'Atlas reference',
  'detail.selectedPieces':'Selected pieces',
  'detail.included':'Included structures',
  'detail.andMore':'And {n} more modeled pieces.',
  'detail.viewSource':'View anatomical source',
  'detail.showSurrounding':'Show surrounding anatomy',
  'detail.isolate':'Isolate structure',
  'detail.clear':'Clear selection',
  'about.eyebrow':'SOURCE & SCOPE',
  'about.title':'A body, revealed.',
  'about.intro':'Explore the adult male reference anatomy from BodyParts3D.',
  'about.male':'Male · BodyParts3D',
  'about.meshes':'2,234 individual meshes and 3,432 named concepts from an adult male reference anatomy.',
  'about.p2':'This reference does not contain every human structure or variation. Named concepts can contain multiple pieces; each source mesh is rendered once.',
  'about.p3':'Colors and system groupings are designed for exploration. The geometry is simplified for the web, and short explanations provide general educational context. This is an anatomical reference, not a diagnostic or surgical tool.',
  'about.sourceHeading':'Source',
  'about.license':'BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International.',
  'about.datasetLicense':'Dataset license',
  'about.geometry':'Original geometry & metadata',
  'about.publication':'Read the source publication',
  'scene.noWebGL':'This browser could not start the 3D viewer. Please try a browser with WebGL enabled.',
  'scene.canvasAria':'Interactive human anatomy. Drag to orbit, pinch or scroll to zoom, and tap a structure to inspect it.',
  'scene.assembleFail':'Could not assemble anatomy geometry.',
  'scene.loadFail':'Could not load the anatomy.',
  'scene.paused':'The 3D session was paused by your device. Reload to continue.',
 },
 uz:{
  'eyebrow.interactive':'INTERAKTIV ANATOMIYA',
  'app.title':'Inson Atlasi',
  'meta.pieces':'{count} ta modellashtirilgan bo‘lak',
  'aria.panels':'Tadqiqot panellari',
  'aria.searchAnatomy':'Anatomiyani qidirish',
  'action.find':'Tuzilmani topish',
  'aria.about':'Atlas haqida',
  'aria.switchLang':'Tilni almashtirish',
  'aria.layers':'Anatomik qatlamlar',
  'label.systems':'Tizimlar',
  'aria.closeSystems':'Tizimlarni yopish',
  'preset.all':'Hammasi',
  'preset.skeleton':'Skelet',
  'preset.organs':'A‘zolar',
  'title.showOnly':'Faqat {name}ni ko‘rsatish',
  'aria.show':'{name}ni ko‘rsatish',
  'label.visible':'{count} ta bo‘lak ko‘rinmoqda',
  'action.hideAll':'Hammasini yashirish',
  'aria.findAnatomy':'Anatomiyani topish',
  'aria.closeSearch':'Qidiruvni yopish',
  'search.placeholder':'Yurak, son suyagi, bosh miya nervi…',
  'aria.searchNamed':'Nomlangan anatomik tuzilmalarni qidirish',
  'search.empty':'Qidiruvingizga mos tuzilma topilmadi.',
  'count.pieces':'{count} ta bo‘lak',
  'count.piece':'{count} ta bo‘lak',
  'search.noteRefine':'80 tagacha moslik ko‘rsatilmoqda. Kichikroq tuzilmalarni topish uchun qidiruvni aniqlashtiring.',
  'search.noteStart':'Yirik a‘zodan boshlang yoki har qanday nomlangan tuzilmani qidiring.',
  'aria.camera':'Kamera boshqaruvi',
  'view.three-quarter':'chorak burchak',
  'view.front':'old',
  'view.side':'yon',
  'view.back':'orqa',
  'title.view':'{view} ko‘rinishi',
  'aria.pauseRotation':'Aylanishni to‘xtatish',
  'aria.rotateBody':'Tanani aylantirish',
  'title.autoRotate':'Avto-aylantirish',
  'aria.resetViewLayers':'Ko‘rinish va qatlamlarni tiklash',
  'title.reset':'Tiklash',
  'caption.selected':'TANLANGAN TUZILMA',
  'caption.inventory':'ANATOMIK RO‘YXAT',
  'caption.separated':'AJRATILGAN TUZILMALAR',
  'caption.adultMale':'VOYAGA YETGAN INSON · ERKAK',
  'aria.openLayers':'Tizim qatlamlarini ochish',
  'label.explode':'Anatomiyani yoyish',
  'slider.assembled':'Yig‘ilgan',
  'slider.everyPiece':'Har bir bo‘lak',
  'aria.assembleReset':'Yig‘ish va tiklash',
  'footer.pan':'Surish uchun torting',
  'footer.orbit':'Aylantirish uchun torting',
  'footer.zoom':'Kattalashtirish uchun chimchilang',
  'footer.inspect':'Ko‘rish uchun bosing',
  'action.sourceCredits':'Manba va mualliflar',
  'loading.preparing':'Anatomiya tayyorlanmoqda',
  'loading.progress':'{progress}% · {count} ta bo‘lak yuklanmoqda',
  'error.reload':'Ko‘ruvchini qayta yuklash',
  'error.catalogue':'Anatomiya katalogini yuklab bo‘lmadi.',
  'detail.anatomy':'ANATOMIYA',
  'detail.systemOverview':'Tizim sharhi · tuzilma manba anatomiyadan aniqlangan',
  'detail.atlasRef':'Atlas havolasi',
  'detail.selectedPieces':'Tanlangan bo‘laklar',
  'detail.included':'Tarkibiy tuzilmalar',
  'detail.andMore':'Va yana {n} ta modellashtirilgan bo‘lak.',
  'detail.viewSource':'Anatomik manbani ko‘rish',
  'detail.showSurrounding':'Atrofdagi anatomiyani ko‘rsatish',
  'detail.isolate':'Tuzilmani ajratish',
  'detail.clear':'Tanlovni tozalash',
  'about.eyebrow':'MANBA VA QAMROV',
  'about.title':'Ochib berilgan tana.',
  'about.intro':'BodyParts3D’dan voyaga yetgan erkak namunaviy anatomiyasini o‘rganing.',
  'about.male':'Erkak · BodyParts3D',
  'about.meshes':'Voyaga yetgan erkak namunaviy anatomiyasidan 2,234 ta alohida mesh va 3,432 ta nomlangan tushuncha.',
  'about.p2':'Bu namuna har bir inson tuzilmasi yoki o‘zgarishini o‘z ichiga olmaydi. Nomlangan tushunchalar bir nechta bo‘lakdan iborat bo‘lishi mumkin; har bir manba mesh bir marta tasvirlanadi.',
  'about.p3':'Ranglar va tizim guruhlari o‘rganish uchun mo‘ljallangan. Geometriya veb uchun soddalashtirilgan va qisqa izohlar umumiy ta’limiy kontekst beradi. Bu diagnostika yoki jarrohlik vositasi emas, anatomik namunadir.',
  'about.sourceHeading':'Manba',
  'about.license':'BodyParts3D, © The Database Center for Life Science, CC Attribution 4.0 International litsenziyasi ostida.',
  'about.datasetLicense':'Ma’lumotlar to‘plami litsenziyasi',
  'about.geometry':'Asl geometriya va metama’lumotlar',
  'about.publication':'Manba nashrini o‘qish',
  'scene.noWebGL':'Bu brauzer 3D ko‘ruvchini ishga tushira olmadi. WebGL yoqilgan brauzerdan foydalanib ko‘ring.',
  'scene.canvasAria':'Interaktiv inson anatomiyasi. Aylantirish uchun torting, kattalashtirish uchun chimchilang yoki aylantiring, ko‘rish uchun tuzilmaga bosing.',
  'scene.assembleFail':'Anatomiya geometriyasini yig‘ib bo‘lmadi.',
  'scene.loadFail':'Anatomiyani yuklab bo‘lmadi.',
  'scene.paused':'3D sessiyasi qurilmangiz tomonidan to‘xtatildi. Davom etish uchun qayta yuklang.',
 },
};

// Anatomical system names and descriptions. English falls back to anatomy.ts data.
const SYSTEMS_UZ:Record<SystemId,{name:string;description:string}>={
 skeletal:{name:'Skelet',description:'Suyaklar tananing tayanch karkasini hosil qiladi, a‘zolarni himoya qiladi va mushaklar uchun birikish nuqtalarini beradi. Ularning ichki to‘qimasi minerallarni saqlaydi va qon hujayralarini ishlab chiqaradi.'},
 muscular:{name:'Mushaklar',description:'Skelet mushaklari o‘z birikmalarini tortish orqali harakatni yuzaga keltiradi. Paylar bilan birga ular bo‘g‘imlarni harakatlantiradi, tana holatini barqarorlashtiradi va issiqlik hosil qiladi.'},
 cardiac:{name:'Yurak',description:'Yurak — to‘rt kamerali mushakli nasos. Uning klapanlari qonni o‘pka va tizimli qon aylanish doiralari bo‘ylab oldinga yo‘naltiradi.'},
 sensory:{name:'Sezgi a‘zolari',description:'Bu tuzilmalar ko‘rish, eshitish va muvozanat kabi maxsus sezgilarni ta’minlaydi. Ularning ixtisoslashgan to‘qimalari qo‘zg‘atuvchilarni sezadi va asab tizimi bilan birga axborot uzatadi.'},
 arterial:{name:'Arteriyalar',description:'Yurak qonni qon aylanish tizimi bo‘ylab haydaydi. Arteriyalar qonni yurakdan to‘qimalarga yoki o‘pka doirasida o‘pkaga olib boradi.'},
 venous:{name:'Venalar',description:'Venalar qonni yurakka qaytaradi. Yuzaki va chuqur tarmoqlar to‘qimalardan qonni yig‘adi; o‘pka venalari kislorodli qonni o‘pkadan qaytaradi.'},
 nervous:{name:'Asab tizimi',description:'Bosh miya, orqa miya va periferik nervlar signallarni uzatadi va qayta ishlaydi. Ular sezgi, harakat, muvofiqlashtirish va tana funksiyalarini avtomatik boshqarishni ta’minlaydi.'},
 respiratory:{name:'Nafas olish',description:'Nafas yo‘llari havoni o‘pkaga olib boradi, u yerda kislorod va karbonat angidrid havo bilan qon o‘rtasida almashinadi. Nafas olish nafas mushaklari hosil qilgan bosim o‘zgarishlariga bog‘liq.'},
 digestive:{name:'Ovqat hazm qilish',description:'Ovqat hazm qilish yo‘li oziq-ovqatni parchalaydi, oziq moddalar va suvni so‘radi hamda chiqindini oldinga suradi. Yordamchi a‘zolar safro va hazm fermentlarini beradi.'},
 urinary:{name:'Siydik ajratish',description:'Buyraklar qonni filtrlaydi va suyuqlik, elektrolit hamda kislota–ishqor muvozanatini boshqaradi. Siydik siydik naylari orqali qovuqqa boradi va siydik chiqarish kanali orqali tashqariga chiqadi.'},
 lymphatic:{name:'Limfa tizimi',description:'Limfa tomirlari ortiqcha to‘qima suyuqligini qon aylanishiga qaytaradi. Limfa tugunlari va boshqa limfoid a‘zolar immun nazorat va javoblarni qo‘llab-quvvatlaydi.'},
 endocrine:{name:'Endokrin',description:'Endokrin a‘zolar qonga gormonlar chiqarib, moddalar almashinuvi, o‘sish, stress javoblari va ko‘payish kabi jarayonlarni muvofiqlashtiradi.'},
 reproductive:{name:'Ko‘payish',description:'Bu yerda tasvirlangan erkak ko‘payish tuzilmalari sperma ishlab chiqarish, yetilishi, tashilishi va jinsiy gormonlar ishlab chiqarishga hissa qo‘shadi.'},
 integumentary:{name:'Tana yuzasi',description:'Tana yuzasi tashqi anatomik yo‘nalishni beradi. Teri (integumentar) tizimi himoya to‘sig‘ini hosil qiladi hamda sezgi va harorat boshqaruviga hissa qo‘shadi.'},
 connective:{name:'Biriktiruvchi to‘qima',description:'Tog‘ay, boylamlar va boshqa biriktiruvchi to‘qimalar tuzilmalarni qo‘llab-quvvatlaydi, bog‘laydi va ajratib turadi. Ularning vazifasiga bo‘g‘imlarni barqarorlashtirish va mexanik yuklarni taqsimlash kiradi.'},
};

// Dedicated organ explanations, keyed by the lowercase concept name (matching anatomy.ts).
const EXPLANATIONS_UZ:Record<string,string>={
 'heart':'Ko‘krak qafasidagi mushakli nasos. Uning o‘ng tomoni qonni o‘pkaga yuboradi; chap tomoni qonni tizimli qon aylanishi orqali haydaydi.',
 'liver':'Diafragmaning o‘ng tomoni ostidagi yirik a‘zo. U so‘rilgan oziq moddalarni qayta ishlaydi, safro ishlab chiqaradi va qonda tashiladigan ko‘plab oqsillarni sintez qiladi.',
 'brain':'Asab tizimining markaziy a‘zosi. Uning o‘zaro bog‘langan qismlari idrok, harakat, xotira, nutq va tana funksiyalarini boshqarishni ta’minlaydi.',
 'stomach':'Qizilo‘ngach bilan ingichka ichak o‘rtasidagi mushakli bo‘shliq. U oziq-ovqatni saqlaydi va kislota hamda fermentlar bilan aralashtirib, o‘n ikki barmoqli ichakka chiqaradi.',
 'spleen':'Qorinning yuqori chap qismidagi limfoid a‘zo. U qonni filtrlaydi, qarigan qon hujayralarini yo‘qotadi va immun javoblarda ishtirok etadi.',
 'pancreas':'Hazm va endokrin vazifalarga ega qorin a‘zosi. U ingichka ichakka fermentlar yetkazadi hamda insulin va glukagon kabi gormonlarni chiqaradi.',
 'urinary bladder':'Chanoqda joylashgan mushakli rezervuar bo‘lib, buyraklardan siydik naylari orqali kelgan siydikni saqlaydi.',
 'trachea':'Hiqildoqni bronxlar bilan bog‘laydigan asosiy nafas yo‘li. Uning tog‘ay halqalari nafas olishda yo‘lni ochiq tutadi.',
 'diaphragm':'Ko‘krak va qorin bo‘shliqlarini ajratib turuvchi keng mushak. Qisqarganda ko‘krak hajmini oshiradi va havoni o‘pkaga tortishga yordam beradi.',
};

function fill(template:string,vars?:Record<string,string|number>){
 if(!vars)return template;
 return template.replace(/\{(\w+)\}/g,(_,k)=>String(vars[k]??`{${k}}`));
}

export interface I18n{
 lang:Lang;
 setLang:(l:Lang)=>void;
 t:(key:string,vars?:Record<string,string|number>)=>string;
 sys:(id:SystemId)=>{name:string;description:string};
 explain:(name:string,system:SystemId)=>string;
}

const I18nContext=createContext<I18n|null>(null);
const STORAGE_KEY='human-atlas-lang';

function initialLang():Lang{
 if(typeof localStorage==='undefined')return 'en';
 const saved=localStorage.getItem(STORAGE_KEY);
 return saved==='uz'||saved==='en'?saved:'en';
}

export function I18nProvider({children}:{children:ReactNode}){
 const [lang,setLangState]=useState<Lang>(initialLang);
 useEffect(()=>{document.documentElement.lang=lang;},[lang]);
 const value=useMemo<I18n>(()=>({
  lang,
  setLang(l){setLangState(l);try{localStorage.setItem(STORAGE_KEY,l);}catch{/* storage unavailable */}},
  t(key,vars){const table=UI[lang];return fill(table[key]??UI.en[key]??key,vars);},
  sys(id){if(lang==='uz')return SYSTEMS_UZ[id];const s=SYSTEMS.find(x=>x.id===id);return {name:s?.name??id,description:s?.description??''};},
  explain(name,system){const key=name.toLowerCase();if(lang==='uz')return EXPLANATIONS_UZ[key]??SYSTEMS_UZ[system]?.description??'';return EXPLANATIONS[key]??SYSTEMS.find(s=>s.id===system)?.description??'';},
 }),[lang]);
 return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n():I18n{
 const ctx=useContext(I18nContext);
 if(!ctx)throw new Error('useI18n must be used within I18nProvider');
 return ctx;
}
