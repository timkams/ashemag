/** Knee X-ray proof of concept: upload rules and the analysis boundary. Educational only, not a diagnostic tool. */
export const MAX_XRAYS=2;
export const XRAY_TYPES=['image/png','image/jpeg'] as const;
export const XRAY_ACCEPT=XRAY_TYPES.join(',');
export const MAX_XRAY_BYTES=20*1024*1024;
export interface XrayFileInfo {name:string;type:string;size:number}
const KNEE_API_URL=(import.meta as {env?:{VITE_KNEE_API_URL?:string}}).env?.VITE_KNEE_API_URL??'http://localhost:8000';
export interface KneeXrayResult {
 imageId:string;fileName:string;task:string;grade:number;confidence:number;
 probabilities:{grade0:number;grade1:number;grade2:number;grade3:number;grade4:number};
 tkrRisk:{probability:number;aboveThreshold:boolean};
 model:{name:string;checkpoint:string};
 limitations:string[];
}
export type KneeXrayAnalysis =
 |{status:'ok';results:KneeXrayResult[]}
 |{status:'error';message:string};

/** Returns a message explaining why a file cannot be used, or null when it is acceptable. */
export function checkXrayFile(file:XrayFileInfo):string|null{
 const name=`“${file.name}”`;
 if(/\.dcm$/i.test(file.name)||file.type==='application/dicom')return `${name} is a DICOM file. Export the X-ray as PNG or JPEG and try again.`;
 if(!(XRAY_TYPES as readonly string[]).includes(file.type))return `${name} is not a PNG or JPEG image.`;
 if(file.size===0)return `${name} is empty.`;
 if(file.size>MAX_XRAY_BYTES)return `${name} is larger than ${formatBytes(MAX_XRAY_BYTES)}.`;
 return null;
}

export function formatBytes(bytes:number){return bytes<1024*1024?`${Math.max(1,Math.round(bytes/1024))} KB`:`${(bytes/1024/1024).toFixed(1)} MB`;}

/** Sends each X-ray to the local knee inference service (see service/README.md) and collects structured results. */
export async function analyzeKneeXrays(files:File[],signal?:AbortSignal):Promise<KneeXrayAnalysis>{
 if(!files.length||files.length>MAX_XRAYS)throw new Error(`Select 1 or ${MAX_XRAYS} knee X-rays to analyze.`);
 try{
  const results=await Promise.all(files.map(file=>analyzeOne(file,signal)));
  return {status:'ok',results};
 }catch(e){
  if(e instanceof DOMException&&e.name==='AbortError')throw e;
  return {status:'error',message:e instanceof TypeError?`Could not reach the knee X-ray service at ${KNEE_API_URL}. Make sure it is running (see service/README.md).`:e instanceof Error?e.message:'The X-rays could not be analyzed.'};
 }
}

interface KneeApiResponse {
 imageId:string;
 assessment:{task:string;grade:number;confidence:number};
 probabilities:{grade0:number;grade1:number;grade2:number;grade3:number;grade4:number};
 additionalFindings:{totalKneeReplacementRisk:{probability:number;aboveThreshold:boolean}};
 modelInfo:{name:string;checkpoint:string};
 limitations:string[];
}

async function analyzeOne(file:File,signal?:AbortSignal):Promise<KneeXrayResult>{
 const body=new FormData();body.append('file',file);
 const response=await fetch(`${KNEE_API_URL}/api/knee/analyze`,{method:'POST',body,signal});
 if(!response.ok)throw new Error(`“${file.name}” could not be analyzed (${response.status}).`);
 const data=await response.json() as KneeApiResponse;
 return {
  imageId:data.imageId,fileName:file.name,task:data.assessment.task,
  grade:data.assessment.grade,confidence:data.assessment.confidence,
  probabilities:data.probabilities,
  tkrRisk:data.additionalFindings.totalKneeReplacementRisk,
  model:data.modelInfo,
  limitations:data.limitations,
 };
}
