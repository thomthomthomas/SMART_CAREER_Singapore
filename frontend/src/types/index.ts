export type RoleContent = {
  role: string;
  summary: string;      // 100–120 words
  facts: string[];      // 3–4 items
  skills: string[];     // up to 15 tags
  pdfUrl?: string;      // backend URL to download PDF
  imageQuery?: string;  // optional image query override
  imageUrl?: string;    // direct image URL from backend
};

export type RoleCard = {
  slug: string;
  title: string;
  category: string;
  imageQuery: string;
  colorFrom: string;
  colorTo: string;
  demand?: "High" | "Rising" | "Stable";
};

