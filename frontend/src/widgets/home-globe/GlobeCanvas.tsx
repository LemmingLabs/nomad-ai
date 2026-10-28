import { useEffect, useRef, useState } from 'react';
import Globe, { type GlobeMethods } from 'react-globe.gl';
import type { GlobeScene } from './scenes';

interface GlobeCanvasProps {
  scene: GlobeScene;
  scenes: GlobeScene[];
  altitude: number;
  onSelect: (id: string) => void;
  onFailure: () => void;
}

export default function GlobeCanvas({ scene, scenes, altitude, onSelect, onFailure }: GlobeCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const globeRef = useRef<GlobeMethods | undefined>(undefined);
  const inViewRef = useRef(true);
  const [size, setSize] = useState({ width: 520, height: 520 });
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return undefined;
    const observer = new ResizeObserver(([entry]) => {
      const width = Math.round(entry.contentRect.width);
      if (width > 0) setSize({ width, height: Math.min(width, 650) });
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
    globeRef.current?.pointOfView({ lat: scene.lat, lng: scene.lng, altitude }, 850);
  }, [scene, altitude, ready]);

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
        atmosphereColor="#4fd6d4"
        atmosphereAltitude={0.18}
        pointsData={scenes}
        pointLat="lat"
        pointLng="lng"
        pointColor={(point) => (point as GlobeScene).id === scene.id ? '#ffffff' : '#5eead4'}
        pointAltitude={0.02}
        pointRadius={0.58}
        pointLabel={(point) => (point as GlobeScene).name}
        pointsTransitionDuration={0}
        onPointClick={(point) => onSelect((point as GlobeScene).id)}
        onGlobeReady={() => {
          const instance = globeRef.current;
          if (!instance) return;
          instance.renderer().setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
          const controls = instance.controls();
          controls.enableZoom = false;
          controls.enablePan = false;
          controls.autoRotate = true;
          controls.autoRotateSpeed = 0.32;
          instance.pointOfView({ lat: scene.lat, lng: scene.lng, altitude }, 0);
          if (document.hidden || !inViewRef.current) instance.pauseAnimation();
          setReady(true);
        }}
      />
    </div>
  );
}
