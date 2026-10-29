/** Approximate subsolar coordinates from NOAA's fractional-year solar equations. */
export function getSubsolarPoint(date: Date) {
  const year = date.getUTCFullYear();
  const dayOfYear = (Date.UTC(year, date.getUTCMonth(), date.getUTCDate()) - Date.UTC(year, 0, 1)) / 86_400_000 + 1;
  const daysInYear = (Date.UTC(year + 1, 0, 1) - Date.UTC(year, 0, 1)) / 86_400_000;
  const utcMinutes = date.getUTCHours() * 60 + date.getUTCMinutes() + date.getUTCSeconds() / 60;
  const gamma = (2 * Math.PI / daysInYear) * (dayOfYear - 1 + (utcMinutes / 60 - 12) / 24);
  const equationOfTime = 229.18 * (
    0.000075 + 0.001868 * Math.cos(gamma) - 0.032077 * Math.sin(gamma)
    - 0.014615 * Math.cos(2 * gamma) - 0.040849 * Math.sin(2 * gamma)
  );
  const declination = 0.006918 - 0.399912 * Math.cos(gamma) + 0.070257 * Math.sin(gamma)
    - 0.006758 * Math.cos(2 * gamma) + 0.000907 * Math.sin(2 * gamma)
    - 0.002697 * Math.cos(3 * gamma) + 0.00148 * Math.sin(3 * gamma);
  const longitude = (720 - utcMinutes - equationOfTime) / 4;
  return {
    lat: declination * 180 / Math.PI,
    lng: ((longitude + 540) % 360) - 180,
  };
}

export function getSunView(view: { lat: number; lng: number }, sun: { lat: number; lng: number }) {
  const toRadians = Math.PI / 180;
  const viewLat = view.lat * toRadians;
  const sunLat = sun.lat * toRadians;
  const longitudeDelta = (sun.lng - view.lng) * toRadians;
  const facing = Math.sin(viewLat) * Math.sin(sunLat)
    + Math.cos(viewLat) * Math.cos(sunLat) * Math.cos(longitudeDelta);
  const east = Math.cos(sunLat) * Math.sin(longitudeDelta);
  const north = Math.sin(sunLat) * Math.cos(viewLat)
    - Math.cos(sunLat) * Math.sin(viewLat) * Math.cos(longitudeDelta);
  return {
    facing: Math.max(0, facing),
    x: Math.max(10, Math.min(90, 50 + east * 42)),
    y: Math.max(10, Math.min(90, 50 - north * 42)),
  };
}
