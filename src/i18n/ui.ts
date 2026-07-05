export type Lang = 'en' | 'ru' | 'de' | 'es' | 'fr';

export const LANGS: Lang[] = ['en', 'ru', 'de', 'es', 'fr'];

export function getLangFromUrl(url: URL): Lang {
  const [, lang] = url.pathname.split('/');
  if (LANGS.includes(lang as Lang)) return lang as Lang;
  return 'en';
}

export function localePath(lang: Lang, path = ''): string {
  const base = lang === 'en' ? '' : `/${lang}`;
  return `${base}/${path}`.replace(/\/$/, '') || '/';
}

export const ui = {
  en: {
    nav: {
      blog: 'Blog',
      method: 'How it works',
      support: 'Support us',
    },
    hero: {
      nicotine: 'NICOTINE',
      headline: 'Quit. For good.',
      sub: 'A free app with your personal quit plan, body recovery tracking, and support when it gets hard.',
      cta: 'Get NiQuit, free',
    },
    features: {
      title: 'What NiQuit does',
      course: { title: 'Personal quit course', desc: 'A structured programme that works with your habits, not against them.' },
      health: { title: 'Body recovery tracking', desc: 'See exactly what heals and when, calibrated to how long you used nicotine.' },
      coach: { title: 'AI coach, 24/7', desc: 'Text your coach any time. No judgement, no scripts. Just honest support.' },
      savings: { title: 'Money saved', desc: 'Watch what you would have spent add up. Every day counts.' },
    },
    blog: {
      title: 'From the blog',
      readMore: 'Read',
      empty: 'Posts coming soon.',
    },
    articleCta: {
      headline: 'Ready to quit? NiQuit is free.',
      button: 'Download on Google Play',
    },
    donate: {
      title: 'Support NiQuit',
      sub: 'Free for everyone. If NiQuit helped you, you can give back, once, any amount.',
      custom: 'Your amount',
      customPlaceholder: 'e.g. 15',
      customCta: 'Donate',
      currency: 'EUR',
    },
    install: {
      google: 'Get it on Google Play',
      apple: 'Download on the App Store',
    },
    footer: {
      tagline: 'Free nicotine cessation, for everyone.',
      privacy: 'Privacy Policy',
      terms: 'Terms',
      contact: 'Contact',
    },
    privacy: {
      title: 'Privacy Policy',
    },
    terms: {
      title: 'Terms of Use',
    },
    method: {
      title: 'How NiQuit works',
      sub: 'The app is built around one idea: quitting is easier when you understand the trap.',
    },
  },

  ru: {
    nav: {
      blog: 'Блог',
      method: 'Как это работает',
      support: 'Поддержать',
    },
    hero: {
      nicotine: 'НИКОТИН',
      headline: 'Брось. Насовсем.',
      sub: 'Бесплатное приложение с личным планом отказа, трекингом восстановления организма и поддержкой в трудные моменты.',
      cta: 'Скачать NiQuit, бесплатно',
    },
    features: {
      title: 'Что умеет NiQuit',
      course: { title: 'Личный курс отказа', desc: 'Структурированная программа, которая работает с твоими привычками, а не против них.' },
      health: { title: 'Восстановление организма', desc: 'Видишь, что именно восстанавливается и когда, с учётом твоего стажа употребления.' },
      coach: { title: 'ИИ-коуч, 24/7', desc: 'Пиши коучу в любой момент. Без осуждения, без скриптов. Только честная поддержка.' },
      savings: { title: 'Сэкономленные деньги', desc: 'Следи, как копится то, что ты больше не тратишь. Каждый день на счету.' },
    },
    blog: {
      title: 'Из блога',
      readMore: 'Читать',
      empty: 'Статьи скоро появятся.',
    },
    articleCta: {
      headline: 'Готов бросить? NiQuit бесплатный.',
      button: 'Скачать в Google Play',
    },
    donate: {
      title: 'Поддержать NiQuit',
      sub: 'Бесплатно для всех. Если NiQuit тебе помог, можешь поддержать нас. Один раз, любая сумма.',
      custom: 'Своя сумма',
      customPlaceholder: 'напр. 15',
      customCta: 'Поддержать',
      currency: 'EUR',
    },
    install: {
      google: 'Скачать в Google Play',
      apple: 'Скачать в App Store',
    },
    footer: {
      tagline: 'Бесплатный отказ от никотина, для всех.',
      privacy: 'Политика конфиденциальности',
      terms: 'Условия использования',
      contact: 'Связаться',
    },
    privacy: { title: 'Политика конфиденциальности' },
    terms: { title: 'Условия использования' },
    method: {
      title: 'Как работает NiQuit',
      sub: 'Приложение построено вокруг одной идеи: бросить легче, когда понимаешь ловушку.',
    },
  },

  de: {
    nav: {
      blog: 'Blog',
      method: 'So funktioniert\'s',
      support: 'Unterstützen',
    },
    hero: {
      nicotine: 'NIKOTIN',
      headline: 'Weg damit. Für immer.',
      sub: 'Eine kostenlose App mit deinem persönlichen Ausstiegsplan, Körper-Erholungs-Tracking und Unterstützung, wenn es schwer wird.',
      cta: 'NiQuit laden, kostenlos',
    },
    features: {
      title: 'Was NiQuit kann',
      course: { title: 'Persönlicher Ausstiegskurs', desc: 'Ein strukturiertes Programm, das mit deinen Gewohnheiten arbeitet, nicht dagegen.' },
      health: { title: 'Körper-Erholung verfolgen', desc: 'Sieh genau, was sich wann erholt, abgestimmt auf deine Konsumzeit.' },
      coach: { title: 'KI-Coach, 24/7', desc: 'Schreib deinem Coach jederzeit. Kein Urteil, keine Skripte. Nur ehrliche Unterstützung.' },
      savings: { title: 'Erspartes Geld', desc: 'Beobachte, wie das Geld, das du nicht mehr ausgibst, wächst. Jeder Tag zählt.' },
    },
    blog: {
      title: 'Aus dem Blog',
      readMore: 'Lesen',
      empty: 'Beiträge folgen bald.',
    },
    articleCta: {
      headline: 'Bereit aufzuhören? NiQuit ist kostenlos.',
      button: 'Bei Google Play laden',
    },
    donate: {
      title: 'NiQuit unterstützen',
      sub: 'Für alle kostenlos. Wenn NiQuit dir geholfen hat, kannst du etwas zurückgeben, einmalig, beliebiger Betrag.',
      custom: 'Eigener Betrag',
      customPlaceholder: 'z. B. 15',
      customCta: 'Unterstützen',
      currency: 'EUR',
    },
    install: {
      google: 'Bei Google Play laden',
      apple: 'Im App Store laden',
    },
    footer: {
      tagline: 'Kostenloser Nikotinentzug, für alle.',
      privacy: 'Datenschutz',
      terms: 'Nutzungsbedingungen',
      contact: 'Kontakt',
    },
    privacy: { title: 'Datenschutzerklärung' },
    terms: { title: 'Nutzungsbedingungen' },
    method: {
      title: 'So funktioniert NiQuit',
      sub: 'Die App basiert auf einer Idee: Aufhören ist leichter, wenn du die Falle verstehst.',
    },
  },

  es: {
    nav: {
      blog: 'Blog',
      method: 'Cómo funciona',
      support: 'Apoyar',
    },
    hero: {
      nicotine: 'NICOTINA',
      headline: 'Déjalo. Para siempre.',
      sub: 'Una app gratuita con tu plan personal de abandono, seguimiento de la recuperación del cuerpo y apoyo cuando se pone difícil.',
      cta: 'Descargar NiQuit, gratis',
    },
    features: {
      title: 'Qué hace NiQuit',
      course: { title: 'Curso personal de abandono', desc: 'Un programa estructurado que trabaja con tus hábitos, no en su contra.' },
      health: { title: 'Seguimiento de recuperación', desc: 'Ve exactamente qué se recupera y cuándo, ajustado al tiempo que consumiste.' },
      coach: { title: 'Coach con IA, 24/7', desc: 'Escríbele a tu coach cuando quieras. Sin juicios, sin guiones. Solo apoyo honesto.' },
      savings: { title: 'Dinero ahorrado', desc: 'Observa cómo se acumula lo que ya no gastas. Cada día cuenta.' },
    },
    blog: {
      title: 'Del blog',
      readMore: 'Leer',
      empty: 'Artículos próximamente.',
    },
    articleCta: {
      headline: '¿Listo para dejarlo? NiQuit es gratis.',
      button: 'Descargar en Google Play',
    },
    donate: {
      title: 'Apoya NiQuit',
      sub: 'Gratis para todos. Si NiQuit te ayudó, puedes devolver algo, una vez, cualquier cantidad.',
      custom: 'Tu cantidad',
      customPlaceholder: 'ej. 15',
      customCta: 'Donar',
      currency: 'EUR',
    },
    install: {
      google: 'Descargar en Google Play',
      apple: 'Descargar en App Store',
    },
    footer: {
      tagline: 'Abandono del tabaco gratuito, para todos.',
      privacy: 'Política de privacidad',
      terms: 'Condiciones de uso',
      contact: 'Contacto',
    },
    privacy: { title: 'Política de privacidad' },
    terms: { title: 'Condiciones de uso' },
    method: {
      title: 'Cómo funciona NiQuit',
      sub: 'La app se construye alrededor de una idea: dejar es más fácil cuando entiendes la trampa.',
    },
  },

  fr: {
    nav: {
      blog: 'Blog',
      method: 'Comment ça marche',
      support: 'Soutenir',
    },
    hero: {
      nicotine: 'NICOTINE',
      headline: 'Arrête. Pour de bon.',
      sub: "Une app gratuite avec ton plan d'arrêt personnalisé, le suivi de ta récupération et un soutien quand c'est difficile.",
      cta: 'Télécharger NiQuit, gratuit',
    },
    features: {
      title: 'Ce que fait NiQuit',
      course: { title: "Cours d'arrêt personnalisé", desc: 'Un programme structuré qui travaille avec tes habitudes, pas contre elles.' },
      health: { title: 'Suivi de récupération', desc: 'Vois exactement ce qui guérit et quand, ajusté à la durée de ta consommation.' },
      coach: { title: 'Coach IA, 24h/24', desc: "Écris à ton coach quand tu veux. Sans jugement, sans scripts. Juste un soutien honnête." },
      savings: { title: 'Argent économisé', desc: 'Regarde s\'accumuler ce que tu ne dépenses plus. Chaque jour compte.' },
    },
    blog: {
      title: 'Du blog',
      readMore: 'Lire',
      empty: 'Des articles arrivent bientôt.',
    },
    articleCta: {
      headline: "Prêt à arrêter ? NiQuit est gratuit.",
      button: 'Télécharger sur Google Play',
    },
    donate: {
      title: 'Soutenir NiQuit',
      sub: "Gratuit pour tous. Si NiQuit t'a aidé, tu peux donner en retour, une fois, n'importe quel montant.",
      custom: 'Ton montant',
      customPlaceholder: 'ex. 15',
      customCta: 'Donner',
      currency: 'EUR',
    },
    install: {
      google: 'Télécharger sur Google Play',
      apple: "Télécharger sur l'App Store",
    },
    footer: {
      tagline: 'Arrêt du tabac gratuit, pour tous.',
      privacy: 'Politique de confidentialité',
      terms: "Conditions d'utilisation",
      contact: 'Contact',
    },
    privacy: { title: 'Politique de confidentialité' },
    terms: { title: "Conditions d'utilisation" },
    method: {
      title: 'Comment fonctionne NiQuit',
      sub: "L'app repose sur une idée : arrêter est plus facile quand on comprend le piège.",
    },
  },
} as const;

export type UiStrings = typeof ui.en;

export function t(lang: Lang): UiStrings {
  return ui[lang] as unknown as UiStrings;
}
