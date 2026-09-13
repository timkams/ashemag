import {fileURLToPath} from 'node:url';
import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/postcss';
const path=(relative:string)=>fileURLToPath(new URL(relative,import.meta.url));
export default defineConfig({root:path('./web'),publicDir:path('./public'),plugins:[react(),{name:'clean-urls',configureServer(server){server.middlewares.use((req,_res,next)=>{if(req.url?.split('?')[0]==='/welcome')req.url=req.url.replace('/welcome','/welcome.html');next();});}}],resolve:{alias:{'@':path('./')}},css:{postcss:{plugins:[tailwindcss()]}},server:{watch:{usePolling:true}},build:{outDir:path('./dist'),emptyOutDir:true,rollupOptions:{input:{main:path('./web/index.html'),welcome:path('./web/welcome.html')}}}});
