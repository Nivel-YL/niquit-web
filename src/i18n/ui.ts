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

// build.format:'file' makes Astro.url.pathname reflect the actual output
// filename (e.g. /method.html, or literally /index.html for the root), but
// every internal link (localePath()) points to the clean, extensionless URL
// Cloudflare actually serves it at. Normalize any Astro.url.pathname to that
// clean form - used for canonical/og:url and anywhere else a "which page am
// I on" path is needed.
export function canonicalPath(url: URL): string {
  let path = url.pathname
    .replace(/(^|\/)index\.html$/, '$1')
    .replace(/\.html$/, '');
  if (path.length > 1) path = path.replace(/\/$/, '');
  return path === '' ? '/' : path;
}

// localePath() expects a bare path with no leading slash and no locale
// prefix (it adds both itself). Strips the locale prefix from an already-
// clean path (see canonicalPath()) down to that bare form.
export function stripLocalePrefix(path: string): string {
  return path.replace(/^\/(ru|de|es|fr)(\/|$)/, '/').replace(/^\//, '');
}

export const ui = {
  en: {
    nav: {
      home: 'Home',
      blog: 'Blog',
      method: 'How it works',
      support: 'Support us',
    },
    calc: {
      entry: "See what you'll save",
      phoneCta: 'Calculate your savings',
      tapHere: 'Tap the phone',
      cardTitle: "Curious what you'd save?",
      cardBody: 'Run your numbers in 15 seconds.',
      cardCta: 'Open calculator',
      methodCta: 'See what quitting would save you',
      postPrompt: 'Curious what quitting would save you?',
      postCta: 'Open the savings calculator',
      pill: 'Savings calculator',
      title: 'See what nicotine really costs you',
      sub: "Enter your habit below. We'll show what you've already spent, and what you'd save by quitting, factoring in the way tobacco prices climb every year.",
      perDay: 'How much per day',
      perDayHint: 'cigarettes / pouches / puffs a day',
      perPack: 'Units per pack or tin',
      perPackHint: 'e.g. 20 cigarettes, 20 pouches',
      packPrice: 'Price per pack today',
      packPriceHint: 'EU average is around 6 EUR',
      startYear: 'When you started',
      startYearHint: 'the year you began using nicotine',
      spentLabel: "What you've likely spent since",
      projTitle: "If you quit today, you'd save",
      year: 'year',
      yearsFew: 'years',
      years: 'years',
      close: 'Close calculator',
      footnote: 'Figures use an average EU pack price and assume tobacco prices keep rising about 4% a year, the pace seen across the EU in recent years, driven mainly by annual excise-duty increases. Real prices vary widely by country (roughly 4 to 13 EUR a pack) and by product, so treat these as a realistic estimate, not an exact forecast.',
    },
    calcPage: {
      metaTitle: 'Nicotine savings calculator',
      metaDescription: "See what cigarettes, vaping or pouches have already cost you, and how much you would save by quitting, adjusted for the way tobacco prices rise each year.",
      h1: 'Nicotine savings calculator',
      intro: 'See what your habit has already cost you and how much quitting would save. Works for cigarettes, vaping and nicotine pouches.',
      howTitle: 'How this is calculated',
      howBody: "The calculator turns your daily use into packs per year and values them at today's price. Past spending discounts that price backwards year by year; future savings project it forward. Both use a 4% annual rise, the average pace of tobacco price increases across the EU in recent years, driven mainly by excise duty. Real prices vary by country and product, so the result is a realistic estimate, not an exact figure.",
      ctaTitle: 'Ready to stop spending on nicotine?',
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
      invite: "If NiQuit helped you, I'd be grateful for any amount, anytime.",
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
    article: {
      feedbackPrompt: 'Was this helpful?',
      readNext: 'Read next',
    },
    support: {
      accent: 'Freedom from nicotine. Free, for everyone.',
      body: "NiQuit isn't backed by any fund or investor. Every cost of building and running it comes straight from the founder's own pocket. And since one of the best parts of getting free is the money you stop spending, I'd be grateful if a little of those savings found its way back, as a thank you. That's what keeps NiQuit free for everyone.",
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
      home: 'Главная',
      blog: 'Блог',
      method: 'Как это работает',
      support: 'Поддержать',
    },
    calc: {
      entry: 'Посчитай свою экономию',
      phoneCta: 'Посчитать экономию',
      tapHere: 'Нажми на телефон',
      cardTitle: 'Интересно, сколько сэкономишь?',
      cardBody: 'Прикинь свои цифры за 15 секунд.',
      cardCta: 'Открыть калькулятор',
      methodCta: 'Посмотри, сколько сэкономит отказ',
      postPrompt: 'Интересно, сколько сэкономит отказ?',
      postCta: 'Открыть калькулятор экономии',
      pill: 'Калькулятор экономии',
      title: 'Посмотри, во сколько на самом деле обходится никотин',
      sub: 'Укажи свою привычку ниже. Мы покажем, сколько ты уже потратил и сколько сэкономишь, если бросишь, с учётом того, как цены на табак растут каждый год.',
      perDay: 'Сколько в день',
      perDayHint: 'сигарет / паучей / затяжек в день',
      perPack: 'Штук в пачке или банке',
      perPackHint: 'напр. 20 сигарет, 20 паучей',
      packPrice: 'Цена пачки сегодня',
      packPriceHint: 'в среднем по ЕС около 6 EUR',
      startYear: 'Когда начал',
      startYearHint: 'год, когда ты начал употреблять никотин',
      spentLabel: 'Ты, скорее всего, потратил с',
      projTitle: 'Если бросишь сегодня, сэкономишь',
      year: 'год',
      yearsFew: 'года',
      years: 'лет',
      close: 'Закрыть калькулятор',
      footnote: 'Расчёты используют среднюю цену пачки по ЕС и предполагают, что цены на табак растут примерно на 4% в год, как это происходило в ЕС в последние годы, в основном из-за ежегодного повышения акцизов. Реальные цены сильно различаются по странам (примерно от 4 до 13 EUR за пачку) и по продуктам, так что считай это реалистичной оценкой, а не точным прогнозом.',
    },
    calcPage: {
      metaTitle: 'Калькулятор экономии на никотине',
      metaDescription: 'Посмотри, во сколько уже обошлись сигареты, вейп или паучи и сколько ты сэкономишь, если бросишь, с учётом ежегодного роста цен на табак.',
      h1: 'Калькулятор экономии на никотине',
      intro: 'Посмотри, во сколько уже обошлась твоя привычка и сколько сэкономит отказ. Работает для сигарет, вейпа и никотиновых паучей.',
      howTitle: 'Как это считается',
      howBody: 'Калькулятор переводит твоё дневное потребление в пачки за год и оценивает их по сегодняшней цене. Прошлые траты дисконтируются назад по годам, будущая экономия проецируется вперёд. И то и другое с ростом 4% в год, средний темп повышения цен на табак в ЕС за последние годы, в основном из-за акцизов. Реальные цены различаются по странам и продуктам, так что это реалистичная оценка, а не точная цифра.',
      ctaTitle: 'Готов перестать тратить на никотин?',
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
      invite: 'Если NiQuit помог тебе, буду благодарен за любую сумму, в любое время.',
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
    article: {
      feedbackPrompt: 'Было ли это полезно?',
      readNext: 'Читать дальше',
    },
    support: {
      accent: 'Свобода от никотина. Бесплатно и для каждого.',
      body: 'NiQuit не поддерживается фондами или инвесторами. Все расходы на разработку и поддержание проекта автор берёт на себя лично. А раз одним из главных бонусов свободы от никотина становятся освободившиеся деньги, буду благодарен, если часть этой экономии вернётся в проект как знак благодарности. Именно так NiQuit остаётся бесплатным для всех.',
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
      home: 'Start',
      blog: 'Blog',
      method: 'So funktioniert\'s',
      support: 'Unterstützen',
    },
    calc: {
      entry: 'Sieh, was du sparst',
      phoneCta: 'Ersparnis berechnen',
      tapHere: 'Tippe aufs Handy',
      cardTitle: 'Neugierig, was du sparst?',
      cardBody: 'Rechne deine Zahlen in 15 Sekunden aus.',
      cardCta: 'Rechner öffnen',
      methodCta: 'Sieh, was dir das Aufhören spart',
      postPrompt: 'Neugierig, was dir das Aufhören spart?',
      postCta: 'Ersparnis-Rechner öffnen',
      pill: 'Ersparnis-Rechner',
      title: 'Sieh, was Nikotin dich wirklich kostet',
      sub: 'Gib unten deine Gewohnheit ein. Wir zeigen dir, was du bereits ausgegeben hast und was du mit dem Aufhören sparen würdest, unter Berücksichtigung dessen, wie die Tabakpreise jedes Jahr steigen.',
      perDay: 'Wie viel pro Tag',
      perDayHint: 'Zigaretten / Pouches / Züge pro Tag',
      perPack: 'Stück pro Packung oder Dose',
      perPackHint: 'z. B. 20 Zigaretten, 20 Pouches',
      packPrice: 'Preis pro Packung heute',
      packPriceHint: 'EU-Durchschnitt liegt bei etwa 6 EUR',
      startYear: 'Wann du angefangen hast',
      startYearHint: 'das Jahr, in dem du mit Nikotin begonnen hast',
      spentLabel: 'Du hast wahrscheinlich ausgegeben seit',
      projTitle: 'Wenn du heute aufhörst, sparst du',
      year: 'Jahr',
      yearsFew: 'Jahre',
      years: 'Jahre',
      close: 'Rechner schließen',
      footnote: 'Die Zahlen verwenden einen durchschnittlichen EU-Packungspreis und nehmen an, dass die Tabakpreise um etwa 4% pro Jahr steigen, so wie in den letzten Jahren in der EU, hauptsächlich getrieben durch jährliche Erhöhungen der Verbrauchsteuer. Die realen Preise unterscheiden sich stark je nach Land (etwa 4 bis 13 EUR pro Packung) und Produkt, betrachte dies also als realistische Schätzung, nicht als exakte Prognose.',
    },
    calcPage: {
      metaTitle: 'Nikotin-Ersparnis-Rechner',
      metaDescription: 'Sieh, was Zigaretten, Vaping oder Pouches dich schon gekostet haben und wie viel du mit dem Aufhören sparst, angepasst an die jährlich steigenden Tabakpreise.',
      h1: 'Nikotin-Ersparnis-Rechner',
      intro: 'Sieh, was dich deine Gewohnheit schon gekostet hat und wie viel das Aufhören spart. Für Zigaretten, Vaping und Nikotinbeutel.',
      howTitle: 'So wird gerechnet',
      howBody: 'Der Rechner setzt deinen täglichen Konsum in Packungen pro Jahr um und bewertet sie zum heutigen Preis. Vergangene Ausgaben werden Jahr für Jahr zurück abgezinst, künftige Ersparnisse nach vorn projiziert. Beides mit 4% Anstieg pro Jahr, dem durchschnittlichen Tempo der Tabakpreissteigerung in der EU der letzten Jahre, vor allem durch die Verbrauchsteuer. Reale Preise unterscheiden sich je nach Land und Produkt, das Ergebnis ist also eine realistische Schätzung, keine exakte Zahl.',
      ctaTitle: 'Bereit, kein Geld mehr für Nikotin auszugeben?',
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
      invite: 'Wenn NiQuit dir geholfen hat, bin ich für jeden Betrag dankbar, jederzeit.',
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
    article: {
      feedbackPrompt: 'War das hilfreich?',
      readNext: 'Weiter lesen',
    },
    support: {
      accent: 'Freiheit von Nikotin. Kostenlos, für alle.',
      body: 'NiQuit wird von keinem Fonds und keinem Investor unterstützt. Sämtliche Kosten für Entwicklung und Betrieb trägt der Gründer selbst. Und da einer der größten Vorteile beim Freiwerden das gesparte Geld ist, wäre ich dankbar, wenn ein kleiner Teil davon als Dankeschön zurück ins Projekt fließt. Genau so bleibt NiQuit für alle kostenlos.',
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
      home: 'Inicio',
      blog: 'Blog',
      method: 'Cómo funciona',
      support: 'Apoyar',
    },
    calc: {
      entry: 'Mira cuánto ahorrarás',
      phoneCta: 'Calcular tu ahorro',
      tapHere: 'Toca el teléfono',
      cardTitle: '¿Curiosidad por cuánto ahorrarías?',
      cardBody: 'Calcula tus números en 15 segundos.',
      cardCta: 'Abrir calculadora',
      methodCta: 'Mira cuánto te ahorraría dejarlo',
      postPrompt: '¿Curiosidad por cuánto te ahorraría dejarlo?',
      postCta: 'Abrir la calculadora de ahorro',
      pill: 'Calculadora de ahorro',
      title: 'Mira cuánto te cuesta de verdad la nicotina',
      sub: 'Introduce tu hábito abajo. Te mostramos lo que ya has gastado y lo que ahorrarías si lo dejas, teniendo en cuenta cómo suben los precios del tabaco cada año.',
      perDay: 'Cuánto al día',
      perDayHint: 'cigarrillos / bolsitas / caladas al día',
      perPack: 'Unidades por paquete o lata',
      perPackHint: 'ej. 20 cigarrillos, 20 bolsitas',
      packPrice: 'Precio del paquete hoy',
      packPriceHint: 'la media de la UE ronda los 6 EUR',
      startYear: 'Cuándo empezaste',
      startYearHint: 'el año en que empezaste a consumir nicotina',
      spentLabel: 'Probablemente has gastado desde',
      projTitle: 'Si lo dejas hoy, ahorrarías',
      year: 'año',
      yearsFew: 'años',
      years: 'años',
      close: 'Cerrar calculadora',
      footnote: 'Las cifras usan un precio medio de paquete de la UE y asumen que los precios del tabaco siguen subiendo alrededor de un 4% al año, el ritmo visto en la UE en los últimos años, impulsado sobre todo por las subidas anuales de impuestos especiales. Los precios reales varían mucho según el país (aproximadamente de 4 a 13 EUR por paquete) y el producto, así que tómalo como una estimación realista, no como una previsión exacta.',
    },
    calcPage: {
      metaTitle: 'Calculadora de ahorro al dejar la nicotina',
      metaDescription: 'Mira lo que ya te han costado los cigarrillos, el vapeo o las bolsitas y cuánto ahorrarías al dejarlo, ajustado a la subida anual del precio del tabaco.',
      h1: 'Calculadora de ahorro al dejar la nicotina',
      intro: 'Mira lo que ya te ha costado tu hábito y cuánto te ahorraría dejarlo. Sirve para cigarrillos, vapeo y bolsitas de nicotina.',
      howTitle: 'Cómo se calcula',
      howBody: 'La calculadora convierte tu consumo diario en paquetes al año y los valora al precio de hoy. El gasto pasado se descuenta hacia atrás año a año y el ahorro futuro se proyecta hacia adelante. Ambos con una subida del 4% anual, el ritmo medio del alza del precio del tabaco en la UE en los últimos años, impulsado sobre todo por los impuestos especiales. Los precios reales varían según el país y el producto, así que es una estimación realista, no una cifra exacta.',
      ctaTitle: '¿Listo para dejar de gastar en nicotina?',
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
      invite: 'Si NiQuit te ayudó, te agradecería cualquier cantidad, en cualquier momento.',
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
    article: {
      feedbackPrompt: '¿Fue de ayuda?',
      readNext: 'Leer más',
    },
    support: {
      accent: 'Libertad frente a la nicotina. Gratis, para todos.',
      body: 'NiQuit no cuenta con el respaldo de ningún fondo ni inversor. Todos los gastos de crear y mantener el proyecto corren por cuenta del propio fundador. Y como una de las mejores partes de dejarlo es el dinero que dejas de gastar, te agradecería muchísimo que una parte de ese ahorro volviera al proyecto, como forma de decir gracias. Así es como NiQuit sigue siendo gratis para todos.',
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
      home: 'Accueil',
      blog: 'Blog',
      method: 'Comment ça marche',
      support: 'Soutenir',
    },
    calc: {
      entry: 'Vois ce que tu économises',
      phoneCta: 'Calcule tes économies',
      tapHere: 'Appuie sur le téléphone',
      cardTitle: 'Curieux de savoir ce que tu économiserais ?',
      cardBody: 'Calcule tes chiffres en 15 secondes.',
      cardCta: 'Ouvrir le calculateur',
      methodCta: 'Vois ce que ton arrêt te ferait économiser',
      postPrompt: 'Curieux de savoir ce que ton arrêt te ferait économiser ?',
      postCta: "Ouvrir le calculateur d'économies",
      pill: "Calculateur d'économies",
      title: 'Vois ce que la nicotine te coûte vraiment',
      sub: "Renseigne ton habitude ci-dessous. On te montre ce que tu as déjà dépensé et ce que tu économiserais en arrêtant, en tenant compte de la hausse des prix du tabac chaque année.",
      perDay: 'Combien par jour',
      perDayHint: 'cigarettes / sachets / bouffées par jour',
      perPack: 'Unités par paquet ou boîte',
      perPackHint: 'ex. 20 cigarettes, 20 sachets',
      packPrice: 'Prix du paquet aujourd\'hui',
      packPriceHint: "la moyenne UE tourne autour de 6 EUR",
      startYear: 'Quand tu as commencé',
      startYearHint: "l'année où tu as commencé la nicotine",
      spentLabel: 'Tu as probablement dépensé depuis',
      projTitle: "Si tu arrêtes aujourd'hui, tu économiserais",
      year: 'an',
      yearsFew: 'ans',
      years: 'ans',
      close: 'Fermer le calculateur',
      footnote: "Les chiffres utilisent un prix de paquet moyen dans l'UE et supposent que les prix du tabac continuent d'augmenter d'environ 4% par an, le rythme observé dans l'UE ces dernières années, porté surtout par les hausses annuelles des droits d'accise. Les prix réels varient beaucoup selon le pays (environ 4 à 13 EUR le paquet) et le produit, considère donc ceci comme une estimation réaliste, pas une prévision exacte.",
    },
    calcPage: {
      metaTitle: "Calculateur d'économies sur la nicotine",
      metaDescription: "Vois ce que les cigarettes, le vapotage ou les sachets t'ont déjà coûté et combien tu économiserais en arrêtant, ajusté à la hausse annuelle du prix du tabac.",
      h1: "Calculateur d'économies sur la nicotine",
      intro: "Vois ce que ton habitude t'a déjà coûté et combien ton arrêt ferait économiser. Pour les cigarettes, le vapotage et les sachets de nicotine.",
      howTitle: 'Comment le calcul fonctionne',
      howBody: "Le calculateur convertit ta consommation quotidienne en paquets par an et les valorise au prix d'aujourd'hui. Les dépenses passées sont actualisées en arrière année par année, les économies futures projetées en avant. Les deux avec une hausse de 4% par an, le rythme moyen d'augmentation du prix du tabac dans l'UE ces dernières années, porté surtout par les droits d'accise. Les prix réels varient selon le pays et le produit, c'est donc une estimation réaliste, pas un chiffre exact.",
      ctaTitle: 'Prêt à arrêter de dépenser pour la nicotine ?',
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
      invite: "Si NiQuit t'a aidé, je serais reconnaissant pour n'importe quel montant, à tout moment.",
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
    article: {
      feedbackPrompt: 'Cela vous a-t-il aidé ?',
      readNext: 'Lire la suite',
    },
    support: {
      accent: 'La liberté face à la nicotine. Gratuite, pour tous.',
      body: "NiQuit n'est soutenu par aucun fonds ni investisseur. Tous les frais de développement et de fonctionnement sont pris en charge par le fondateur lui-même. Et puisque l'un des grands bénéfices de la liberté retrouvée, c'est justement l'argent que tu ne dépenses plus, je te serais reconnaissant qu'une petite part de cette économie revienne au projet, en guise de merci. C'est ainsi que NiQuit reste gratuit pour tous.",
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
