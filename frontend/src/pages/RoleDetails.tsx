// src/pages/RoleDetails.tsx
import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import type { RoleContent } from "../types";
import { useImageSearch } from "../hooks/useImageSearch";
import {
  Download,
  Home,
  ArrowLeft,
  CheckCircle,
  Lightbulb,
  FileText,
  ExternalLink,
} from "lucide-react";

// 🔗 local assets map (images, pdfs, json)
import { ROLE_ASSETS, type RoleSlug } from "../assets/roleAssets";

// --- Your existing fallback content kept intact ---
const FALLBACKS: Record<string, RoleContent> = {
  "software-developer": {
    role: "Software Developer",
    summary:
      "Software developers design, build, and maintain applications and systems that power our digital world. They work across various platforms, from web and mobile applications to enterprise software and embedded systems. In Singapore's thriving tech ecosystem, developers collaborate with cross-functional teams to solve complex problems, implement new features, and ensure software quality. The role demands both technical expertise and creative problem-solving skills, as developers must translate business requirements into functional, scalable, and user-friendly solutions.",
    facts: [
      "Singapore has over 200,000 tech professionals with software development being the most in-demand skill",
      "Average salary ranges from S$60,000 to S$150,000+ annually depending on experience and specialization",
      "Remote and hybrid work options are increasingly common, with 70% of companies offering flexible arrangements",
      "The demand for full-stack developers has grown by 35% year-over-year in Singapore's job market",
    ],
    skills: [
      "JavaScript",
      "Python",
      "React",
      "Node.js",
      "SQL",
      "Git",
      "AWS",
      "Docker",
      "TypeScript",
      "API Development",
      "Testing",
      "Agile",
      "Problem Solving",
      "Debugging",
      "System Design",
    ],
    pdfUrl: "/api/roles/software-developer/pdf",
    imageQuery: "software developer coding programming",
  },
  "data-scientist": {
    role: "Data Scientist",
    summary:
      "Data scientists extract meaningful insights from complex datasets to drive business decisions and innovation. They combine statistical analysis, machine learning, and domain expertise to solve real-world problems across industries. In Singapore's data-driven economy, data scientists work with stakeholders to identify opportunities, build predictive models, and communicate findings through compelling visualizations. The role requires both technical proficiency in programming and analytics tools, as well as strong business acumen to translate data insights into actionable strategies.",
    facts: [
      "Data science roles in Singapore have grown by 50% in the past two years across finance, healthcare, and e-commerce",
      "Average salary ranges from S$80,000 to S$180,000+ with senior roles commanding premium compensation",
      "Python and R are the most sought-after programming languages, with SQL being essential for data manipulation",
      "Machine learning and AI specializations can increase earning potential by 25-40% above base data science roles",
    ],
    skills: [
      "Python",
      "R",
      "SQL",
      "Machine Learning",
      "Statistics",
      "Pandas",
      "Scikit-learn",
      "TensorFlow",
      "Data Visualization",
      "Jupyter",
      "A/B Testing",
      "Big Data",
      "Cloud Platforms",
      "Business Intelligence",
      "Communication",
    ],
    pdfUrl: "/api/roles/data-scientist/pdf",
    imageQuery: "data science analytics machine learning",
  },
};

// Types that match your JSON shape (flexible)
type RoleJson = {
  main_role?: string;
  summary?: string;
  facts?: string[];
  // some JSONs use skills[], some use skills_breakdown:[{skill}]
  skills?: string[];
  skills_breakdown?: Array<{ skill: string }>;
  generated_on?: string;
};

export default function RoleDetails() {
  const { slug = "" } = useParams();
  const localMeta = useMemo(
    () => ROLE_ASSETS[slug as RoleSlug],
    [slug]
  );

  const [data, setData] = useState<(RoleContent & { imageUrl?: string }) | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // image handling: prefer local -> if fails, fallback to search hook
  const [localImgOk, setLocalImgOk] = useState(true);
  const searchedImg = useImageSearch(data?.imageQuery || data?.role);

  // keep a ref so we only try the backend once after local JSON 404s
  const triedBackendRef = useRef(false);

  // helper to normalize JSON into RoleContent-ish structure
  const normalizeJson = (j: RoleJson): RoleContent => {
    return {
      role: j.main_role || localMeta?.title || slug,
      summary:
        j.summary ||
        "Details coming soon. Download the PDF guide for the full breakdown.",
      facts: j.facts || [],
      // prefer flat skills[], else map skills_breakdown[].skill
      skills:
        j.skills && j.skills.length
          ? j.skills
          : j.skills_breakdown?.map((s) => s.skill) || [],
      // for the UI sections that expect these optional fields
      pdfUrl: localMeta ? `/pdf/${localMeta.pdf}` : undefined,
      imageQuery: localMeta?.title,
    };
  };

  useEffect(() => {
    let cancelled = false;

    async function loadFromLocalJson() {
      if (!localMeta) return Promise.reject(new Error("No local meta"));

      const url = `/json_transcribe/${localMeta.json}`;
      const res = await fetch(url, { cache: "no-store" });
      if (!res.ok) {
        throw new Error(`Local JSON not found: ${url} (${res.status})`);
      }
      const j: RoleJson = await res.json();
      return normalizeJson(j);
    }

    async function loadFromBackend() {
      const res = await fetch(`http://localhost:5000/api/roles/${slug}`);
      if (!res.ok) {
        throw new Error(`Backend failed: ${res.status}`);
      }
      const j = await res.json();
      return j as RoleContent;
    }

    async function load() {
      setLoading(true);
      setError(null);
      triedBackendRef.current = false;

      try {
        // 1) try local JSON (public/json_transcribe)
        const localData = await loadFromLocalJson();
        if (!cancelled) setData(localData);
      } catch {
        // 2) fallback to backend API once
        try {
          triedBackendRef.current = true;
          const backendData = await loadFromBackend();
          if (!cancelled) setData(backendData);
        } catch {
          // 3) final fallback to hardcoded content
          const fallbackData = FALLBACKS[slug];
          if (!cancelled) {
            if (fallbackData) setData(fallbackData);
            else setError("Role not found");
          }
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [slug, localMeta]);

  // derive skills (limit 15 like your old code)
  const skillList = useMemo(() => (data?.skills || []).slice(0, 15), [data]);

  // hero image: local first → fallback to searched image
  const heroImage =
    localMeta && localImgOk
      ? `/images/${localMeta.image}`
      : data?.imageUrl || searchedImg;

  // build primary PDF url: local first → backend-provided url
  const localPdfUrl = localMeta ? `/pdf/${localMeta.pdf}` : undefined;
  const backendPdfUrl = data?.pdfUrl?.startsWith("/api/")
    ? `http://localhost:5000${data.pdfUrl}`
    : data?.pdfUrl;
  const pdfHref = localPdfUrl || backendPdfUrl;

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-32 mb-8"></div>
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              <div className="lg:col-span-5">
                <div className="h-64 bg-gray-200 rounded-2xl"></div>
              </div>
              <div className="lg:col-span-7 space-y-4">
                <div className="h-8 bg-gray-200 rounded w-3/4"></div>
                <div className="h-4 bg-gray-200 rounded w-full"></div>
                <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                <div className="h-4 bg-gray-200 rounded w-4/5"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <FileText className="w-8 h-8 text-red-600" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-4">
              Role Not Found
            </h1>
            <p className="text-gray-600 mb-8">
              We couldn't load information for this role right now. Please try
              again later or explore other career options.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/careers" className="btn-primary">
                <Home className="w-4 h-4 mr-2" />
                Back to Career Hub
              </Link>
              <Link to="/" className="btn-secondary">
                Return to Home
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <header className="relative overflow-hidden border-b border-white/20">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/5 to-purple-600/5"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Link
            to="/careers"
            className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Career Hub
          </Link>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12">
          {/* Left Column: Image */}
          <div className="lg:col-span-5">
            <div className="sticky top-8">
              <div className="relative overflow-hidden rounded-2xl shadow-xl ring-1 ring-black/5 group">
                {heroImage ? (
                  <img
                    src={heroImage}
                    alt={data.role}
                    className="w-full h-64 sm:h-80 object-cover group-hover:scale-105 transition-transform duration-500"
                    onError={() => setLocalImgOk(false)}
                  />
                ) : (
                  <div className="h-64 sm:h-80 bg-gradient-to-br from-gray-200 to-gray-100 flex items-center justify-center">
                    <FileText className="w-16 h-16 text-gray-400" />
                  </div>
                )}
                <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              </div>
            </div>
          </div>

          {/* Right Column: Content */}
          <div className="lg:col-span-7 space-y-8">
            {/* Title and PDF Download */}
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
              <div>
                <h1 className="text-3xl sm:text-4xl font-extrabold text-gray-900 mb-2">
                  {data.role}
                </h1>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  High-Demand Career Path
                </div>
              </div>

              {pdfHref && (
                <a
                  href={pdfHref}
                  className="btn-primary flex-shrink-0 inline-flex items-center gap-2"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Download className="w-4 h-4" />
                  Download PDF Guide
                </a>
              )}
            </div>

            {/* Summary */}
            <div className="card p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <FileText className="w-5 h-5 text-blue-600" />
                Role Overview
              </h2>
              <p className="text-gray-700 leading-relaxed text-lg">
                {data.summary}
              </p>
              {/* Optional "Updated on" stamp if JSON had it */}
              {localMeta && (
                <p className="mt-3 text-xs text-gray-500">
                  Source: local guide {triedBackendRef.current ? "+ backend" : ""}.
                </p>
              )}
            </div>

            {/* Interesting Facts */}
            {data.facts?.length > 0 && (
              <div className="card p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <Lightbulb className="w-5 h-5 text-yellow-600" />
                  Interesting Facts
                </h2>
                <ul className="space-y-3">
                  {data.facts.slice(0, 4).map((fact, index) => (
                    <li
                      key={index}
                      className="flex items-start gap-3 text-gray-700"
                    >
                      <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                      <span className="leading-relaxed">{fact}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Key Skills */}
            {skillList.length > 0 && (
              <div className="card p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  Key Skills ({skillList.length})
                </h2>
                <div className="flex flex-wrap gap-2">
                  {skillList.map((skill, index) => (
                    <span
                      key={index}
                      className="skill-tag hover:border-blue-300 hover:bg-blue-50 transition-colors"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4">
              <Link to="/careers" className="btn-secondary flex-1 justify-center">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Explore More Roles
              </Link>
              <Link to="/" className="btn-secondary flex-1 justify-center">
                <Home className="w-4 h-4 mr-2" />
                Return to Home
              </Link>
            </div>

            {/* Additional Resources */}
            {pdfHref && (
              <div className="card p-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
                <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                  <ExternalLink className="w-4 h-4 text-blue-600" />
                  Comprehensive Career Guide
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Download our detailed PDF guide for in-depth information about
                  skills, learning paths, and career progression opportunities.
                </p>
                <a
                  href={pdfHref}
                  className="text-blue-600 hover:text-blue-700 font-medium text-sm inline-flex items-center gap-1"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Access Full Guide
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
