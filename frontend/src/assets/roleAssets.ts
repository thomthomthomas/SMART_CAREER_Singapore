// src/assets/roleAssets.ts
export type RoleSlug =
  | 'ai-engineer'
  | 'ai-data-engineer'
  | 'machine-learning-engineer'
  | 'data-scientist'
  | 'ai-product-manager'
  | 'ai-security-specialist';

type RoleAsset = {
  title: string;
  image: string; // file name in /public/images
  pdf: string;   // file name in /public/pdf
  json: string;  // file name in /public/json_transcribe
};

export const ROLE_ASSETS: Record<RoleSlug, RoleAsset> = {
  'ai-engineer': {
    title: 'AI Engineer',
    image: 'ai_engineer.jpg',
    pdf: 'AI_Engineer_skills_report.pdf',
    json: 'AI_Engineer_20250908_124310_analysis.json', // use your actual file name
  },
  'ai-data-engineer': {
    title: 'AI Data Engineer',
    image: 'ai_data_engineer.jpg',
    pdf: 'AI_Data_Engineer_skills_report.pdf',
    json: 'AI_Data_Engineer_20250908_124618_analysis.json',
  },
  'machine-learning-engineer': {
    title: 'Machine Learning Engineer',
    image: 'machine_learning_engineer.webp',
    pdf: 'Machine_Learning_Engineer_skills_report.pdf',
    json: 'Machine_Learning_Engineer_20250908_124443_analysis.json',
  },
  'data-scientist': {
    title: 'Data Scientist',
    image: 'data_scientist.jpg',
    pdf: 'Data_Scientist_skills_report.pdf',
    json: 'Data_Scientist_20250908_124748_analysis.json',
  },
  'ai-product-manager': {
    title: 'AI Product Manager',
    image: 'AI_Product_Management.jpg',
    pdf: 'AI_Product_Manager_skills_report.pdf',
    json: 'AI_Product_Manager_20250908_124927_analysis.json',
  },
  'ai-security-specialist': {
    title: 'AI Security Specialist',
    image: 'ai_security_specialist.png',
    pdf: 'AI_Security_Specialist_skills_report.pdf',
    json: 'AI_Security_Specialist_20250908_125105_analysis.json',
  },
};
