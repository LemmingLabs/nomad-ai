import { lazy, Suspense, useCallback, useEffect, useState } from 'react';
import { ArrowRight, Compass, Minus, Plus } from 'lucide-react';
import type { Destination } from '../../entities/destination';
import { useMediaQuery } from '../../shared/hooks';
import { GlobeErrorBoundary } from './GlobeErrorBoundary';
import { globeScenes } from './scenes';
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
  destinations: Destination[];
  onPlan: (destinationId: string) => void;
}

export function HomeGlobe({ destinations, onPlan }: HomeGlobeProps) {
  const isMobile = useMediaQuery('(max-width: 768px)');
  const reducedMotion = useMediaQuery('(prefers-reduced-motion: reduce)');
  const [activeIndex, setActiveIndex] = useState(initialSceneIndex);
  const [mobileExplore, setMobileExplore] = useState(false);
  const [desktopReady, setDesktopReady] = useState(false);
  const [globeFailed, setGlobeFailed] = useState(false);
  const [altitude, setAltitude] = useState(2.15);
  const activeScene = globeScenes[activeIndex];
  const canPlan = destinations.some((destination) => destination.enabled && destination.id === activeScene.destinationId);
  const supportsWebGL = Boolean(window.WebGLRenderingContext);
  const show3D = supportsWebGL && !globeFailed && !reducedMotion && (isMobile ? mobileExplore : desktopReady);
  const onFailure = useCallback(() => setGlobeFailed(true), []);

  useEffect(() => {
    if (isMobile || reducedMotion || !supportsWebGL) return undefined;
    if (typeof window.requestIdleCallback === 'function') {
      const id = window.requestIdleCallback(() => setDesktopReady(true), { timeout: 1200 });
      return () => window.cancelIdleCallback(id);
    }
    const id = setTimeout(() => setDesktopReady(true), 250);
    return () => clearTimeout(id);
  }, [isMobile, reducedMotion, supportsWebGL]);

  const selectScene = (id: string) => {
    const nextIndex = globeScenes.findIndex((scene) => scene.id === id);
    if (nextIndex >= 0) setActiveIndex(nextIndex);
  };

  return (
    <section className={styles.experience} aria-label="Explore Kyrgyzstan landscapes">
      <div className={styles.orbit}>
        <div className={styles.orbitHalo} aria-hidden="true" />
        <div className={styles.globe} aria-hidden="true">
          {show3D ? (
            <GlobeErrorBoundary onFailure={onFailure} fallback={<div className={styles.poster} />}>
              <Suspense fallback={<div className={styles.poster} />}>
                <GlobeCanvas
                  scene={activeScene}
                  scenes={globeScenes}
                  altitude={altitude}
                  onSelect={selectScene}
                  onFailure={onFailure}
                />
              </Suspense>
            </GlobeErrorBoundary>
          ) : (
            <div className={styles.poster} />
          )}
        </div>
        <div className={styles.globeCaption}>
          <Compass size={14} />
          <span>Earth, from a new point of view</span>
        </div>
        {show3D && (
          <div className={styles.zoomControls} aria-label="Globe zoom controls">
            <button type="button" onClick={() => setAltitude((current) => Math.min(current + 0.3, 3))} aria-label="Zoom out globe"><Minus size={16} /></button>
            <button type="button" onClick={() => setAltitude((current) => Math.max(current - 0.3, 1.55))} aria-label="Zoom in globe"><Plus size={16} /></button>
          </div>
        )}
        {isMobile && !show3D && supportsWebGL && !reducedMotion && !globeFailed && (
          <button type="button" className={styles.exploreButton} onClick={() => setMobileExplore(true)}>
            Explore 3D globe <ArrowRight size={16} />
          </button>
        )}
      </div>

      <div className={styles.sceneCard}>
        <div className={styles.sceneImageWrap}>
          <img src={activeScene.image} alt={activeScene.imageAlt} className={styles.sceneImage} width="960" height="640" />
          <span className={styles.imageTag}>A place to imagine</span>
        </div>
        <div className={styles.sceneContent}>
          <p className={styles.sceneRegion}>{activeScene.region}</p>
          <h2 className={styles.sceneTitle}>{activeScene.name}</h2>
          <p className={styles.sceneDescription}>{activeScene.description}</p>
          <div className={styles.sceneFooter}>
            {canPlan && (
              <button type="button" className={styles.planButton} onClick={() => onPlan(activeScene.destinationId)}>
                Plan Kyrgyzstan <ArrowRight size={15} />
              </button>
            )}
            <a href={activeScene.sourceUrl} target="_blank" rel="noreferrer" className={styles.credit}>
              Photo: {activeScene.photographer} / Pexels
            </a>
          </div>
        </div>
      </div>

      <div className={styles.scenePicker} role="group" aria-label="Choose a landscape">
        {globeScenes.map((scene, index) => (
          <button
            key={scene.id}
            type="button"
            className={styles.scenePick}
            aria-pressed={index === activeIndex}
            onClick={() => setActiveIndex(index)}
          >
            <span className={styles.scenePickNumber}>0{index + 1}</span>
            {scene.name}
          </button>
        ))}
      </div>
      <a className={styles.earthCredit} href="https://visibleearth.nasa.gov/images/57730/the-blue-marble-land-surface-ocean-color-and-sea-ice" target="_blank" rel="noreferrer">
        Earth imagery: NASA Earth Observatory
      </a>
    </section>
  );
}
