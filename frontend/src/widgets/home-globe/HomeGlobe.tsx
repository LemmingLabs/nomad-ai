import { lazy, Suspense, useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';
import { ArrowLeft, ArrowRight, Compass, Minus, Plus, Sun } from 'lucide-react';
import type { Destination } from '../../entities/destination';
import { useMediaQuery } from '../../shared/hooks';
import { GlobeErrorBoundary } from './GlobeErrorBoundary';
import { globeScenes } from './scenes';
import { getSubsolarPoint, getSunView } from './solar';
import styles from './HomeGlobe.module.scss';

const GlobeCanvas = lazy(() => import('./GlobeCanvas'));

function initialSceneIndex() {
  let previous = -1;
  try {
    const saved = sessionStorage.getItem('nomad-home-scene');
    if (saved !== null) previous = Number(saved);
  } catch {
    // The scene still works when storage is disabled.
  }
  const offset = Math.floor(Math.random() * globeScenes.length);
  const next = offset === previous ? (offset + 1) % globeScenes.length : offset;
  try {
    sessionStorage.setItem('nomad-home-scene', String(next));
  } catch {
    // Keep the random scene for this visit.
  }
  return next;
}

interface HomeGlobeProps {
  children: ReactNode;
  destinations: Destination[];
  onPlan: (destinationId: string) => void;
}

export function HomeGlobe({ children, destinations, onPlan }: HomeGlobeProps) {
  const isMobile = useMediaQuery('(max-width: 768px)');
  const reducedMotion = useMediaQuery('(prefers-reduced-motion: reduce)');
  const [activeIndex, setActiveIndex] = useState(initialSceneIndex);
  const [exploring, setExploring] = useState(false);
  const [mobileExplore, setMobileExplore] = useState(false);
  const [desktopReady, setDesktopReady] = useState(false);
  const [globeFailed, setGlobeFailed] = useState(false);
  const [altitude, setAltitude] = useState(1.65);
  const [now, setNow] = useState(() => new Date());
  const activeScene = globeScenes[activeIndex];
  const [view, setView] = useState({ lat: activeScene.lat, lng: activeScene.lng });
  const sun = useMemo(() => getSubsolarPoint(now), [now]);
  const canPlan = destinations.some((destination) => destination.enabled && destination.id === activeScene.destinationId);
  const supportsWebGL = Boolean(window.WebGLRenderingContext);
  const show3D = supportsWebGL && !globeFailed && !reducedMotion && (isMobile ? mobileExplore : desktopReady);
  const sunlight = getSunView(show3D ? view : activeScene, sun);
  const onFailure = useCallback(() => setGlobeFailed(true), []);
  const onExplore = useCallback(() => setExploring(true), []);
  const onViewChange = useCallback((nextView: { lat: number; lng: number }) => setView(nextView), []);
  const selectScene = useCallback((id: string) => {
    const nextIndex = globeScenes.findIndex((scene) => scene.id === id);
    if (nextIndex >= 0) {
      setActiveIndex(nextIndex);
      setExploring(true);
    }
  }, []);

  useEffect(() => {
    if (isMobile || reducedMotion || !supportsWebGL) return undefined;
    if (typeof window.requestIdleCallback === 'function') {
      const id = window.requestIdleCallback(() => setDesktopReady(true), { timeout: 1200 });
      return () => window.cancelIdleCallback(id);
    }
    const id = setTimeout(() => setDesktopReady(true), 250);
    return () => clearTimeout(id);
  }, [isMobile, reducedMotion, supportsWebGL]);

  useEffect(() => {
    const id = window.setInterval(() => setNow(new Date()), 60_000);
    return () => window.clearInterval(id);
  }, []);

  useEffect(() => {
    if (exploring || reducedMotion) return undefined;
    const id = window.setInterval(() => setActiveIndex((index) => (index + 1) % globeScenes.length), 7_000);
    return () => window.clearInterval(id);
  }, [exploring, reducedMotion]);

  return (
    <section className={styles.experience} data-exploring={exploring} aria-label="Explore Kyrgyzstan landscapes">
      <div className={styles.sky} aria-hidden="true" />
      <div className={styles.sunWash} style={{ opacity: 0.08 + sunlight.facing * 0.7 }} aria-hidden="true" />
      <div
        className={styles.sunHalo}
        style={{ left: `${sunlight.x}%`, top: `${sunlight.y}%`, opacity: 0.22 + sunlight.facing * 0.65 }}
        aria-hidden="true"
      />
      <div className={styles.stars} aria-hidden="true" />

      <div className={styles.globe} aria-hidden="true" data-testid="globe-backdrop" onPointerDown={onExplore}>
        {show3D ? (
          <GlobeErrorBoundary onFailure={onFailure} fallback={<div className={styles.poster} />}>
            <Suspense fallback={<div className={styles.poster} />}>
              <GlobeCanvas
                scene={activeScene}
                scenes={globeScenes}
                sun={sun}
                altitude={altitude}
                exploring={exploring}
                onExplore={onExplore}
                onSelect={selectScene}
                onViewChange={onViewChange}
                onFailure={onFailure}
              />
            </Suspense>
          </GlobeErrorBoundary>
        ) : (
          <div className={styles.poster} />
        )}
      </div>

      <div className={styles.topLine}>
        <span className={styles.eyebrow}><Compass size={15} /> NOMADAI / EARTH</span>
        <span className={styles.sunLabel}><Sun size={15} /> Sunlight follows the current UTC time</span>
      </div>

      <div className={styles.intro} inert={exploring} aria-hidden={exploring}>
        <div className={styles.introContent}>{children}</div>
        <button type="button" className={styles.exploreButton} onClick={onExplore}>
          Explore the globe <ArrowRight size={17} />
        </button>
      </div>

      <div className={styles.exploreBar} inert={!exploring} aria-hidden={!exploring}>
        <button type="button" className={styles.backButton} onClick={() => setExploring(false)}>
          <ArrowLeft size={16} /> Back to start
        </button>
        <span>Drag Earth or choose a landscape below</span>
        <div className={styles.exploreControls}>
          {isMobile && !show3D && supportsWebGL && !reducedMotion && !globeFailed && (
            <button type="button" onClick={() => setMobileExplore(true)}>Enable 3D</button>
          )}
          {show3D && (
            <div className={styles.zoomControls} role="group" aria-label="Globe zoom controls">
              <button type="button" onClick={() => setAltitude((value) => Math.min(value + 0.25, 3))} aria-label="Zoom out globe"><Minus size={16} /></button>
              <button type="button" onClick={() => setAltitude((value) => Math.max(value - 0.25, 1.15))} aria-label="Zoom in globe"><Plus size={16} /></button>
            </div>
          )}
        </div>
      </div>

      <div className={styles.sceneDock} inert={!exploring} aria-hidden={!exploring}>
        <article className={styles.activeScene}>
          <img src={activeScene.image} alt={activeScene.imageAlt} width="960" height="640" />
          <div className={styles.activeSceneContent}>
            <span className={styles.sceneKicker}>{activeScene.region}</span>
            <h2>{activeScene.name}</h2>
            <p>{activeScene.description}</p>
            <div className={styles.activeSceneFooter}>
              {canPlan && (
                <button type="button" onClick={() => onPlan(activeScene.destinationId)}>
                  Plan Kyrgyzstan <ArrowRight size={15} />
                </button>
              )}
              <a href={activeScene.sourceUrl} target="_blank" rel="noreferrer">
                Photo: {activeScene.photographer} / Pexels
              </a>
            </div>
          </div>
        </article>
        <div className={styles.scenePicker} role="group" aria-label="Choose a landscape">
          {globeScenes.map((scene, index) => (
            <button
              key={scene.id}
              type="button"
              className={styles.scenePick}
              aria-pressed={index === activeIndex}
              onClick={() => selectScene(scene.id)}
            >
              <img src={scene.image} alt="" width="960" height="640" />
              <span><small>0{index + 1} / KYRGYZSTAN</small>{scene.name}</span>
            </button>
          ))}
        </div>
      </div>
      <a className={styles.earthCredit} href="https://visibleearth.nasa.gov/images/57730/the-blue-marble-land-surface-ocean-color-and-sea-ice" target="_blank" rel="noreferrer">
        Earth imagery: NASA Earth Observatory
      </a>
    </section>
  );
}
