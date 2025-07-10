<script>
  import { API_ENDPOINTS } from '$lib/config.js';
  import { storefronts, getFlagUrl } from '$lib/storefronts.js';
  
  let url = '';
  let loading = false;
  let error = '';
  let result = null;
  let copied = null;
  let selectedStorefront = 'us';
  let showCountryDropdown = false;

  async function handleCopyToClipboard(text, type) {
    try {
      await navigator.clipboard.writeText(text);
      copied = type;
      setTimeout(() => (copied = null), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  }

  function isValidUrl(string) {
    try {
      const url = new URL(string);
      return url.protocol === 'http:' || url.protocol === 'https:';
    } catch {
      return false;
    }
  }
  
  async function handleSubmit() {
    loading = true;
    error = '';
    result = null;

    if (!isValidUrl(url)) {
      error = 'Hmmm, invalid URL provided';
      loading = false;
      return;
    }

    try {
      const response = await fetch(API_ENDPOINTS.convert, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          source_url: url,
          storefront: selectedStorefront
        }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'An unknown error occurred');
      }

      result = await response.json();
    } catch (err) {
      if (err instanceof SyntaxError && err.message.includes('JSON')) {
        error = 'Network error - please check your connection and try again';
      } else if (err.message) {
        error = err.message;
      } else {
        error = 'An unexpected error occurred';
      }
    } finally {
      loading = false;
    }
  }

  function getPlatform(link) {
    return link.includes('spotify.com') ? 'Spotify' : 'Apple Music';
  }

  function selectCountry(countryId) {
    selectedStorefront = countryId;
    showCountryDropdown = false;
  }

  function toggleCountryDropdown() {
    showCountryDropdown = !showCountryDropdown;
  }

  function handleClickOutside(event) {
    if (!event.target.closest('.country-selector')) {
      showCountryDropdown = false;
    }
  }

  $: sourcePlatform = result ? getPlatform(result.source_url) : '';
  $: convertedPlatform = result ? (sourcePlatform === 'Spotify' ? 'Apple Music' : 'Spotify') : '';
</script>

<svelte:head>
  <title>MuShare</title>
</svelte:head>

<svelte:window on:click={handleClickOutside} />

<div class="container">
  <header>
    <h1>| MuShare |</h1>
    <p>Convert links between Spotify and Apple Music in a snap</p>
  </header>

  <main>
    <form on:submit|preventDefault={handleSubmit}>
      <div class="input-row">
        <input
          type="url"
          bind:value={url}
          placeholder="Paste Spotify or Apple Music link..."
          required
          class="url-input"
        />
        
        <div class="country-selector">
          <button 
            type="button"
            class="country-button"
            on:click={toggleCountryDropdown}
          >
            <img src={getFlagUrl(selectedStorefront)} alt="" class="flag-image" />
            <svg class="dropdown-arrow" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>
          
          {#if showCountryDropdown}
            <div class="country-dropdown">
              {#each storefronts as country}
                <button
                  type="button"
                  class="country-option"
                  class:selected={country.id === selectedStorefront}
                  on:click={() => selectCountry(country.id)}
                >
                  <img src={getFlagUrl(country.id)} alt="" class="flag-image" />
                  <span class="country-name">{country.name}</span>
                  <span class="country-code-small">{country.id.toUpperCase()}</span>
                </button>
              {/each}
            </div>
          {/if}
        </div>
        
        <div class="help-tooltip">
          <div class="info-icon">?</div>
          <div class="tooltip-content">
            Apple Music links are region specific and may not work across different countries. Selecting your region ensures the link works properly for you.
          </div>
        </div>
      </div>

      <button type="submit" disabled={loading}>
        {loading ? 'Converting...' : 'Convert'}
      </button>
    </form>

    {#if error}
      <div class="error-box">
        <p>{error}</p>
      </div>
    {/if}

    {#if result}
      <div class="results-container">
        <!-- Converted Link -->
        <div class="result-item">
          <div class="link-info">
            <span class="platform-label">{convertedPlatform} Link</span>
            <a href={result.converted_url} target="_blank" rel="noopener noreferrer" class="link url-link">
              {result.converted_url}
            </a>
          </div>
          <button
            class="copy-btn"
            on:click={() => handleCopyToClipboard(result.converted_url, 'single')}
            title="Copy {convertedPlatform} link"
          >
            {#if copied === 'single'}
              <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>
            {:else}
              <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
            {/if}
          </button>
        </div>

        <div class="result-item">
          <div class="link-info">
            <span class="platform-label">Share Both</span>
            <span class="link-description">{sourcePlatform} & {convertedPlatform} links</span>
          </div>
          <button
            class="copy-btn"
            on:click={() => handleCopyToClipboard(`${sourcePlatform}: ${result.source_url}\n\n${convertedPlatform}: ${result.converted_url}`, 'combined')}
            title="Copy both links"
          >
             {#if copied === 'combined'}
              <svg xmlns="http://www.w3.org/2000/svg" class="icon" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>
            {:else}
              <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
            {/if}
          </button>
        </div>
      </div>
    {/if}
  </main>

  <footer>
    <div class="footer-content">
        <p class="main-line">
            Made with ❤️ in Madison
        </p>
        <p class="contact">
            Issues? Contact: <a href="mailto:guthijp.reddy@gmail.com">guthijp.reddy@gmail.com</a>
        </p>
        <p class="font-credit">
            Font by <a href="http://bythebutterfly.com" target="_blank" rel="noopener noreferrer">Vanessa Bays</a>
        </p>
    </div>
  </footer>
</div>

<style>
  @font-face {
    font-family: 'PleaseWriteMeASong';
    src: url('/fonts/PleaseWriteMeASong.ttf') format('truetype');
    font-display: swap;
  }

  @font-face {
    font-family: 'GT-Walsheim';
    src: url('/fonts/GT-Walsheim-Regular.otf') format('opentype');
    font-weight: normal;
    font-style: normal;
    font-display: swap;
  }

  :global(html, body) {
    background-color: #fdfcfb;
    color: #2d3748;
    font-family: 'GT-Walsheim', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
      Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    margin: 0;
    padding: 0;
    min-height: 100svh;
    overflow-x: hidden;
    box-sizing: border-box;
  }

  .container {
    min-height: 100svh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    width: 100%;
    max-width: 600px;
    margin: 0 auto;
    padding: 1rem;
    box-sizing: border-box;
    text-align: center;
  }

  header h1 {
    font-family: "PleaseWriteMeASong";
    font-size: 3rem;
    font-weight: 700;
    color: #FC2D55;
    margin-bottom: 0.5rem;
  }

  header p {
    font-family: "PleaseWriteMeASong";
    font-size: 1.5rem;
    font-weight: 700;
    color: #4a5568;
    margin: 1rem;
  }

  main {
    margin-top: 2rem;
    background-color: #ffffff;
    border-radius: 1rem;
    padding: 1.5rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
    width: 100%;
    box-sizing: border-box;
  }

  .input-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .url-input {
    flex: 1;
    padding: 1rem;
    text-align: left;
    background-color: #f7fafc;
    border: 2px solid #e2e8f0;
    border-radius: 0.5rem;
    color: #4a5568;
    font-size: 1rem;
    transition: border-color 0.3s, box-shadow 0.3s;
    box-sizing: border-box;
    font-family: inherit;
    height: 3.5rem;
  }

  .url-input::placeholder {
    color: #a0aec0;
  }

  .url-input:focus {
    outline: none;
    border-color: #FC2D55;
    box-shadow: 0 0 0 3px rgba(252, 45, 85, 0.3);
  }

  .country-selector {
    position: relative;
    z-index: 10;
  }

  .country-button {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0 0.5rem;
    background-color: #f7fafc;
    border: 2px solid #e2e8f0;
    border-radius: 0.5rem;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s;
    box-sizing: border-box;
    font-family: inherit;
    white-space: nowrap;
    height: 3.5rem;
  }

  .country-button:hover {
    background-color: #edf2f7;
    border-color: #cbd5e0;
  }

  .country-button:focus {
    outline: none;
    border-color: #FC2D55;
    box-shadow: 0 0 0 3px rgba(252, 45, 85, 0.3);
  }

  .flag-image {
    width: 20px;
    height: 15px;
    object-fit: cover;
    border-radius: 2px;
  }



  .dropdown-arrow {
    width: 1rem;
    height: 1rem;
    color: #718096;
  }

  .country-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    min-width: 250px;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 0.5rem;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
    max-height: 200px;
    overflow-y: auto;
    z-index: 20;
    margin-top: 0.25rem;
  }

  .country-option {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    width: 100%;
    padding: 0.75rem;
    border: none;
    background: white;
    cursor: pointer;
    transition: background-color 0.2s;
    font-family: inherit;
    text-align: left;
  }

  .country-option:hover {
    background-color: #f7fafc;
  }

  .country-option.selected {
    background-color: #ebf8ff;
    color: #3182ce;
  }

  .country-name {
    flex: 1;
    font-size: 0.875rem;
    color: #4a5568;
  }

  .country-code-small {
    font-size: 0.75rem;
    color: #718096;
    font-weight: 600;
  }

  .help-tooltip {
    position: relative;
  }

  .info-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    background-color: #e2e8f0;
    border-radius: 50%;
    color: #718096;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s;
    font-family: inherit;
  }

  .info-icon:hover {
    background-color: #cbd5e0;
    color: #4a5568;
    transform: scale(1.1);
  }

  .tooltip-content {
    position: absolute;
    bottom: 150%;
    right: -140px;
    width: 280px;
    background-color: #2d3748;
    color: white;
    text-align: left;
    border-radius: 0.5rem;
    padding: 0.75rem;
    font-size: 0.875rem;
    line-height: 1.4;
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.3s, visibility 0.3s;
    z-index: 30;
  }

  .tooltip-content::after {
    content: '';
    position: absolute;
    top: 100%;
    right: 150px;
    width: 0;
    height: 0;
    border-left: 8px solid transparent;
    border-right: 8px solid transparent;
    border-top: 8px solid #2d3748;
  }

  .help-tooltip:hover .tooltip-content {
    opacity: 1;
    visibility: visible;
  }

  button[type="submit"] {
    width: 100%;
    margin-top: 1rem;
    padding: 0.75rem 1rem;
    background: #FC2D55;
    color: white;
    border: none;
    border-radius: 0.5rem;
    font-size: 1.125rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    font-family: inherit;
  }

  button[type="submit"]:hover:not(:disabled) {
    opacity: 0.9;
    transform: scale(1.05);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  }
  
  button[type="submit"]:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .error-box {
    margin-top: 1.5rem;
    background-color: #fff5f5;
    border: 1px solid #fecaca;
    color: #c53030;
    padding: 1rem;
    border-radius: 0.5rem;
  }

  .results-container {
    margin-top: 2rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .result-item {
    background-color: #f7fafc;
    border-radius: 0.5rem;
    padding: 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    border: 1px solid #e2e8f0;
  }

  .link-info {
    text-align: left;
    min-width: 0;
  }

  .platform-label {
    font-size: 0.875rem;
    font-weight: 600;
    color: #0369a1; 
  }

  .link {
    display: block;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    color: #4a5568;
    text-decoration: none;
  }
  .link:hover {
    text-decoration: underline;
  }
  

  .link-description {
    display: block;
    font-size: 0.875rem;
    color: #718096; 
  }
  
  .copy-btn {
    flex-shrink: 0;
    width: 3rem;
    height: 3rem;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #e2e8f0;
    border: none;
    border-radius: 0.5rem;
    margin: 0;
    padding: 0;
    transition: all 0.3s;
    color: #4a5568;
    cursor: pointer;
    font-family: inherit;
  }

  .copy-btn:hover {
    background-color: #cbd5e0;
    transform: none;
    opacity: 1;
    box-shadow: none;
  }

  .copy-btn:hover .icon {
    transform: scale(1.1);
  }

  .icon {
    width: 1.1rem;
    height: 1.1rem;
  }

  .copy-btn .icon:nth-child(1) {
    color: #FC2D55; 
  }

  .url-link {
    display: block;
    font-size: 0.875rem;
    color: #718096;
  }

  footer {
    margin-top: auto;
    padding: 2rem 0;
    border-top: 1px solid #e2e8f0;
    text-align: center;
    width: 100%;
  }

  .footer-content {
    max-width: 600px;
    margin: 0 auto;
  }

  .footer-content p {
    margin: 0.5rem 0;
    font-size: 0.875rem;
    color: #718096;
    line-height: 1.5;
  }

  .footer-content a {
    color: #FC2D55;
    text-decoration: none;
    transition: opacity 0.2s;
  }

  .footer-content a:hover {
    opacity: 0.8;
    text-decoration: underline;
  }

  .main-line {
    color: #6B46C1;
    margin-bottom: 0.75rem;
  }

  @media (max-width: 768px) {
    .container {
      padding: 0.75rem;
      min-height: 100dvh;
    }
    
    header h1 {
      font-size: 2.5rem;
    }
    
    header p {
      font-size: 1.25rem;
      margin: 0.5rem;
    }
    
    main {
      padding: 1rem;
      margin-top: 1rem;
    }
    
    .input-row {
      gap: 0.5rem;
    }

    .url-input {
      min-width: 0;
      flex: 1;
    }

    .country-button {
      padding: 0 0.375rem;
      min-width: fit-content;
    }

    .info-icon {
      width: 1.75rem;
      height: 1.75rem;
      font-size: 0.875rem;
    }

    .tooltip-content {
      right: auto;
      left: -150px;
      width: 200px;
    }

    .tooltip-content::after {
      left: 160px;
    }
    
    footer {
      padding: 1.5rem 0;
    }
  }
</style>
