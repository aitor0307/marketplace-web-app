/**
 * Random anonymous usernames like "SwiftLynx42" / "LinceVeloz42". ASCII only,
 * and always well under RegisterPayload's 30-character name limit.
 */
const WORDS = {
  en: {
    first: [
      'Swift',
      'Quiet',
      'Brave',
      'Lucky',
      'Clever',
      'Sunny',
      'Calm',
      'Bold',
      'Witty',
      'Happy',
    ],
    second: ['Lynx', 'Otter', 'Falcon', 'Fox', 'Badger', 'Heron', 'Ibex', 'Wolf', 'Owl', 'Hare'],
  },
  // Spanish puts the adjective after the noun: "LinceVeloz".
  es: {
    first: [
      'Lince',
      'Nutria',
      'Halcon',
      'Zorro',
      'Tejon',
      'Garza',
      'Lobo',
      'Buho',
      'Liebre',
      'Rebeco',
    ],
    second: [
      'Veloz',
      'Tranquilo',
      'Valiente',
      'Astuto',
      'Alegre',
      'Sereno',
      'Audaz',
      'Agil',
      'Feliz',
      'Curioso',
    ],
  },
} as const;

function pick<T>(items: readonly T[]): T {
  return items[Math.floor(Math.random() * items.length)];
}

export function randomUsername(language: string): string {
  const words = language.startsWith('es') ? WORDS.es : WORDS.en;
  const number = 10 + Math.floor(Math.random() * 90);
  return `${pick(words.first)}${pick(words.second)}${number}`;
}
