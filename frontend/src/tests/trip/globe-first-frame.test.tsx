import { act, cleanup, render } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import GlobeCanvas from '../../widgets/home-globe/GlobeCanvas';
import { globeScenes } from '../../widgets/home-globe/scenes';

const globe = vi.hoisted(() => ({
  pointOfView: vi.fn(),
  renderer: () => ({ setPixelRatio: vi.fn() }),
  controls: () => ({ enableZoom: true, enablePan: true, autoRotate: false, autoRotateSpeed: 0 }),
  getCoords: () => ({ x: 1, y: 2, z: 3 }),
  lights: vi.fn(),
  pauseAnimation: vi.fn(),
  resumeAnimation: vi.fn(),
}));

vi.mock('react-globe.gl', async () => {
  const React = await import('react');
  return {
    default: React.forwardRef(function MockGlobe(props: { onGlobeReady: () => void }, ref) {
      const onReady = React.useRef(props.onGlobeReady);
      React.useImperativeHandle(ref, () => globe);
      React.useEffect(() => { onReady.current(); }, []);
      return <div>Globe renderer</div>;
    }),
  };
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.clearAllMocks();
});

test('reveals the globe only after measuring and setting its initial camera', () => {
  let resize: ResizeObserverCallback | undefined;
  const frames = new Map<number, FrameRequestCallback>();
  let frameId = 0;
  vi.stubGlobal('ResizeObserver', class {
    constructor(callback: ResizeObserverCallback) { resize = callback; }
    observe() {}
    disconnect() {}
  });
  vi.stubGlobal('IntersectionObserver', class {
    observe() {}
    disconnect() {}
  });
  vi.stubGlobal('requestAnimationFrame', (callback: FrameRequestCallback) => {
    frames.set(++frameId, callback);
    return frameId;
  });
  vi.stubGlobal('cancelAnimationFrame', (id: number) => frames.delete(id));

  const scene = globeScenes[0];
  const { container, queryByText } = render(<GlobeCanvas
    scene={scene} scenes={globeScenes} sun={{ lat: 0, lng: 0 }} altitude={1.65}
    exploring={false} onExplore={vi.fn()} onSelect={vi.fn()} onViewChange={vi.fn()} onFailure={vi.fn()}
  />);
  const canvas = container.firstElementChild as HTMLElement;
  expect(canvas.style.opacity).toBe('0');
  expect(queryByText('Globe renderer')).toBeNull();

  act(() => resize?.([{ contentRect: { width: 1000, height: 700 } } as ResizeObserverEntry], {} as ResizeObserver));
  expect(globe.pointOfView).toHaveBeenCalledWith({ lat: scene.lat, lng: scene.lng, altitude: 1.65 }, 0);
  expect(canvas.style.opacity).toBe('0');
  for (let i = 0; i < 2; i++) {
    act(() => {
      const [id, callback] = [...frames.entries()][0];
      frames.delete(id);
      callback(0);
    });
  }
  expect(canvas.style.opacity).toBe('1');
});
