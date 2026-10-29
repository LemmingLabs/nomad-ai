import { useEffect, useRef, useState } from 'react';
import { AmbientLight, DirectionalLight } from 'three';
import Globe, { type GlobeMethods } from 'react-globe.gl';
import type { GlobeScene } from './scenes';

interface Coordinates { lat: number; lng: number }

interface GlobeCanvasProps {
  scene: GlobeScene;
  scenes: GlobeScene[];
  sun: Coordinates;
  altitude: number;
  exploring: boolean;
  onExplore: () => void;
  onSelect: (id: string) => void;
  onViewChange: (view: Coordinates) => void;
  onFailure: () => void;
}

export default function GlobeCanvas({
  scene, scenes, sun, altitude, exploring, onExplore, onSelect, onViewChange, onFailure,
}: GlobeCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const globeRef = useRef<GlobeMethods | undefined>(undefined);
  const sunLightRef = useRef<DirectionalLight | null>(null);
  const inViewRef = useRef(true);
  const lastViewReportRef = useRef(0);
  const lastFocusRef = useRef({ sceneId: scene.id, altitude });
  const [size, setSize] = useState({ width: 1200, height: 800 });
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return undefined;
    const observer = new ResizeObserver(([entry]) => {
      const width = Math.round(entry.contentRect.width);
      const height = Math.round(entry.contentRect.height);
      if (width > 0 && height > 0) setSize({ width, height });
    });
    observer.observe(container);
    const handleContextLoss = (event: Event) => {
      event.preventDefault();
      onFailure();
    };
    container.addEventListener('webglcontextlost', handleContextLoss);
    return () => {
      observer.disconnect();
      container.removeEventListener('webglcontextlost', handleContextLoss);
    };
  }, [onFailure]);

  useEffect(() => {
    if (!ready) return;
    if (lastFocusRef.current.sceneId === scene.id && lastFocusRef.current.altitude === altitude) return;
    lastFocusRef.current = { sceneId: scene.id, altitude };
    globeRef.current?.pointOfView({ lat: scene.lat, lng: scene.lng, altitude }, exploring ? 850 : 2200);
  }, [scene, altitude, exploring, ready]);

  useEffect(() => {
    if (!ready || !sunLightRef.current) return;
    const position = globeRef.current?.getCoords(sun.lat, sun.lng, 5);
    if (position) sunLightRef.current.position.set(position.x, position.y, position.z);
  }, [sun, ready]);

  useEffect(() => {
    if (!ready) return;
    const controls = globeRef.current?.controls();
    if (controls) controls.autoRotate = !exploring;
  }, [exploring, ready]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return undefined;
    const updateAnimation = () => {
      if (document.hidden || !inViewRef.current) globeRef.current?.pauseAnimation();
      else globeRef.current?.resumeAnimation();
    };
    const observer = new IntersectionObserver(([entry]) => {
      inViewRef.current = entry.isIntersecting;
      updateAnimation();
    });
    observer.observe(container);
    document.addEventListener('visibilitychange', updateAnimation);
    return () => {
      observer.disconnect();
      document.removeEventListener('visibilitychange', updateAnimation);
    };
  }, []);

  return (
    <div
      ref={containerRef}
      style={{ width: '100%', height: '100%' }}
      onPointerDown={() => {
        onExplore();
        const controls = globeRef.current?.controls();
        if (controls) controls.autoRotate = false;
        globeRef.current?.resumeAnimation();
      }}
    >
      <Globe
        ref={globeRef}
        width={size.width}
        height={size.height}
        backgroundColor="rgba(0,0,0,0)"
        globeImageUrl="/images/home-globe/earth-blue-marble.jpg"
        showAtmosphere
        atmosphereColor="#a8ddf6"
        atmosphereAltitude={0.17}
        pointsData={scenes}
        pointLat="lat"
        pointLng="lng"
        pointColor={(point) => (point as GlobeScene).id === scene.id ? '#ffe5a2' : '#ffffff'}
        pointAltitude={0.025}
        pointRadius={0.66}
        pointLabel={(point) => (point as GlobeScene).name}
        pointsTransitionDuration={0}
        onPointClick={(point) => onSelect((point as GlobeScene).id)}
        onZoom={(view) => {
          const now = performance.now();
          if (now - lastViewReportRef.current > 90) {
            lastViewReportRef.current = now;
            onViewChange({ lat: view.lat, lng: view.lng });
          }
        }}
        onGlobeReady={() => {
          const instance = globeRef.current;
          if (!instance) return;
          instance.renderer().setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
          const controls = instance.controls();
          controls.enableZoom = false;
          controls.enablePan = false;
          controls.autoRotate = !exploring;
          controls.autoRotateSpeed = 0.2;
          const sunlight = new DirectionalLight('#fff1ce', 2.15);
          const position = instance.getCoords(sun.lat, sun.lng, 5);
          sunlight.position.set(position.x, position.y, position.z);
          sunLightRef.current = sunlight;
          instance.lights([new AmbientLight('#c4dcf1', 0.48), sunlight]);
          instance.pointOfView({ lat: scene.lat, lng: scene.lng, altitude }, 0);
          if (document.hidden || !inViewRef.current) instance.pauseAnimation();
          setReady(true);
        }}
      />
    </div>
  );
}
