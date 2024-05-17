import pandas as pd

df_initial = pd.read_csv('sounds.csv')

df = df_initial.drop('LanguageName', axis=1).drop_duplicates()  # датафрейм для дальнейшей работы

n_langs = len(df_initial.LanguageName.unique())  # количество уникальных языков

df_langs = df_initial.groupby([
    'Phoneme', 'SegmentClass', 'stress', 'syllabic',
    'short', 'long', 'consonantal', 'sonorant', 'continuant',
    'delayedRelease', 'approximant', 'tap', 'trill', 'nasal', 'lateral',
    'labial', 'round', 'labiodental', 'coronal', 'anterior', 'distributed',
    'strident', 'dorsal', 'high', 'low', 'front', 'back', 'tense',
    'retractedTongueRoot', 'advancedTongueRoot', 'periodicGlottalSource',
    'epilaryngealSource', 'spreadGlottis', 'constrictedGlottis', 'fortis',
    'lenis', 'raisedLarynxEjective', 'loweredLarynxImplosive', 'click'])['LanguageName'].agg(set).reset_index()  # группируем и делаем сет языков для каждого сегмента

df_langs['Representation'] = df_langs['LanguageName'].apply(lambda x: len(x) / n_langs)  # делаем новый столбец в который записываем результат деления длины сета на количества языков
df_langs = df_langs.drop('LanguageName', axis=1)
df_langs.to_csv('bebe.csv', sep='\t', index=False, header=True)