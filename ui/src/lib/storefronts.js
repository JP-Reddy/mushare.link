export const storefronts = [
  { id: 'us', name: 'United States' },
  { id: 'au', name: 'Australia' },
  { id: 'at', name: 'Austria' },
  { id: 'be', name: 'Belgium' },
  { id: 'br', name: 'Brazil' },
  { id: 'ca', name: 'Canada' },
  { id: 'cl', name: 'Chile' },
  { id: 'cn', name: 'China mainland' },
  { id: 'co', name: 'Colombia' },
  { id: 'hr', name: 'Croatia' },
  { id: 'cz', name: 'Czech Republic' },
  { id: 'dk', name: 'Denmark' },
  { id: 'fi', name: 'Finland' },
  { id: 'fr', name: 'France' },
  { id: 'de', name: 'Germany' },
  { id: 'gr', name: 'Greece' },
  { id: 'hk', name: 'Hong Kong' },
  { id: 'hu', name: 'Hungary' },
  { id: 'in', name: 'India' },
  { id: 'id', name: 'Indonesia' },
  { id: 'ie', name: 'Ireland' },
  { id: 'il', name: 'Israel' },
  { id: 'it', name: 'Italy' },
  { id: 'jp', name: 'Japan' },
  { id: 'kr', name: 'Korea, Republic of' },
  { id: 'my', name: 'Malaysia' },
  { id: 'mx', name: 'Mexico' },
  { id: 'nl', name: 'Netherlands' },
  { id: 'nz', name: 'New Zealand' },
  { id: 'no', name: 'Norway' },
  { id: 'pl', name: 'Poland' },
  { id: 'pt', name: 'Portugal' },
  { id: 'ru', name: 'Russia' },
  { id: 'sg', name: 'Singapore' },
  { id: 'za', name: 'South Africa' },
  { id: 'es', name: 'Spain' },
  { id: 'se', name: 'Sweden' },
  { id: 'ch', name: 'Switzerland' },
  { id: 'tw', name: 'Taiwan' },
  { id: 'th', name: 'Thailand' },
  { id: 'tr', name: 'Türkiye' },
  { id: 'ae', name: 'UAE' },
  { id: 'gb', name: 'United Kingdom' },
  { id: 'vn', name: 'Vietnam' }
].sort((a, b) => {
  // Keep US at the top, then sort alphabetically
  if (a.id === 'us') return -1;
  if (b.id === 'us') return 1;
  return a.name.localeCompare(b.name);
});

export function getFlagUrl(countryCode) {
  if (countryCode === 'gb') {
    return `https://flagcdn.com/w40/gb.png`;
  }
  if (countryCode === 'xk') {
    return ''; // Kosovo not available on flagcdn
  }
  return `https://flagcdn.com/w40/${countryCode}.png`;
} 