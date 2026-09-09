import { flushSync } from "react-dom";
import { registerAtlasTools } from "./agent-tools";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  Activity,
  ArrowUpRight,
  ChevronRight,
  Focus,
  Info,
  Layers3,
  Pause,
  RotateCcw,
  RotateCw,
  Search,
  Sparkles,
  Sun,
  Moon,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import {
  Sheet,
  SheetContent,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import {
  Combobox,
  ComboboxInput,
  ComboboxContent,
  ComboboxList,
  ComboboxItem,
  ComboboxEmpty,
} from "@/components/ui/combobox";
import AnatomyScene from "./scene";
import BioChatbot from "@/components/BioChatbot";
import BioPromptDock from "@/components/BioPromptDock";
import { BioChatProvider, useBioChat } from "@/lib/bio-chat-context";
import { ThemeProvider, useTheme } from "@/lib/theme-context";
import {
  DEFAULT_VISIBLE,
  SYSTEMS,
  EXPLANATIONS,
  explanation,
  type Atlas,
  type Concept,
  type SceneState,
  type SystemId,
  type View,
} from "./anatomy";
const initial: SceneState = {
  explode: 0,
  visible: DEFAULT_VISIBLE,
  selected: [],
  isolate: false,
  view: "three-quarter",
  rotate: false,
  reset: 0,
};
function AtlasContent() {
  const { theme, toggleTheme, language, toggleLanguage, t } = useTheme();
  const { isSidebarOpen: about, setIsSidebarOpen: setAbout } = useBioChat();
  const detailTitle = useRef<HTMLHeadingElement>(null);
  const [atlas, setAtlas] = useState<Atlas | null>(null),
    [state, setState] = useState(initial),
    [progress, setProgress] = useState(0),
    [error, setError] = useState(""),
    [panel, setPanel] = useState<"layers" | "search" | null>(null),
    [details, setDetails] = useState(false),
    [query, setQuery] = useState(""),
    [chosen, setChosen] = useState<Concept | null>(null);
  useEffect(() => {
    const abort = new AbortController();
    setProgress(0);
    setError("");
    setAtlas(null);
    setChosen(null);
    setDetails(false);
    setState({ ...initial, visible: DEFAULT_VISIBLE });
    fetch("/models/atlas.json", { signal: abort.signal })
      .then((r) => {
        if (!r.ok)
          throw new Error("The anatomy catalogue could not be loaded.");
        return r.json();
      })
      .then((data) => setAtlas(data as Atlas))
      .catch((e) => {
        if (e.name !== "AbortError") setError(e.message);
      });
    return () => abort.abort();
  }, []);
  useEffect(() => {
    const key = (e: KeyboardEvent) => {
      if (
        e.key === "/" &&
        !(e.target instanceof HTMLInputElement) &&
        !(e.target instanceof HTMLTextAreaElement)
      ) {
        e.preventDefault();
        setPanel("search");
        setDetails(false);
      }
    };
    window.addEventListener("keydown", key);
    return () => window.removeEventListener("keydown", key);
  }, []);
  const parts = useMemo(
    () => new Map(atlas?.parts.map((p) => [p.id, p])),
    [atlas],
  );
  const counts = useMemo(
    () =>
      Object.fromEntries(
        SYSTEMS.map((s) => [
          s.id,
          atlas?.parts.filter((p) => p.system === s.id).length ?? 0,
        ]),
      ),
    [atlas],
  );
  const activeSystems = SYSTEMS.filter((s) => counts[s.id] > 0);
  const selectedParts = state.selected
      .map((id) => parts.get(id))
      .filter((p) => !!p),
    selected = selectedParts[0],
    system = SYSTEMS.find((s) => s.id === selected?.system);
  const visibleCount =
    atlas?.parts.filter((p) =>
      state.isolate
        ? state.selected.includes(p.id)
        : state.visible.includes(p.system) || state.selected.includes(p.id),
    ).length ?? 0;
  const results = useMemo(() => {
    if (!atlas) return [];
    const term = query.toLowerCase().trim();
    if (!term)
      return [
        "heart",
        "brain",
        "liver",
        "stomach",
        "spleen",
        "pancreas",
        "urinary bladder",
        "trachea",
      ]
        .map((name) =>
          atlas.concepts.find((c) => c.name.toLowerCase() === name),
        )
        .filter((x): x is Concept => !!x);
    return atlas.concepts
      .filter(
        (c) =>
          c.name.toLowerCase().includes(term) ||
          c.id.toLowerCase().includes(term),
      )
      .sort((a, b) => a.name.length - b.name.length)
      .slice(0, 80);
  }, [atlas, query]);
  const choose = (c: Concept) => {
    setChosen(c);
    setState((s) => ({
      ...s,
      selected: c.elements,
      isolate: false,
      rotate: false,
    }));
    setDetails(true);
    setPanel(null);
  };
  useEffect(() => {
    if (!atlas) return;
    return registerAtlasTools(atlas, (c) => flushSync(() => choose(c)));
  }, [atlas]);
  const choosePart = (id: string) => {
    const p = parts.get(id);
    if (!p) return;
    setChosen({ id: p.conceptId, name: p.name, elements: [id] });
    setState((s) => ({ ...s, selected: [id], isolate: false, rotate: false }));
    setDetails(true);
    setPanel(null);
  };
  const toggle = (id: SystemId) => {
    setDetails(false);
    setState((s) => ({
      ...s,
      selected: [],
      isolate: false,
      visible: s.visible.includes(id)
        ? s.visible.filter((x) => x !== id)
        : [...s.visible, id],
    }));
  };
  const reset = () => {
    setState((s) => ({
      ...initial,
      visible: DEFAULT_VISIBLE,
      reset: s.reset + 1,
    }));
    setChosen(null);
    setDetails(false);
    setPanel(null);
  };
  const openPanel = (next: "layers" | "search") => {
    setDetails(false);
    setPanel((p) => (p === next ? null : next));
  };
  return (
    <main className={`studio ${theme === 'dark' ? 'dark' : ''}`}>
      {atlas && (
        <AnatomyScene
          atlas={atlas}
          state={{
            ...state,
            theme,
            inspectorOpen: details && selectedParts.length > 0,
          }}
          onSelect={choosePart}
          onProgress={(n) => {
            setProgress(n);
            if (n === 100) setError("");
          }}
          onError={setError}
        />
      )}
      <div className="vignette" />
      <header className="identity">
        <div className="eyebrow">
          <span className="status-dot" /> {t.brandEyebrow}
        </div>
        <h1>
          Human Atlas
          <Badge variant="outline" className="edition">
            {t.edition}
          </Badge>
        </h1>
        <div className="identity-meta">
          {atlas ? atlas.parts.length.toLocaleString() : "2,234"} {t.modeledPieces}{" "}
          <span>·</span> {t.bodyParts3d}
        </div>
      </header>{" "}
      <nav className="top-actions" aria-label="Explorer panels">
        <Button
          variant="ghost"
          className={panel === "search" ? "active" : ""}
          onClick={() => openPanel("search")}
          aria-label={t.findStructure}
        >
          <Search size={18} />
          <span>{t.findStructure}</span>
          <kbd>/</kbd>
        </Button>
        <Button
          variant="ghost"
          className={`bio-tutor-trigger ${about ? "active" : ""}`}
          aria-label={t.bioAiTutor}
          onClick={() => {
            setDetails(false);
            setPanel(null);
            setAbout(true);
          }}
        >
          <Sparkles size={17} style={{ color: "#458a85" }} />
          <span>{t.bioAiTutor}</span>
        </Button>
      </nav>
      <section
        className={`layers-panel glass ${panel === "layers" ? "mobile-open" : ""}`}
        aria-label="Anatomical layers"
      >
        <div className="panel-heading">
          <span>{t.systems}</span>
          <Button
            variant="ghost"
            className="mobile-only icon-button"
            onClick={() => setPanel(null)}
            aria-label={t.closeSystems}
          >
            <X size={18} />
          </Button>
          <Badge variant="secondary" className="desktop-only small-number">
            {activeSystems.length}
          </Badge>
        </div>
        <div className="layer-presets">
          <Button
            variant="ghost"
            aria-pressed={activeSystems.every((x) =>
              state.visible.includes(x.id),
            )}
            onClick={() =>
              setState((s) => ({
                ...s,
                selected: [],
                isolate: false,
                visible: activeSystems.map((x) => x.id),
              }))
            }
          >
            {t.all}
          </Button>
          <Button
            variant="ghost"
            aria-pressed={
              state.visible.length === 1 && state.visible[0] === "skeletal"
            }
            onClick={() =>
              setState((s) => ({
                ...s,
                selected: [],
                isolate: false,
                visible: ["skeletal"],
              }))
            }
          >
            {t.skeleton}
          </Button>
          <Button
            variant="ghost"
            aria-pressed={
              state.visible.length === 6 &&
              [
                "cardiac",
                "respiratory",
                "digestive",
                "urinary",
                "endocrine",
                "reproductive",
              ].every((id) => state.visible.includes(id as SystemId))
            }
            onClick={() =>
              setState((s) => ({
                ...s,
                selected: [],
                isolate: false,
                visible: [
                  "cardiac",
                  "respiratory",
                  "digestive",
                  "urinary",
                  "endocrine",
                  "reproductive",
                ],
              }))
            }
          >
            {t.organs}
          </Button>
        </div>
        <div className="system-list">
          {activeSystems.map((s) => (
            <div
              className={`system-row ${state.visible.includes(s.id) ? "enabled" : ""}`}
              key={s.id}
            >
              <Button
                variant="ghost"
                className="system-name"
                title={`Show only ${(t.systemNames[s.id] ?? s.name).toLowerCase()}`}
                onClick={() =>
                  setState((v) => ({
                    ...v,
                    visible: [s.id],
                    isolate: false,
                    selected: [],
                  }))
                }
              >
                <span className="system-dot" style={{ background: s.color }} />
                {t.systemNames[s.id] ?? s.name}
                <span className="system-count">{counts[s.id]}</span>
              </Button>
              <Switch
                checked={state.visible.includes(s.id)}
                onCheckedChange={() => toggle(s.id)}
                aria-label={`Show ${(t.systemNames[s.id] ?? s.name).toLowerCase()}`}
              />
            </div>
          ))}
        </div>
        <div className="panel-foot">
          <span>
            {visibleCount.toLocaleString()} {t.piecesVisible}
          </span>
          <Button
            variant="ghost"
            onClick={() =>
              setState((s) => ({
                ...s,
                visible: [],
                selected: [],
                isolate: false,
              }))
            }
          >
            {t.hideAll}
          </Button>
        </div>
      </section>
      {panel === "search" && (
        <section className="search-panel glass" aria-label="Find anatomy">
          <div className="panel-heading">
            <span>{t.findStructure}</span>
            <Button
              variant="ghost"
              className="icon-button"
              onClick={() => setPanel(null)}
              aria-label={t.closeSearch}
            >
              <X size={18} />
            </Button>
          </div>
          <Combobox<Concept>
            items={results}
            value={null}
            onValueChange={(value) => {
              if (value) choose(value);
            }}
            inputValue={query}
            onInputValueChange={setQuery}
            itemToStringLabel={(c) => c.name}
            filter={null}
            open
            onOpenChange={(open) => {
              if (!open) setPanel(null);
            }}
          >
            <ComboboxInput
              autoFocus
              placeholder={t.searchPlaceholder}
              aria-label="Search named anatomical structures"
              showTrigger={false}
            />
            <ComboboxContent className="anatomy-search-results">
              <ComboboxEmpty>{t.noStructuresMatch}</ComboboxEmpty>
              <ComboboxList>
                {(c: Concept) => (
                  <ComboboxItem key={c.id} value={c}>
                    <span className="search-result-name">{c.name}</span>
                    <span className="small-number">
                      {c.elements.length}{" "}
                      {c.elements.length === 1 ? t.piece : t.pieces}
                    </span>
                  </ComboboxItem>
                )}
              </ComboboxList>
            </ComboboxContent>
          </Combobox>
          <p className="search-note">
            {query ? t.searchNoteActive : t.searchNoteEmpty}
          </p>
        </section>
      )}
      <nav className="view-controls glass" aria-label="Controls">
        {(['three-quarter', 'front', 'side', 'back'] as View[]).map((v, i) => (
          <Button
            key={v}
            variant="ghost"
            className={state.view === v ? 'active' : ''}
            onClick={() => setState(s => ({ ...s, view: v, reset: s.reset + 1, rotate: false }))}
            title={v === 'three-quarter' ? t.threeQuarterView : v === 'front' ? t.frontView : v === 'side' ? t.sideView : t.backView}
            aria-label={v === 'three-quarter' ? t.threeQuarterView : v === 'front' ? t.frontView : v === 'side' ? t.sideView : t.backView}
          >
            <span>{['¾', 'F', 'S', 'B'][i]}</span>
          </Button>
        ))}
        <i />
        <Button
          variant="ghost"
          aria-label={state.rotate ? t.pauseRotation : t.autoRotate}
          title={state.rotate ? t.pauseRotation : t.autoRotate}
          className={state.rotate ? 'active' : ''}
          onClick={() => setState(s => ({ ...s, rotate: !s.rotate }))}
        >
          {state.rotate ? <Pause size={17} /> : <RotateCw size={18} />}
        </Button>
        <Button
          variant="ghost"
          aria-label={t.resetView}
          title={t.resetView}
          onClick={reset}
        >
          <RotateCcw size={17} />
        </Button>
        <i />
        <Button
          variant="ghost"
          className={`theme-toggle-btn ${theme === 'dark' ? 'is-dark' : ''}`}
          aria-label={t.darkMode}
          title={t.darkMode}
          onClick={toggleTheme}
        >
          {theme === 'dark' ? <Sun size={17} className="text-amber-400" /> : <Moon size={17} />}
        </Button>
        <Button
          variant="ghost"
          className="lang-toggle-btn"
          aria-label={t.languageToggle}
          title={t.languageToggle}
          onClick={toggleLanguage}
        >
          <span style={{ fontSize: '11px', fontWeight: 700, letterSpacing: '0.02em' }}>
            {language === 'en' ? 'हिं' : 'EN'}
          </span>
        </Button>
      </nav>
      <div className="scene-caption">
        <span className="caption-line" />
        <span>
          {state.isolate
            ? (chosen?.name ?? t.selectedStructure)
            : state.explode > 0.95
              ? t.anatomicalInventory
              : state.explode > 0.05
                ? t.separatedStructures
                : t.adultHumanMale}
        </span>
        <span className="caption-line" />
      </div>
      <div className="bottom-dock glass has-prompt-dock">
        <BioPromptDock selectedStructureName={chosen?.name} />
      </div>
      <footer className="studio-footer">
        <span>
          {state.explode > 0.8 ? t.dragToPan : t.dragToOrbit} <b>·</b> {t.pinchToZoom}{" "}
          <b>·</b> {t.tapToInspect}
        </span>
        <Button
          variant="ghost"
          onClick={() => {
            setDetails(false);
            setPanel(null);
            setAbout(true);
          }}
        >
          <Sparkles size={13} style={{ color: "#458a85" }} />
          <span>{t.bioAiAndScope}</span> <ArrowUpRight size={12} />
        </Button>
      </footer>
      {progress < 100 && !error && (
        <div className="loading glass" role="status">
          <Activity size={18} />
          <div>
            <strong>{t.preparingAnatomy}</strong>
            <span>
              {progress}% · {t.loadingPieces}{" "}
              {atlas?.parts.length.toLocaleString() ?? "2,234"}{" "}
              {t.pieces}
            </span>
            <div className="loading-track">
              <i style={{ width: `${progress}%` }} />
            </div>
          </div>
        </div>
      )}
      {error && (
        <div className="loading glass error" role="alert">
          <p>{error}</p>
          <Button variant="ghost" onClick={() => location.reload()}>
            {t.reloadViewer}
          </Button>
        </div>
      )}
      <Sheet
        open={details && selectedParts.length > 0}
        modal={false}
        disablePointerDismissal
        onOpenChange={setDetails}
      >
        <SheetContent
          initialFocus={detailTitle}
          className={`detail-sheet glass ${state.isolate ? "is-isolated" : ""}`}
          showCloseButton={true}
        >
          <div className="detail-header">
            <div
              className="detail-accent"
              style={{ background: system?.color }}
            />
            <div className="eyebrow">
              {system ? (t.systemNames[system.id] ?? system.name) : t.anatomyHeader}
            </div>
            <SheetTitle
              ref={detailTitle}
              tabIndex={-1}
              className="structure-title"
            >
              {chosen?.name}
            </SheetTitle>
          </div>
          <div className="detail-scroll" key={`${chosen?.id}-${state.isolate}`}>
            <SheetDescription className="structure-description">
              {chosen && selected
                ? explanation(chosen.name, selected.system)
                : ""}
            </SheetDescription>
            {chosen && !EXPLANATIONS[chosen.name.toLowerCase()] && (
              <span className="context-note">
                {t.systemOverview}
              </span>
            )}
            <div className="structure-meta">
              <span>
                {t.atlasReference}<strong>{chosen?.id}</strong>
              </span>
              <span>
                {t.selectedPieces}
                <strong>{state.selected.length.toLocaleString()}</strong>
              </span>
            </div>
            {selectedParts.length > 1 && (
              <div className="member-list">
                <h3>{t.includedStructures}</h3>
                {selectedParts.slice(0, 50).map((p) => (
                  <Button
                    variant="ghost"
                    key={p.id}
                    onClick={() => choosePart(p.id)}
                  >
                    <span>{p.name}</span>
                    <ChevronRight size={14} />
                  </Button>
                ))}
                {selectedParts.length > 50 && (
                  <p>{t.andMorePieces}</p>
                )}
              </div>
            )}
            <a
              className="source-link"
              href="https://lifesciencedb.jp/bp3d/"
              target="_blank"
              rel="noreferrer"
            >
              {t.viewAnatomicalSource} <ArrowUpRight size={14} />
            </a>
          </div>
          <div className="detail-actions">
            <Button
              className={`primary-action ${state.isolate ? "active" : ""}`}
              onClick={() =>
                setState((s) => ({ ...s, isolate: !s.isolate, explode: 0 }))
              }
            >
              <Focus size={18} />
              {state.isolate ? t.showSurrounding : t.isolateStructure}
              <ChevronRight size={16} />
            </Button>
            <Button
              variant="ghost"
              className="secondary-action"
              onClick={() => {
                setState((s) => ({ ...s, selected: [], isolate: false }));
                setDetails(false);
              }}
            >
              {t.clearSelection}
            </Button>
          </div>
        </SheetContent>
      </Sheet>
      <Sheet open={about} onOpenChange={setAbout}>
        <SheetContent
          className="about-sheet glass"
          style={{ width: "min(500px, 100vw)", maxWidth: "500px" }}
        >
          <BioChatbot selectedStructureName={chosen?.name} />
        </SheetContent>
      </Sheet>
    </main>
  );
}

export default function Home() {
  return (
    <ThemeProvider>
      <BioChatProvider>
        <AtlasContent />
      </BioChatProvider>
    </ThemeProvider>
  );
}

