import { useEffect, useState } from "react";

/**
 * Deterministic Unsplash Source image by query (no API key).
 * If your API returns `imageUrl`, prefer that directly.
 */
export function useImageSearch(query?: string) {
  const [url, setUrl] = useState<string | undefined>(undefined);

  useEffect(() => {
    if (!query) return;
    let hash = 0;
    for (let i = 0; i < query.length; i++) hash = ((hash << 5) - hash) + query.charCodeAt(i);
    const sig = Math.abs(hash);
    setUrl(`https://source.unsplash.com/featured/800x450?${encodeURIComponent(query)}&sig=${sig}`);
  }, [query]);

  return url;
}

