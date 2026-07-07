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
      label: 'Quit nicotine for good',
      prefix: 'Quit',
      suffix: 'for good.',
      sub: 'NiQuit helps you break free from cigarettes, vaping, snus and IQOS, using a method that works with your mind, not against it.',
      cta: 'Get the app, free',
    },
    features: {
      title: 'What NiQuit does',
      course: { title: 'Personal quit course', desc: 'A structured programme that works with your habits, not against them.' },
      health: { title: 'Body recovery tracking', desc: 'See exactly what heals and when, calibrated to how long you used nicotine.' },
      coach: { title: 'AI coach, 24/7', desc: 'Text your coach any time. No judgement, no scripts. Just honest support.' },
      savings: { title: 'Money saved', desc: 'Watch what you would have spent add up. Every day counts.' },
      multiSource: { title: 'Every source, one programme', desc: 'Cigarettes, vaping, pouches or heated tobacco: it is all nicotine. NiQuit treats the addiction, not the delivery method.' },
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
      sub: 'If NiQuit helped you, you can give back: once, any amount.',
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
    consent: {
      text: 'We use anonymous analytics to understand how people use NiQuit. No personal data is collected.',
      accept: 'Accept',
      decline: 'Decline',
    },
    method: {
      title: 'How NiQuit works',
      sub: 'The app is built around one idea: quitting is easier when you understand the trap.',
      trap: {
        heading: 'The nicotine trap',
        body: 'Nicotine does not make you feel good. It removes the discomfort it created in the first place. A non-smoker in the same situation feels no tension at all.',
      },
      why: {
        heading: 'Why willpower alone fails',
        body: 'When you try to quit by force alone, you are fighting a physiological loop your body locked. The craving feels like a genuine need because your brain now registers normal as "with nicotine". That is not a character flaw: it is how the substance works.',
      },
      understanding: {
        heading: 'What changes when you understand it',
        body: 'A craving is a withdrawal symptom, not a real need. It peaks in minutes and passes on its own. Every one you outlast without giving in becomes shorter than the last.',
      },
      what: {
        heading: 'What NiQuit provides',
        body: 'A personal quit course that explains the mechanism before you quit. Health recovery milestones calibrated to your history. An AI coach available any time a craving hits. And savings tracking so you feel progress, not just survive it.',
      },
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
      label: 'Брось никотин навсегда',
      prefix: 'Брось',
      suffix: 'навсегда.',
      sub: 'NiQuit помогает вырваться из зависимости от сигарет, вейпа, снюса и айкоса, с методом, который работает с тобой, а не против тебя.',
      cta: 'Скачать бесплатно',
    },
    features: {
      title: 'Что умеет NiQuit',
      course: { title: 'Личный курс отказа', desc: 'Структурированная программа, которая работает с твоими привычками, а не против них.' },
      health: { title: 'Восстановление организма', desc: 'Видишь, что именно восстанавливается и когда, с учётом твоего стажа употребления.' },
      coach: { title: 'ИИ-коуч, 24/7', desc: 'Пиши коучу в любой момент. Без осуждения, без скриптов. Только честная поддержка.' },
      savings: { title: 'Сэкономленные деньги', desc: 'Следи, как копится то, что ты больше не тратишь. Каждый день на счету.' },
      multiSource: { title: 'Любой источник, одна программа', desc: 'Сигареты, вейп, снюс или айкос: всё это никотин. NiQuit работает с зависимостью, а не с конкретным продуктом.' },
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
      sub: 'Если NiQuit тебе помог, можешь поддержать нас. Один раз, любая сумма.',
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
    consent: {
      text: 'Мы используем анонимную аналитику, чтобы понимать, как люди пользуются NiQuit. Личные данные не собираются.',
      accept: 'Принять',
      decline: 'Отклонить',
    },
    method: {
      title: 'Как работает NiQuit',
      sub: 'Приложение построено вокруг одной идеи: бросить легче, когда понимаешь ловушку.',
      trap: {
        heading: 'Ловушка никотина',
        body: 'Никотин не приносит удовольствия. Он убирает дискомфорт, который сам же и создал. Некурящий в той же ситуации не чувствует никакого напряжения вообще.',
      },
      why: {
        heading: 'Почему воля не работает',
        body: 'Когда бросаешь через силу, борешься с физиологической петлёй, которую тело замкнуло само. Тяга кажется настоящей потребностью, потому что мозг теперь воспринимает норму как "с никотином". Это не слабость характера: так работает это вещество.',
      },
      understanding: {
        heading: 'Что меняет понимание',
        body: 'Тяга - это симптом отмены, а не настоящая потребность. Она достигает пика за несколько минут и спадает сама по себе. Каждая пережитая без сигареты делает следующую короче.',
      },
      what: {
        heading: 'Что даёт NiQuit',
        body: 'Личный курс отказа, который объясняет механизм ещё до того, как бросишь. Показатели восстановления с учётом твоего стажа. Коуч на ИИ, доступный в любой момент тяги. И трекинг сэкономленных денег, чтобы чувствовать прогресс.',
      },
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
      label: 'Nikotin für immer loswerden',
      prefix: 'Weg mit',
      suffix: 'Für immer.',
      sub: 'NiQuit hilft dir, von Zigaretten, Vaping, Snus und IQOS frei zu werden, mit einer Methode, die mit deinem Kopf arbeitet, nicht gegen ihn.',
      cta: 'App laden, kostenlos',
    },
    features: {
      title: 'Was NiQuit kann',
      course: { title: 'Persönlicher Ausstiegskurs', desc: 'Ein strukturiertes Programm, das mit deinen Gewohnheiten arbeitet, nicht dagegen.' },
      health: { title: 'Körper-Erholung verfolgen', desc: 'Sieh genau, was sich wann erholt, abgestimmt auf deine Konsumzeit.' },
      coach: { title: 'KI-Coach, 24/7', desc: 'Schreib deinem Coach jederzeit. Kein Urteil, keine Skripte. Nur ehrliche Unterstützung.' },
      savings: { title: 'Erspartes Geld', desc: 'Beobachte, wie das Geld, das du nicht mehr ausgibst, wächst. Jeder Tag zählt.' },
      multiSource: { title: 'Jede Quelle, ein Programm', desc: 'Zigaretten, Vaping, Pouches oder Tabakerhitzer: alles Nikotin. NiQuit behandelt die Abhängigkeit, nicht das Produkt.' },
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
      sub: 'Wenn NiQuit dir geholfen hat, kannst du etwas zurückgeben: einmalig, beliebiger Betrag.',
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
    consent: {
      text: 'Wir nutzen anonyme Analysen, um zu verstehen, wie NiQuit verwendet wird. Keine persönlichen Daten werden gesammelt.',
      accept: 'Akzeptieren',
      decline: 'Ablehnen',
    },
    method: {
      title: 'So funktioniert NiQuit',
      sub: 'Die App basiert auf einer Idee: Aufhören ist leichter, wenn du die Falle verstehst.',
      trap: {
        heading: 'Die Nikotinfalle',
        body: 'Nikotin macht dich nicht glücklich. Es beseitigt den Entzug, den es selbst verursacht hat. Eine Person, die nie geraucht hat, spürt in derselben Situation überhaupt keine Anspannung.',
      },
      why: {
        heading: 'Warum Willenskraft allein versagt',
        body: 'Wenn du durch reine Kraft aufhörst, kämpfst du gegen eine Schleife, die dein Körper selbst geschlossen hat. Das Verlangen fühlt sich wie ein echter Bedarf an, weil dein Gehirn normal jetzt als "mit Nikotin" definiert. Das ist keine Schwäche: so wirkt diese Substanz.',
      },
      understanding: {
        heading: 'Was das Verstehen verändert',
        body: 'Ein Craving ist ein Entzugssymptom, kein echtes Bedürfnis. Es erreicht seinen Höhepunkt in Minuten und klingt von selbst ab. Jedes, das du ohne Zigarette überwindest, wird kürzer.',
      },
      what: {
        heading: 'Was NiQuit bietet',
        body: 'Einen persönlichen Ausstiegskurs, der den Mechanismus erklärt, bevor du aufhörst. Körper-Erholungsmeilensteine, abgestimmt auf deine Geschichte. Einen KI-Coach, der jederzeit verfügbar ist. Und Ersparnis-Tracking, damit du Fortschritt spürst.',
      },
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
      label: 'Deja la nicotina para siempre',
      prefix: 'Deja la',
      suffix: 'para siempre.',
      sub: 'NiQuit te ayuda a liberarte de los cigarrillos, el vapeo, el snus y los IQOS, con un método que trabaja con tu mente, no en su contra.',
      cta: 'Descargar gratis',
    },
    features: {
      title: 'Qué hace NiQuit',
      course: { title: 'Curso personal de abandono', desc: 'Un programa estructurado que trabaja con tus hábitos, no en su contra.' },
      health: { title: 'Seguimiento de recuperación', desc: 'Ve exactamente qué se recupera y cuándo, ajustado al tiempo que consumiste.' },
      coach: { title: 'Coach con IA, 24/7', desc: 'Escríbele a tu coach cuando quieras. Sin juicios, sin guiones. Solo apoyo honesto.' },
      savings: { title: 'Dinero ahorrado', desc: 'Observa cómo se acumula lo que ya no gastas. Cada día cuenta.' },
      multiSource: { title: 'Cualquier fuente, un programa', desc: 'Cigarrillos, vapeo, bolsitas o tabaco calentado: todo es nicotina. NiQuit trata la dependencia, no el producto.' },
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
      sub: 'Si NiQuit te ayudó, puedes devolver algo: una vez, cualquier cantidad.',
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
    consent: {
      text: 'Usamos análisis anónimos para entender cómo se usa NiQuit. No se recopilan datos personales.',
      accept: 'Aceptar',
      decline: 'Rechazar',
    },
    method: {
      title: 'Cómo funciona NiQuit',
      sub: 'La app se construye alrededor de una idea: dejar es más fácil cuando entiendes la trampa.',
      trap: {
        heading: 'La trampa de la nicotina',
        body: 'La nicotina no te hace sentir bien. Elimina la abstinencia que ella misma creó. Una persona que no fuma en la misma situación no siente absolutamente ninguna tensión.',
      },
      why: {
        heading: 'Por qué la fuerza de voluntad sola no basta',
        body: 'Cuando intentas dejarlo por pura fuerza, luchas contra un ciclo que tu propio cuerpo cerró. El antojo parece una necesidad real porque tu cerebro ahora define normal como "con nicotina". No es debilidad: así funciona esta sustancia.',
      },
      understanding: {
        heading: 'Qué cambia cuando lo entiendes',
        body: 'Un antojo es un síntoma de abstinencia, no una necesidad real. Alcanza su punto máximo en minutos y cede solo. Cada uno que superas sin ceder se vuelve más corto.',
      },
      what: {
        heading: 'Qué ofrece NiQuit',
        body: 'Un curso personal de abandono que explica el mecanismo antes de que dejes. Hitos de recuperación ajustados a tu historial. Un coach con IA disponible cuando llegan los antojos. Y seguimiento de ahorro para que sientas el progreso.',
      },
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
      label: 'Arrête la nicotine pour de bon',
      prefix: 'Arrête la',
      suffix: 'pour de bon.',
      sub: "NiQuit t'aide à te libérer des cigarettes, du vapotage, du snus et des IQOS, avec une méthode qui travaille avec ton esprit, pas contre lui.",
      cta: 'Télécharger gratuitement',
    },
    features: {
      title: 'Ce que fait NiQuit',
      course: { title: "Cours d'arrêt personnalisé", desc: 'Un programme structuré qui travaille avec tes habitudes, pas contre elles.' },
      health: { title: 'Suivi de récupération', desc: 'Vois exactement ce qui guérit et quand, ajusté à la durée de ta consommation.' },
      coach: { title: 'Coach IA, 24h/24', desc: "Écris à ton coach quand tu veux. Sans jugement, sans scripts. Juste un soutien honnête." },
      savings: { title: 'Argent économisé', desc: 'Regarde s\'accumuler ce que tu ne dépenses plus. Chaque jour compte.' },
      multiSource: { title: 'Toutes les sources, un programme', desc: "Cigarettes, vapotage, sachets ou tabac chauffé: tout ça, c'est de la nicotine. NiQuit traite la dépendance, pas le produit." },
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
      sub: "Si NiQuit t'a aidé, tu peux donner en retour: une fois, n'importe quel montant.",
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
    consent: {
      text: "Nous utilisons des analyses anonymes pour comprendre comment NiQuit est utilisé. Aucune donnée personnelle n'est collectée.",
      accept: 'Accepter',
      decline: 'Refuser',
    },
    method: {
      title: 'Comment fonctionne NiQuit',
      sub: "L'app repose sur une idée: arrêter est plus facile quand on comprend le piège.",
      trap: {
        heading: 'Le piège de la nicotine',
        body: "La nicotine ne te fait pas te sentir bien. Elle supprime le sevrage qu'elle a elle-même provoqué. Une personne non-fumeuse dans la même situation ne ressent aucune tension du tout.",
      },
      why: {
        heading: 'Pourquoi la seule force de volonté échoue',
        body: "Quand tu essaies d'arrêter par la seule force, tu te bats contre une boucle que ton corps a fermée lui-même. L'envie semble un besoin réel parce que ton cerveau définit maintenant le normal comme avec nicotine. Ce n'est pas une faiblesse: c'est le fonctionnement de cette substance.",
      },
      understanding: {
        heading: 'Ce qui change quand tu comprends',
        body: "Une envie est un symptôme de sevrage, pas un besoin réel. Elle atteint son pic en quelques minutes et passe d'elle-même. Chacune que tu surmontes sans céder devient plus courte.",
      },
      what: {
        heading: 'Ce que NiQuit apporte',
        body: "Un cours d'arrêt personnalisé qui explique le mécanisme avant que tu arrêtes. Des jalons de récupération ajustés à ton historique. Un coach IA disponible quand les envies arrivent. Et un suivi des économies pour que tu sentes le progrès.",
      },
    },
  },
} as const;

export type UiStrings = typeof ui.en;

export function t(lang: Lang): UiStrings {
  return ui[lang] as unknown as UiStrings;
}
