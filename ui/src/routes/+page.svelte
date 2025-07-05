<script>
  import { API_ENDPOINTS } from '$lib/config.js';
  
  let url = '';
  let loading = false;
  let error = '';
  let result = null;
  let copied = null;

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
        body: JSON.stringify({ source_url: url }),
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

  $: sourcePlatform = result ? getPlatform(result.source_url) : '';
  $: convertedPlatform = result ? (sourcePlatform === 'Spotify' ? 'Apple Music' : 'Spotify') : '';
</script>

<svelte:head>
  <title>MuShare</title>
</svelte:head>

<div class="container">
  <header>
    <h1>| MuShare |</h1>
    <p>Convert links between Spotify and Apple Music in a snap</p>
  </header>

  <main>
    <form on:submit|preventDefault={handleSubmit}>
      <input
        type="url"
        bind:value={url}
        placeholder="Paste Spotify or Apple Music link..."
        required
      />
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
    color: #2d3748; /* Dark Gray for text */
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

  input {
    width: 100%;
    padding: 1rem;
    text-align: center;
    background-color: #f7fafc;
    border: 2px solid #e2e8f0;
    border-radius: 0.5rem;
    color: #4a5568;
    font-size: 1rem;
    transition: border-color 0.3s, box-shadow 0.3s;
    box-sizing: border-box;
    font-family: inherit;
  }

  input::placeholder {
    color: #a0aec0;
  }

  input:focus {
    outline: none;
    border-color: #FC2D55;
    box-shadow: 0 0 0 3px rgba(252, 45, 85, 0.3);
  }

  button {
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

  button:hover:not(:disabled) {
    opacity: 0.9;
    transform: scale(1.05);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  }
  
  button:disabled {
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
    border-radius: 0.5rem;
    margin: 0;
    transition: background-color 0.2s;
    color: #4a5568;
  }

  .copy-btn:hover {
    background-color: #cbd5e0;
  }

  .copy-btn:hover .icon {
    transform: scale(1.1);
  }

  .icon {
    width: 1.5rem;
    height: 1.5rem;
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
    
    footer {
      padding: 1.5rem 0;
    }
  }
</style>
