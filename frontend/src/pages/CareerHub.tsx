import { Link } from "react-router-dom";
import { useImageSearch } from "../hooks/useImageSearch";
import { ArrowRight, Flame, Home, Sparkles, TrendingUp } from "lucide-react";
import type { RoleCard } from "../types";

// Updated roles: align slugs with RoleDetails + your assets
const ROLES: (RoleCard & { image?: string })[] = [
  {
    slug: "ai-engineer",
    title: "AI Engineer",
    category: "Technology",
    image: "ai_engineer.jpg",
    imageQuery: "ai engineer coding deep learning",
    colorFrom: "from-blue-600",
    colorTo: "to-cyan-400",
    demand: "High",
  },
  {
    slug: "machine-learning-engineer",
    title: "Machine Learning Engineer",
    category: "Technology",
    image: "machine_learning_engineer.webp",
    imageQuery: "machine learning engineer model training deployment",
    colorFrom: "from-indigo-600",
    colorTo: "to-violet-400",
    demand: "High",
  },
  {
    slug: "data-scientist",
    title: "Data Scientist",
    category: "Analytics",
    image: "data_scientist.jpg",
    imageQuery: "data scientist analytics machine learning",
    colorFrom: "from-fuchsia-600",
    colorTo: "to-pink-400",
    demand: "High",
  },
  {
    slug: "ai-data-engineer",
    title: "AI Data Engineer",
    category: "Data",
    image: "ai_data_engineer.jpg",
    imageQuery: "data engineer big data pipelines",
    colorFrom: "from-emerald-600",
    colorTo: "to-teal-400",
    demand: "Rising",
  },
  {
    slug: "ai-security-specialist",
    title: "AI Security Specialist",
    category: "Security",
    image: "ai_security_specialist.png",
    imageQuery: "cybersecurity ai security analyst",
    colorFrom: "from-red-600",
    colorTo: "to-rose-400",
    demand: "High",
  },
  {
    slug: "ai-product-manager",
    title: "AI Product Manager",
    category: "Product",
    image: "AI_Product_Management.jpg",
    imageQuery: "product manager ai roadmap",
    colorFrom: "from-orange-600",
    colorTo: "to-rose-400",
    demand: "Rising",
  },
];

function RoleCardItem({
  slug,
  title,
  category,
  image,
  imageQuery,
  colorFrom,
  colorTo,
  demand,
}: RoleCard & { image?: string }) {
  // Prefer local /images asset; fall back to image search if missing
  const searched = useImageSearch(imageQuery);
  const img = image ? `/images/${image}` : searched;

  const getDemandIcon = () => {
    switch (demand) {
      case "High":
        return <Flame className="w-3.5 h-3.5" />;
      case "Rising":
        return <TrendingUp className="w-3.5 h-3.5" />;
      default:
        return <Sparkles className="w-3.5 h-3.5" />;
    }
  };

  const getDemandColor = () => {
    switch (demand) {
      case "High":
        return "bg-red-500/90";
      case "Rising":
        return "bg-orange-500/90";
      default:
        return "bg-blue-500/90";
    }
  };

  return (
    <Link to={`/careers/${slug}`} className="group">
      <div className="card overflow-hidden transition-all duration-300 group-hover:shadow-2xl group-hover:-translate-y-2">
        <div className="h-48 sm:h-52 relative overflow-hidden">
          <div className={`absolute inset-0 bg-gradient-to-br ${colorFrom} ${colorTo} opacity-90`} />
          {img && (
            <img
              src={img}
              alt={title}
              className="absolute inset-0 w-full h-full object-cover mix-blend-overlay opacity-80 group-hover:scale-105 transition-transform duration-500"
            />
          )}
          <div className="absolute bottom-4 left-4">
            <span className="text-white/95 text-xs font-medium px-3 py-1.5 rounded-full bg-black/30 backdrop-blur-sm">
              {category}
            </span>
          </div>
          {demand && (
            <div
              className={`absolute top-4 right-4 flex items-center gap-1.5 text-[11px] font-semibold text-white px-3 py-1.5 rounded-full ${getDemandColor()} backdrop-blur-sm`}
            >
              {getDemandIcon()}
              {demand} demand
            </div>
          )}
          <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        </div>

        <div className="p-6">
          <div className="flex items-center justify-between gap-3 mb-3">
            <h3 className="text-lg sm:text-xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
              {title}
            </h3>
            <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all duration-200" />
          </div>
          <p className="text-sm text-gray-600 leading-relaxed">
            Explore detailed role summary, interesting facts, key skills, and download the comprehensive PDF guide.
          </p>
        </div>
      </div>
    </Link>
  );
}

export default function CareerHub() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <header className="relative overflow-hidden border-b border-white/20">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/5 to-purple-600/5"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium transition-colors"
          >
            <Home className="w-4 h-4" />
            Back to Home
          </Link>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-16 animate-fade-in">
          <div className="inline-flex items-center gap-2 bg-blue-100 text-blue-700 px-4 py-2 rounded-full text-sm font-medium mb-6">
            <TrendingUp className="w-4 h-4" />
            High-Demand Careers
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-gray-900 mb-6">
            Career Information Hub
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Discover fast-growing roles where demand outpaces supply. Explore comprehensive summaries, fascinating facts,
            and the exact skills needed to succeed in Singapore's evolving job market.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 animate-slide-up">
          {ROLES.map((role) => (
            <RoleCardItem key={role.slug} {...role} />
          ))}
        </div>

        <div className="mt-16 text-center">
          <div className="card p-8 max-w-2xl mx-auto">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Ready to Start Your Journey?</h3>
            <p className="text-gray-600 mb-6">
              Each role page includes detailed insights, skill requirements, and downloadable PDF guides to help you make
              informed career decisions.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/" className="btn-secondary">
                Explore More Options
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
