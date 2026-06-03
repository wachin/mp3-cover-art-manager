# Internationalization (i18n) Guide

This application supports internationalization using Qt Linguist. The following languages are currently available:
- English (en_US)
- Spanish (es_ES)

## Translation Files

- `translations/cover_art_en.ts` - English translation source file
- `translations/cover_art_es.ts` - Spanish translation source file
- `translations/cover_art_en.qm` - Compiled English translation (binary)
- `translations/cover_art_es.qm` - Compiled Spanish translation (binary)

## How to Use Qt Linguist

### Opening a Translation File

1. Open Qt Linguist:
   ```bash
   linguist translations/cover_art_es.ts
   ```

2. Or open it from your system's application menu.

### Editing Translations

1. In Qt Linguist, open the `.ts` file you want to edit (e.g., `cover_art_es.ts`)
2. You will see a list of all translatable strings in the application
3. For each string:
   - The **Source** column shows the original English text
   - The **Translation** column is where you enter the translated text
   - Click on a row to select it
   - Type your translation in the Translation field
   - Press Enter or click the checkmark to mark it as done

### Saving and Compiling

1. Save your changes in Qt Linguist (File → Save)
2. Compile the translation file to create the `.qm` file:
   ```bash
   lrelease translations/cover_art_es.ts
   ```
3. This will generate `translations/cover_art_es.qm` which the application uses at runtime

## Adding a New Language

1. Copy an existing `.ts` file:
   ```bash
   cp translations/cover_art_en.ts translations/cover_art_fr.ts
   ```
2. Edit the new file and change the language attribute in the header:
   ```xml
   <TS version="2.1" language="fr_FR">
   ```
3. Open the file in Qt Linguist and translate all strings
4. Compile the new translation:
   ```bash
   lrelease translations/cover_art_fr.ts
   ```
5. The application will automatically load the translation based on the system locale

## Updating Translations After Code Changes

If you add new translatable strings to the code:

1. Update the `.ts` files:
   ```bash
   pylupdate6 -ts translations/cover_art_en.ts translations/cover_art_es.ts cover_finder.py
   ```
2. Open the updated `.ts` files in Qt Linguist
3. Translate the new strings
4. Recompile:
   ```bash
   lrelease translations/cover_art_en.ts translations/cover_art_es.ts
   ```

## Testing Translations

To test a specific translation without changing your system locale:

1. Set the `LANG` environment variable before running the application:
   ```bash
   LANG=es_ES.UTF-8 python3 cover_finder.py
   ```

2. Or modify the locale in the code temporarily for testing.

## File Structure

```
mp3-cover-art-manager/
├── cover_finder.py          # Main application
├── translations/            # Translation files folder
│   ├── cover_art_en.ts      # English translation source
│   ├── cover_art_es.ts      # Spanish translation source
│   ├── cover_art_en.qm      # Compiled English translation
│   └── cover_art_es.qm      # Compiled Spanish translation
└── TRANSLATIONS.md          # This file
```

## Notes

- The `.ts` files are XML files that contain all translatable strings
- The `.qm` files are compiled binary files that the application loads at runtime
- Always keep the `.ts` files as they are the source for translations
- The application automatically detects the system locale and loads the appropriate translation
- If a translation for the current locale is not found, the application will use the default English strings
- Translation files are organized in the `translations/` folder for better project structure
