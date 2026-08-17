# Source verification report: the-first-72-hours-without-nicotine-a-survival-guide
Generated: 2026-08-17

Cross-language mismatches found: 3
- F14: {'de': 'Cyclone Pods', 'fr': 'CDC', 'es': 'Cyclone Pods', 'ru': 'CDC'}
- F9: {'de': 'ScienceInsights', 'ru': 'Global State of Tobacco Harm Reduction'}
- F12: {'de': 'NIH', 'fr': 'NIH PMC', 'ru': 'Global Action to End Smoking'}

Fixed automatically: 10
- [de] "CDC" -> reattributed: Laut NIH-Forschung versuchen die meisten Raucher ungestützt zu rauchen, mit Erfolgsquoten von etwa 7 bis 8 Prozent.
- [de] "ScienceInsights" -> reattributed: Nikotin dockt an diese Rezeptoren an und löst Dopamin aus. Hörst du auf, sind die Rezeptoren trotzdem noch da und verlangen weiter nach ihrer Dosis (Cleveland Clinic).
- [de] "NIH" -> reattributed: Forschende beschreiben es 2025 so: Beim Aufhörversuch aktiviert das Gehirn zusätzliche neuronale Mechanismen.
- [fr] "NIH PMC" -> removed (model response failed validation, treated as no source found)
- [fr] "CDC" -> removed (model response failed validation, treated as no source found)
- [es] "Cyclone Pods" -> reattributed: Según datos del CDC, solo alrededor del 7,5% de las personas que intentan dejarlo cada año lo consiguen sin ningún tipo de apoyo, y la mayoría de los que fallan lo hacen en los primeros días.
- [es] "Snus outlet" -> reattributed: En España, donde alrededor del 23% de los adultos fuma con regularidad según el informe Global State of Tobacco Harm Reduction (2024), y en América Latina, donde la prevalencia bajó del 26% al 15% entre 2000 y 2020 según el informe Global State of Tobacco Harm Reduction (2024), millones de personas ya han cruzado estas mismas 72 horas.
- [ru] "Global State of Tobacco Harm Reduction" -> reattributed: По данным Global State of Tobacco Harm Reduction (2024), в России курят около 27,4 миллиона взрослых, это 23% населения, причём среди мужчин показатель втрое выше, чем среди женщин: 36,1% против 12,1%.
- [ru] "CDC" -> removed
- [ru] "Global Action to End Smoking" -> reattributed: По данным Global State of Tobacco Harm Reduction, в России средства для отказа от курения входят в перечень жизненно важных лекарств, однако государство не покрывает их стоимость, и их приходится покупать самому.

Unresolved: 1
- [de] "Cyclone Pods" (tier 1): could not locate the flagged sentence in the saved file

