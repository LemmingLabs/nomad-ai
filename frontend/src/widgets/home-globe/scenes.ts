export interface GlobeScene {
  id: string;
  destinationId: string;
  name: string;
  region: string;
  description: string;
  lat: number;
  lng: number;
  image: string;
  imageAlt: string;
  photographer: string;
  sourceUrl: string;
}

export const globeScenes: GlobeScene[] = [
  {
    id: 'issyk-kul',
    destinationId: 'kg',
    name: 'Issyk-Kul',
    region: 'The lake country',
    description: 'Wide horizons, mountain air, and a slower rhythm beside the water.',
    lat: 42.48,
    lng: 77.18,
    image: '/images/home-globe/issyk-kul.jpg',
    imageAlt: 'Horses grazing beside Issyk-Kul Lake in Kyrgyzstan',
    photographer: 'Apurva Chandwadkar',
    sourceUrl: 'https://www.pexels.com/photo/39762838/',
  },
  {
    id: 'karakol',
    destinationId: 'kg',
    name: 'Karakol',
    region: 'At the foot of the Tian Shan',
    description: 'Snow-lined trails and a gateway to the mountains.',
    lat: 42.49,
    lng: 78.39,
    image: '/images/home-globe/karakol.jpg',
    imageAlt: 'Snow-covered mountain landscape near Karakol, Kyrgyzstan',
    photographer: 'Jesse Blackburn',
    sourceUrl: 'https://www.pexels.com/photo/31833313/',
  },
  {
    id: 'naryn',
    destinationId: 'kg',
    name: 'Naryn',
    region: 'Highland journeys',
    description: 'Open valleys, mountain silhouettes, and a sense of space.',
    lat: 41.43,
    lng: 75.99,
    image: '/images/home-globe/naryn.jpg',
    imageAlt: 'Mountains and highland scenery in the Naryn Region, Kyrgyzstan',
    photographer: 'Erlan Shatmanov',
    sourceUrl: 'https://www.pexels.com/photo/13335981/',
  },
];
