import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { ArrowLeft, GraduationCap, TrendingUp, MapPin, X } from 'lucide-react';

interface JobInfo {
  id: string;
  title: string;
  category: string;
  description: string;
  interestingFacts: string[];
  skills: string[];
  growthRate: string;
  workEnvironment: string;
  educationPath: string;
  coursePlatforms: string[];
  color: string;
  icon: string;
}

export function NewPage() {
  const [selectedJob, setSelectedJob] = useState<JobInfo | null>(null);
  const [hoveredJob, setHoveredJob] = useState<string | null>(null);

  const jobInformation: JobInfo[] = [
    {
      id: 'software-dev',
      title: "Software Developer",
      category: "Technology",
      description: "Software developers design, create, and maintain computer programs and applications. They work with various programming languages to solve problems and create digital solutions.",
      interestingFacts: [
        "The first computer programmer was Ada Lovelace in 1843",
        "There are over 700 programming languages in existence",
        "The average developer makes 104 mistakes per 1000 lines of code"
      ],
      skills: ["Programming", "Problem Solving", "Logic", "Debugging"],
      growthRate: "22% (Much faster than average)",
      workEnvironment: "Office, Remote, or Hybrid",
      educationPath: "Computer Science degree or coding bootcamp",
      coursePlatforms: ["Coursera: CS50 Introduction to Computer Science", "edX: MIT Introduction to Programming"],
      color: "from-blue-500 to-cyan-500",
      icon: "💻"
    },
    {
      id: 'data-scientist',
      title: "Data Scientist",
      category: "Analytics",
      description: "Data scientists analyze large amounts of data to identify patterns, trends, and insights that help organizations make informed business decisions.",
      interestingFacts: [
        "Data scientists are often called 'unicorns' due to their rare skill combination",
        "90% of the world's data was created in the last two years",
        "A data scientist typically spends 80% of their time cleaning data"
      ],
      skills: ["Statistics", "Python/R", "Machine Learning", "Data Visualization"],
      growthRate: "35% (Much faster than average)",
      workEnvironment: "Office, Remote, or Research Labs",
      educationPath: "Statistics, Mathematics, or Computer Science degree",
      coursePlatforms: ["Coursera: IBM Data Science Professional Certificate", "edX: Harvard Data Science Program"],
      color: "from-purple-500 to-pink-500",
      icon: "📊"
    },
    {
      id: 'digital-marketing',
      title: "Digital Marketing Specialist",
      category: "Marketing",
      description: "Digital marketing specialists create and implement online marketing strategies to promote products, services, or brands across digital channels.",
      interestingFacts: [
        "The first banner ad was created in 1994 and had a 44% click-through rate",
        "Email marketing has an average ROI of $42 for every $1 spent",
        "Video content is 50x more likely to drive organic search results than text"
      ],
      skills: ["Content Creation", "SEO/SEM", "Analytics", "Social Media"],
      growthRate: "19% (Much faster than average)",
      workEnvironment: "Office, Remote, or Agency",
      educationPath: "Marketing, Communications, or Business degree",
      coursePlatforms: ["Coursera: Google Digital Marketing Certificate", "edX: University of Pennsylvania Marketing Analytics"],
      color: "from-orange-500 to-red-500",
      icon: "📱"
    },
    {
      id: 'ux-designer',
      title: "UX/UI Designer",
      category: "Design",
      description: "UX/UI designers focus on creating user-friendly and visually appealing interfaces for websites, mobile apps, and other digital products.",
      interestingFacts: [
        "Every $1 invested in UX design returns between $2-100",
        "Users form an opinion about a website in 0.05 seconds",
        "The term 'User Experience' was coined by Don Norman at Apple in the 1990s"
      ],
      skills: ["Design Software", "User Research", "Prototyping", "Visual Design"],
      growthRate: "13% (Faster than average)",
      workEnvironment: "Office, Remote, or Design Studios",
      educationPath: "Design, Psychology, or related degree",
      coursePlatforms: ["Coursera: Google UX Design Certificate", "edX: University of Michigan UX Research and Design"],
      color: "from-green-500 to-teal-500",
      icon: "🎨"
    },
    {
      id: 'cybersecurity',
      title: "Cybersecurity Analyst",
      category: "Security",
      description: "Cybersecurity analysts protect organizations' computer networks and systems from cyber threats, data breaches, and other security incidents.",
      interestingFacts: [
        "A cyber attack occurs every 39 seconds on average",
        "The global cost of cybercrime is expected to reach $10.5 trillion by 2025",
        "There are currently 3.5 million unfilled cybersecurity jobs worldwide"
      ],
      skills: ["Network Security", "Risk Assessment", "Incident Response", "Ethical Hacking"],
      growthRate: "35% (Much faster than average)",
      workEnvironment: "Office, Government Agencies, or Remote",
      educationPath: "Computer Science, Information Technology, or related degree",
      coursePlatforms: ["Coursera: IBM Cybersecurity Analyst Certificate", "edX: RIT Cybersecurity MicroMasters"],
      color: "from-red-500 to-rose-500",
      icon: "🔒"
    },
    {
      id: 'project-manager',
      title: "Project Manager",
      category: "Management",
      description: "Project managers plan, execute, and oversee projects from initiation to completion, ensuring they meet deadlines, budgets, and quality standards.",
      interestingFacts: [
        "Only 64% of projects meet their goals and business intent",
        "Poor project management causes $97 million loss for every $1 billion invested",
        "Agile project management can improve team productivity by up to 25%"
      ],
      skills: ["Leadership", "Planning", "Communication", "Risk Management"],
      growthRate: "11% (Faster than average)",
      workEnvironment: "Office, Remote, or On-site",
      educationPath: "Business, Engineering, or any degree + PM certification",
      coursePlatforms: ["Coursera: Google Project Management Certificate", "edX: University of Adelaide Project Management"],
      color: "from-indigo-500 to-purple-500",
      icon: "📋"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm shadow-sm border-b border-white/20">
        <div className="max-w-7xl mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <Link to="/">
                <Button variant="ghost" size="sm" className="hover:bg-white/60">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back to Home
                </Button>
              </Link>
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg flex items-center justify-center">
                  <GraduationCap className="w-5 h-5 text-white" />
                </div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">Smart Career SG</h1>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold mb-6 bg-gradient-to-r from-gray-900 via-purple-900 to-blue-900 bg-clip-text text-transparent">
            Career Information Hub
          </h2>
          <p className="text-xl text-gray-700 max-w-3xl mx-auto leading-relaxed">
            Click on each career circle to discover detailed information, interesting facts, and educational pathways.
          </p>
        </div>

        {/* Circular Job Display */}
        <div className="relative min-h-[600px] flex items-center justify-center mb-20">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-12 md:gap-16">
            {jobInformation.map((job, index) => (
              <div
                key={job.id}
                className="group relative cursor-pointer"
                onMouseEnter={() => setHoveredJob(job.id)}
                onMouseLeave={() => setHoveredJob(null)}
                onClick={() => setSelectedJob(job)}
              >
                {/* Job Circle */}
                <div className={`w-32 h-32 md:w-40 md:h-40 bg-gradient-to-br ${job.color} rounded-full flex flex-col items-center justify-center text-white shadow-2xl transform transition-all duration-500 group-hover:scale-110 group-hover:shadow-3xl group-hover:-translate-y-2 ${hoveredJob === job.id ? 'ring-4 ring-white/50' : ''}`}>
                  <div className="text-4xl md:text-5xl mb-2">{job.icon}</div>
                  <div className="text-center px-2">
                    <h3 className="font-bold text-sm md:text-base leading-tight">{job.title}</h3>
                    <Badge variant="secondary" className="mt-2 text-xs bg-white/20 text-white border-white/30">
                      {job.category}
                    </Badge>
                  </div>
                </div>

                {/* Hover Ring Effect */}
                <div className={`absolute inset-0 w-32 h-32 md:w-40 md:h-40 bg-gradient-to-br ${job.color} rounded-full opacity-20 scale-125 group-hover:scale-150 transition-all duration-500`}></div>
                
                {/* Hover Tooltip */}
                {hoveredJob === job.id && (
                  <div className="absolute -top-12 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white px-3 py-1 rounded-lg text-sm whitespace-nowrap z-10 pointer-events-none">
                    Click to learn more
                    <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900"></div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Job Details Popup */}
        {selectedJob && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <Card className="max-w-2xl w-full max-h-[80vh] overflow-y-auto bg-white/95 backdrop-blur-sm border-2 border-white/20 shadow-2xl">
              <div className="sticky top-0 bg-white/95 backdrop-blur-sm border-b p-6 flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <div className={`w-16 h-16 bg-gradient-to-br ${selectedJob.color} rounded-2xl flex items-center justify-center text-white text-2xl shadow-lg`}>
                    {selectedJob.icon}
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900">{selectedJob.title}</h3>
                    <Badge variant="secondary" className="mt-1">{selectedJob.category}</Badge>
                  </div>
                </div>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => setSelectedJob(null)}
                  className="hover:bg-gray-100"
                >
                  <X className="w-5 h-5" />
                </Button>
              </div>
              
              <CardContent className="p-6 space-y-6">
                {/* Quick Stats */}
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <TrendingUp className="w-4 h-4 text-green-600" />
                    <span className="font-medium">Growth:</span> {selectedJob.growthRate}
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <MapPin className="w-4 h-4 text-blue-600" />
                    <span className="font-medium">Environment:</span> {selectedJob.workEnvironment}
                  </div>
                </div>

                {/* Description */}
                <div>
                  <h4 className="font-semibold text-lg mb-3 text-gray-900">What They Do</h4>
                  <p className="text-gray-700 leading-relaxed">{selectedJob.description}</p>
                </div>

                {/* Interesting Facts */}
                <div>
                  <h4 className="font-semibold text-lg mb-3 text-gray-900">Interesting Facts</h4>
                  <ul className="space-y-3">
                    {selectedJob.interestingFacts.map((fact, factIndex) => (
                      <li key={factIndex} className="flex items-start gap-3 text-gray-700">
                        <span className="w-2 h-2 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full mt-2 flex-shrink-0"></span>
                        <span className="leading-relaxed">{fact}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Skills */}
                <div>
                  <h4 className="font-semibold text-lg mb-3 text-gray-900">Key Skills Required</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedJob.skills.map((skill, skillIndex) => (
                      <Badge key={skillIndex} variant="outline" className="text-sm">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Education Path */}
                <div>
                  <h4 className="font-semibold text-lg mb-3 text-gray-900">Education Path</h4>
                  <p className="text-gray-700 mb-4 leading-relaxed">{selectedJob.educationPath}</p>
                  
                  <h5 className="font-medium text-base mb-3 text-gray-900">Recommended Online Courses</h5>
                  <ul className="space-y-2">
                    {selectedJob.coursePlatforms.map((course, courseIndex) => (
                      <li key={courseIndex} className="text-sm text-blue-600 hover:text-blue-800 cursor-pointer transition-colors">
                        • {course}
                      </li>
                    ))}
                  </ul>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Call to Action */}
        <div className="text-center">
          <Card className="bg-gradient-to-r from-purple-50 to-blue-50 border-2 border-purple-200/50 max-w-4xl mx-auto">
            <CardContent className="p-10">
              <h3 className="text-3xl font-bold mb-6 bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                Ready to Start Your Journey?
              </h3>
              <p className="text-lg text-gray-700 mb-8 max-w-2xl mx-auto leading-relaxed">
                Get personalized guidance from our AI career assistant. Chat with our bot to discover 
                which career path aligns best with your interests and goals.
              </p>
              <Link to="/existing">
                <Button className="text-lg font-semibold px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1">
                  Chat with Career Assistant
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}