import { Link } from 'react-router-dom';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { BookOpen, MessageSquare, GraduationCap, Briefcase, TreePine } from 'lucide-react';

export function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <header className="w-full py-6 px-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl flex items-center justify-center">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">Smart Career SG</h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-12">
        <div className="text-center mb-20">
          <h2 className="text-5xl font-bold mb-8 bg-gradient-to-r from-gray-900 via-purple-900 to-blue-900 bg-clip-text text-transparent leading-tight">
            Discover Your Career Path in Singapore
          </h2>
          <p className="text-xl text-gray-700 max-w-4xl mx-auto mb-8 leading-relaxed">
            Explore comprehensive information about jobs and courses from leading platforms like Coursera and edX. 
            Get insights into career opportunities and educational pathways to make informed decisions about your future.
          </p>
        </div>

        {/* Action Cards */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {/* Existing Users Card */}
          <Card className="group hover:shadow-2xl hover:scale-105 transition-all duration-500 bg-white/80 backdrop-blur-sm border-2 hover:border-purple-300 overflow-hidden relative">
            <div className="absolute inset-0 bg-gradient-to-br from-purple-50 to-blue-50 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <CardContent className="p-8 text-center relative z-10">
              <div className="mb-6">
                <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-blue-500 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                  <MessageSquare className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold mb-3 text-gray-900">Existing Users</h3>
                <p className="text-gray-600 mb-4 text-sm leading-relaxed">
                  Continue your journey with our AI-powered career assistant. Get personalized recommendations 
                  and explore job insights based on your interests and experience.
                </p>
              </div>
              <Link to="/existing">
                <Button className="w-full py-3 text-sm font-semibold bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1">
                  Access Career Assistant
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* New Users Card - Updated to link to /careers */}
          <Card className="group hover:shadow-2xl hover:scale-105 transition-all duration-500 bg-white/80 backdrop-blur-sm border-2 hover:border-emerald-300 overflow-hidden relative">
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-50 to-teal-50 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <CardContent className="p-8 text-center relative z-10">
              <div className="mb-6">
                <div className="w-16 h-16 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                  <Briefcase className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold mb-3 text-gray-900">New Opportunities</h3>
                <p className="text-gray-600 mb-4 text-sm leading-relaxed">
                  Discover detailed job descriptions, career insights, and fascinating facts about various 
                  professions. Perfect for exploring new career possibilities.
                </p>
              </div>
              <Link to="/careers">
                <Button className="w-full py-3 text-sm font-semibold bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1">
                  Explore Career Information
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Course Creation Card */}
          <Card className="group hover:shadow-2xl hover:scale-105 transition-all duration-500 bg-white/80 backdrop-blur-sm border-2 hover:border-orange-300 overflow-hidden relative">
            <div className="absolute inset-0 bg-gradient-to-br from-orange-50 to-amber-50 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <CardContent className="p-8 text-center relative z-10">
              <div className="mb-6">
                <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-amber-500 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                  <TreePine className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold mb-3 text-gray-900">Course Creation</h3>
                <p className="text-gray-600 mb-4 text-sm leading-relaxed">
                  Create personalized learning paths using our interactive skills tree. 
                  Build custom courses tailored to your career goals and learning preferences.
                </p>
              </div>
              <Link to="/course-creation">
                <Button className="w-full py-3 text-sm font-semibold bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1">
                  Build Your Learning Path
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* Features Section */}
        <div className="mt-20">
          <h3 className="text-2xl text-center mb-12 text-gray-900">
            Why Choose Smart Career SG?
          </h3>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <BookOpen className="w-6 h-6 text-purple-600" />
              </div>
              <h4 className="mb-3 text-gray-900">Educational Resources</h4>
              <p className="text-gray-600">
                Access curated information from top learning platforms like Coursera and edX
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <MessageSquare className="w-6 h-6 text-orange-600" />
              </div>
              <h4 className="mb-3 text-gray-900">AI-Powered Insights</h4>
              <p className="text-gray-600">
                Get personalized career guidance through our intelligent chatbot assistant
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <GraduationCap className="w-6 h-6 text-indigo-600" />
              </div>
              <h4 className="mb-3 text-gray-900">Singapore Focus</h4>
              <p className="text-gray-600">
                Specialized information tailored for the Singapore job market and education system
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-20 py-8 bg-white/50 backdrop-blur-sm border-t border-gray-200">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <p className="text-gray-600">
            © 2024 Smart Career SG. Empowering your career journey through education and insights.
          </p>
        </div>
      </footer>
    </div>
  );
}