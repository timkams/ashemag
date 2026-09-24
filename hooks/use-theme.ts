import * as React from 'react';

export type ThemePreference = 'system' | 'light' | 'dark';

// Keep in sync with the pre-paint script in web/index.html.
const STORAGE_KEY = 'atlas-theme';
const DARK_QUERY = '(prefers-color-scheme: dark)';

function readPreference(): ThemePreference {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored === 'light' || stored === 'dark' ? stored : 'system';
  } catch {
    return 'system';
  }
}

export function useTheme() {
  const [preference, setPreference] =
    React.useState<ThemePreference>(readPreference);

  React.useEffect(() => {
    const mql = window.matchMedia(DARK_QUERY);
    const apply = () => {
      const root = document.documentElement;
      root.classList.toggle(
        'dark',
        preference === 'dark' || (preference === 'system' && mql.matches),
      );
      document
        .querySelector('meta[name="theme-color"]')
        ?.setAttribute(
          'content',
          getComputedStyle(root).getPropertyValue('--background').trim(),
        );
    };
    apply();
    try {
      if (preference === 'system') localStorage.removeItem(STORAGE_KEY);
      else localStorage.setItem(STORAGE_KEY, preference);
    } catch {}
    mql.addEventListener('change', apply);
    return () => mql.removeEventListener('change', apply);
  }, [preference]);

  return [preference, setPreference] as const;
}
