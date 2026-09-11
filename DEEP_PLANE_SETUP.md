# Deep Plane Browlift - Face & Neck Anatomical Explorer

Uma versão customizada do Human Atlas focada em anatomia de **face e pescoço** para estudo aprofundado de procedimentos como:
- Deep Plane Browlift
- Deep Neck Lift
- SMAS Lift
- Facial Nerve Preservation Zones

## 📋 O que foi adicionado

### 1. **face-neck-config.ts**
Arquivo de configuração com:
- **12 regiões anatômicas** organizadas por planos cirúrgicos
- Estruturas críticas para deep plane (SMAS, fáscias, ligamentos retentores)
- Nervos faciais (preservação)
- Vasculatura superficial
- Anatomia cervical
- Presets de câmera para diferentes visualizações
- Presets de procedimentos (surface anatomy, muscle planes, deep plane, etc.)

### 2. **page-face-neck.tsx**
Componente de UI com:
- Novo botão preset **"Deep Plane"** nos layer controls
- Ativa automaticamente: skeletal + muscular + nervous + arterial + venous + connective + sensory
- Pronto para integrar no app/page.tsx

## 🚀 Como implementar

### Passo 1: Integrar o novo preset no app/page.tsx

Localize a linha ~38 onde está `<div className="layer-presets">` e adicione:

```tsx
<Button 
  variant="ghost" 
  title="Deep Plane Browlift: Complete face and neck anatomy"
  aria-pressed={state.visible.length===7&&['skeletal','muscular','nervous','arterial','venous','connective','sensory'].every(id=>state.visible.includes(id as SystemId))} 
  onClick={()=>setState(s=>({...s,selected:[],isolate:false,visible:['skeletal','muscular','nervous','arterial','venous','connective','sensory']}))}
>
  Deep Plane
</Button>
```

### Passo 2: (Opcional) Customize a câmera inicial para face

No arquivo `app/scene.tsx` (linha ~22), modifique a posição da câmera:

```typescript
// Zoom focado na face/pescoço ao invés de corpo inteiro
camera.position.set(0.5, 1.2, 2.0);  
controls.target.set(0, 1.0, 0);
```

### Passo 3: (Opcional) Adicione busca rápida para estruturas deep plane

Importe em `app/page.tsx`:

```typescript
import {DEEP_PLANE_SEARCH_SUGGESTIONS} from './face-neck-config';

// Na função de busca (linha ~24), adicione as sugestões:
const defaultSuggestions = DEEP_PLANE_SEARCH_SUGGESTIONS;
```

### Passo 4: Deploy

```bash
npm run build
npm run dev  # para testar localmente
```

## 🧠 Estruturas Críticas Incluídas

### Para Deep Plane Browlift:
- ✅ Frontalis, Procerus, Corrugator
- ✅ Orbicularis Oculi (pars orbitalis)
- ✅ **SMAS** (Superficial Musculoaponeurotic System)
- ✅ Temporal Fascia (superficial & deep)
- ✅ **Retaining Ligaments** (orbital & zygomatic)
- ✅ Temporal Branch of Facial Nerve CN VII
- ✅ Superficial Temporal Artery/Vein
- ✅ Periosteum

### Para Deep Neck Lift:
- ✅ Platysma
- ✅ Sternocleidomastoid
- ✅ Cervical Fascia (investing, visceral layers)
- ✅ Anterior Cervical Triangle
- ✅ Cervical Plexus branches

## 🔍 Como Usar

1. **Abra o aplicativo** em http://localhost:3016
2. **Clique no botão "Deep Plane"** no painel de layers (canto superior esquerdo)
3. **Use o search** (tecla `/`) para encontrar estruturas específicas:
   - "temporal branch facial nerve"
   - "SMAS"
   - "orbicularis oculi"
   - "zygomatic retaining ligament"
4. **Clique em estruturas** para isolá-las (botão Focus/Isolate)
5. **Use os controles de câmera** para diferentes ângulos

## 📱 Atalhos

| Ação | Como |
|------|------|
| Buscar estrutura | Pressione `/` |
| Rotacionar vista | Drag com mouse |
| Zoom | Scroll / Pinch |
| Isolar estrutura | Clique nela + Focus |
| Ver todos | Clique "All" |
| Voltar ao padrão | Clique "Reset" |

## 🎓 Estruturas por Procedimento

### Surface Anatomy
- Skeleton + Integumentary

### Muscle Planes
- Skeleton + Muscular + Integumentary

### Complete Deep Plane Dissection
- Skeleton + Muscular + Connective + Nervous + Arterial + Venous

### Nerve & Vasculature Preservation
- Nervous + Arterial + Venous + Connective (sem skin para visualizar melhor)

## 📚 Referências Anatômicas

- **BodyParts3D 4.0** - Source geometry (CC BY 4.0)
- **SMAS Anatomy** - Mitz & Peyronie classification
- **Facial Nerve** - Branches and relationships (CN VII)
- **Deep Plane Browlift** - Standard surgical approaches

## 🔧 Próximas Melhorias

- [ ] Criar camadas personalizadas adicionais (e.g., "Nerve Preservation Zones")
- [ ] Adicionar anotações cirúrgicas às estruturas
- [ ] Implementar "waypoints" para sequência de dissecção
- [ ] Exportar views 3D como imagens para apresentações
- [ ] Adicionar animação de dissecção passo a passo

## 📞 Suporte

Para questões sobre a anatomia:
1. Consulte a documentação do BodyParts3D em https://lifesciencedb.jp/bp3d/
2. Verifique os IDs das estruturas no `atlas.json` (public/models/)
3. Use o search do aplicativo para localizar estruturas pelo nome

---

**Versão**: Deep Plane Browlift v1.0  
**Data**: 2025-09-11  
**Base**: Human Atlas 3D (ashemag)
