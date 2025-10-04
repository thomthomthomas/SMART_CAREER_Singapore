import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import {
  ArrowLeft,
  Send,
  GraduationCap,
  Search,
  MessageCircle,
  Sparkles,
  Info,
  Loader2,
  CheckCircle,
  AlertCircle,
  FileText,
  Download,
} from 'lucide-react';

interface Message {
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  suggestions?: string[];
  action?: string;
}

interface AnalysisStatus {
  status: 'idle' | 'running' | 'completed' | 'error';
  progress: number;
  message: string;
  result_file?: string;
  error?: string;
}

interface AnalysisResult {
  status: string;
  data: any;
  file_path: string;
}

const API_BASE_URL = 'http://localhost:5000/api';

export function ExistingPage() {
  /** ----------------------------
   * Job Information Assistant (keeps original behavior)
   * ----------------------------- */
  const [jobInfoQuery, setJobInfoQuery] = useState('');
  const [jobInfoMessages, setJobInfoMessages] = useState<Message[]>([
    {
      type: 'bot',
      content:
        "Hello! I'm your Smart Career SG assistant. I can help you find information about jobs and courses (Coursera, edX, etc.). Ask me about a role, skills, or say 'start analysis' to kick off a personalized report.",
      timestamp: new Date(),
    },
  ]);
  const [jobInfoLoading, setJobInfoLoading] = useState(false);

  /** ----------------------------
   * General Job Support (friend's extra assistant)
   * ----------------------------- */
  const [generalQuery, setGeneralQuery] = useState('');
  const [generalMessages, setGeneralMessages] = useState<Message[]>([
    {
      type: 'bot',
      content:
        "Hi there! I'm your General Job Support Assistant. Ask me about workplace issues, career growth, interviews, or networking.",
      timestamp: new Date(),
    },
  ]);
  const [generalLoading, setGeneralLoading] = useState(false);

  /** ----------------------------
   * Analysis (shared/preserved)
   * ----------------------------- */
  const [analysisStatus, setAnalysisStatus] = useState<AnalysisStatus>({
    status: 'idle',
    progress: 0,
    message: '',
  });
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [pdfGenerating, setPdfGenerating] = useState(false);

  // Poll analysis status when running
  useEffect(() => {
    let interval: ReturnType<typeof setInterval> | undefined;
  
    if (analysisStatus.status === 'running') {
      interval = window.setInterval(async () => {
        try {
          const res = await fetch(`${API_BASE_URL}/analysis-status`);
          const status = await res.json();
          setAnalysisStatus(status);
          if (status.status === 'completed') {
            fetchAnalysisResult();
          }
        } catch (err) {
          console.error('Error fetching analysis status:', err);
        }
      }, 2000);
    }
  
    return () => {
      if (interval !== undefined) {
        window.clearInterval(interval);
      }
    };
  }, [analysisStatus.status]);
  

  const fetchAnalysisResult = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/analysis-result`);
      if (response.ok) {
        const result = await response.json();
        setAnalysisResult(result);
        const resultMessage: Message = {
          type: 'bot',
          content:
            'Analysis completed! Here are your personalized career insights and course recommendations.',
          timestamp: new Date(),
        };
        setJobInfoMessages((prev) => [...prev, resultMessage]);
      }
    } catch (err) {
      console.error('Error fetching analysis result:', err);
    }
  };

  const startAnalysis = async (skills: string[] = ['Data Analyst']) => {
    try {
      setJobInfoLoading(true);
      const response = await fetch(`${API_BASE_URL}/start-analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ skills }),
      });
      if (response.ok) {
        await response.json();
        setAnalysisStatus({
          status: 'running',
          progress: 0,
          message: 'Starting analysis...',
        });
      } else {
        const error = await response.json();
        throw new Error(error.error || 'Failed to start analysis');
      }
    } catch (err: unknown) {
      console.error('Error starting analysis:', err);
      const msg =
        err instanceof Error
          ? `Sorry, I encountered an error starting the analysis: ${err.message}. Please try again.`
          : 'Sorry, I encountered an error starting the analysis. Please try again.';
      setJobInfoMessages((prev) => [
        ...prev,
        { type: 'bot', content: msg, timestamp: new Date() },
      ]);
    } finally {
      setJobInfoLoading(false);
    }
  };

  /** ----------------------------
   * Chat handlers
   * ----------------------------- */
  const sendJobInfoMessage = async (messageContent: string) => {
    try {
      setJobInfoLoading(true);
      const userMessage: Message = {
        type: 'user',
        content: messageContent,
        timestamp: new Date(),
      };
      setJobInfoMessages((prev) => [...prev, userMessage]);

      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: messageContent }),
      });

      if (response.ok) {
        const botResponse = await response.json();
        const botMessage: Message = {
          type: 'bot',
          content: botResponse.message,
          timestamp: new Date(),
          suggestions: botResponse.suggestions,
          action: botResponse.action,
        };
        setJobInfoMessages((prev) => [...prev, botMessage]);

        if (botResponse.action === 'start_analysis') {
          const skills =
            botResponse.skills ||
            extractSkillsFromMessage(messageContent) ||
            ['Data Analyst'];
          setTimeout(() => startAnalysis(skills), 1000);
        }
      } else {
        throw new Error('Failed to send message');
      }
    } catch (err: unknown) {
      console.error('Error sending job info message:', err);
      const msg =
        err instanceof Error
          ? `Sorry, I encountered an error processing your message: ${err.message}. Please try again.`
          : 'Sorry, I encountered an error processing your message. Please try again.';
      setJobInfoMessages((prev) => [
        ...prev,
        { type: 'bot', content: msg, timestamp: new Date() },
      ]);
    } finally {
      setJobInfoLoading(false);
    }
  };

  const sendGeneralMessage = async (messageContent: string) => {
    try {
      setGeneralLoading(true);
      const userMessage: Message = {
        type: 'user',
        content: messageContent,
        timestamp: new Date(),
      };
      setGeneralMessages((prev) => [...prev, userMessage]);

      const response = await fetch(`${API_BASE_URL}/general-chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: messageContent,
          user_context: {
            session_id: Date.now().toString(),
            timestamp: new Date().toISOString(),
          },
        }),
      });

      if (response.ok) {
        const botResponse = await response.json();
        const botMessage: Message = {
          type: 'bot',
          content: botResponse.message,
          timestamp: new Date(),
          suggestions: botResponse.suggestions,
        };
        setGeneralMessages((prev) => [...prev, botMessage]);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to send message');
      }
    } catch (err: unknown) {
      console.error('Error sending general message:', err);
      const msg =
        err instanceof Error
          ? `Sorry, I encountered an error processing your message: ${err.message}. Please try again.`
          : 'Sorry, I encountered an error processing your message. Please try again.';
      setGeneralMessages((prev) => [
        ...prev,
        { type: 'bot', content: msg, timestamp: new Date() },
      ]);
    } finally {
      setGeneralLoading(false);
    }
  };

  /** ----------------------------
   * Utilities / Handlers
   * ----------------------------- */
  const extractSkillsFromMessage = (message: string): string[] | null => {
    const lowerMessage = message.toLowerCase();
    const skillPatterns = [
      'data analyst',
      'data analysis',
      'software developer',
      'software development',
      'web developer',
      'web development',
      'digital marketing',
      'digital marketer',
      'ux designer',
      'ui designer',
      'graphic designer',
      'product manager',
      'project manager',
      'business analyst',
      'cybersecurity',
      'machine learning',
      'artificial intelligence',
      'ai',
      'python',
      'javascript',
      'java',
    ];
    for (const skill of skillPatterns) {
      if (lowerMessage.includes(skill)) {
        return [
          skill
            .split(' ')
            .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
            .join(' '),
        ];
      }
    }
    return null;
  };

  const handleJobInfoSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobInfoQuery.trim() || jobInfoLoading) return;
    sendJobInfoMessage(jobInfoQuery);
    setJobInfoQuery('');
  };

  const handleGeneralSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!generalQuery.trim() || generalLoading) return;
    sendGeneralMessage(generalQuery);
    setGeneralQuery('');
  };

  const handleJobInfoSuggestionClick = (suggestion: string) => {
    sendJobInfoMessage(suggestion);
  };

  const handleGeneralSuggestionClick = (suggestion: string) => {
    sendGeneralMessage(suggestion);
  };

  const downloadPDFReport = async () => {
    try {
      setPdfGenerating(true);
      const response = await fetch(`${API_BASE_URL}/download-pdf-report`, {
        method: 'GET',
      });
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.error || 'Failed to generate PDF report');
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `Smart_Career_SG_Report_${new Date()
        .toISOString()
        .split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setJobInfoMessages((prev) => [
        ...prev,
        {
          type: 'bot',
          content:
            'PDF report downloaded successfully! It includes your analysis, course recommendations, job market insights, and learning path.',
          timestamp: new Date(),
        },
      ]);
    } catch (err: unknown) {
      console.error('Error downloading PDF report:', err);
      const msg =
        err instanceof Error
          ? `Failed to download PDF report: ${err.message}`
          : 'Failed to download PDF report. Please try again.';
      setJobInfoMessages((prev) => [
        ...prev,
        { type: 'bot', content: msg, timestamp: new Date() },
      ]);
    } finally {
      setPdfGenerating(false);
    }
  };

  const downloadJSONReport = () => {
    try {
      if (analysisResult?.file_path || analysisResult?.data) {
        const dataToDownload = analysisResult.data || analysisResult;
        const element = document.createElement('a');
        const file = new Blob([JSON.stringify(dataToDownload, null, 2)], {
          type: 'application/json',
        });
        element.href = URL.createObjectURL(file);
        element.download = `career_analysis_data_${new Date()
          .toISOString()
          .split('T')[0]}.json`;
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
      }
    } catch (err) {
      console.error('Error downloading JSON report:', err);
    }
  };

  /** ----------------------------
   * Render helpers
   * ----------------------------- */
  const renderAnalysisProgress = () => {
    if (analysisStatus.status === 'idle') return null;
    return (
      <Card className="mb-4 border-blue-200 bg-blue-50">
        <CardContent className="p-4">
          <div className="flex items-center gap-3 mb-2">
            {analysisStatus.status === 'running' && (
              <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
            )}
            {analysisStatus.status === 'completed' && (
              <CheckCircle className="w-5 h-5 text-green-600" />
            )}
            {analysisStatus.status === 'error' && (
              <AlertCircle className="w-5 h-5 text-red-600" />
            )}
            <span className="font-medium">
              {analysisStatus.status === 'running' && 'Analysis in Progress'}
              {analysisStatus.status === 'completed' && 'Analysis Completed'}
              {analysisStatus.status === 'error' && 'Analysis Error'}
            </span>
          </div>

          {analysisStatus.status === 'running' && (
            <div className="space-y-2">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${analysisStatus.progress}%` }}
                />
              </div>
              <p className="text-sm text-gray-600">{analysisStatus.message}</p>
            </div>
          )}

          {analysisStatus.status === 'error' && (
            <p className="text-sm text-red-600">{analysisStatus.error}</p>
          )}
        </CardContent>
      </Card>
    );
  };

  const renderAnalysisResult = () => {
    if (!analysisResult) return null;
    const d = analysisResult.data || {};
    return (
      <Card className="mb-4 border-green-200 bg-green-50">
        <CardHeader>
          <CardTitle className="text-green-800">Analysis Results</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-sm text-green-700">
              Your comprehensive career analysis is complete! Here's what I found:
            </p>

            {/* Enterprise-style shape */}
            {d.course_recommendations && (
              <div className="bg-white rounded-lg p-4 border space-y-3">
                <h4 className="font-semibold mb-2">Key Insights:</h4>
                <div>
                  <h5 className="font-medium text-sm mb-1">
                    Top Course Recommendations:
                  </h5>
                  <div className="space-y-1">
                    {d.course_recommendations.slice(0, 3).map(
                      (course: any, idx: number) => (
                        <div key={idx} className="text-xs bg-gray-50 p-2 rounded">
                          <strong>{course.title}</strong> — {course.provider} (
                          {course.rating}⭐)
                        </div>
                      )
                    )}
                  </div>
                </div>
                {d.job_market_analysis && (
                  <div>
                    <h5 className="font-medium text-sm mb-1">Job Market Insights:</h5>
                    <div className="text-xs bg-gray-50 p-2 rounded">
                      <p>
                        <strong>Demand:</strong> {d.job_market_analysis.demand_level}
                      </p>
                      <p>
                        <strong>Growth:</strong> {d.job_market_analysis.growth_rate}
                      </p>
                      {d.job_market_analysis.salary_range && (
                        <p>
                          <strong>Salary Range:</strong>{' '}
                          {d.job_market_analysis.salary_range.entry_level} -{' '}
                          {d.job_market_analysis.salary_range.senior_level}
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* YouTube-agent fallback */}
            {!d.course_recommendations && d.skills_breakdown && (
              <div className="bg-white rounded-lg p-4 border space-y-3">
                <h4 className="font-semibold mb-2">Top Skills & Subskills</h4>
                <div className="text-xs bg-gray-50 p-2 rounded space-y-1">
                  {d.skills_breakdown.slice(0, 3).map((s: any, i: number) => (
                    <div key={i}>
                      <strong>{s.skill}</strong>
                      {s.subskills?.length
                        ? ` — ${s.subskills.slice(0, 4).join(', ')}`
                        : ''}
                    </div>
                  ))}
                </div>

                {d.learning_path && (
                  <div className="pt-2">
                    <h5 className="font-medium text-sm mb-1">Learning Path</h5>
                    <ol className="text-xs bg-gray-50 p-2 rounded list-decimal list-inside">
                      {d.learning_path.slice(0, 6).map((step: string, i: number) => (
                        <li key={i}>{step}</li>
                      ))}
                    </ol>
                  </div>
                )}

                {d.important_considerations &&
                  d.important_considerations.length > 0 && (
                    <div className="pt-2">
                      <h5 className="font-medium text-sm mb-1">
                        Important Considerations
                      </h5>
                      <ul className="text-xs bg-gray-50 p-2 rounded list-disc list-inside">
                        {d.important_considerations.slice(0, 5).map(
                          (c: string, i: number) => (
                            <li key={i}>{c}</li>
                          )
                        )}
                      </ul>
                    </div>
                  )}
              </div>
            )}

            {/* Downloads */}
            <div className="flex gap-2">
              <Button
                onClick={downloadPDFReport}
                disabled={pdfGenerating}
                className="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
              >
                {pdfGenerating ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Generating PDF...
                  </>
                ) : (
                  <>
                    <FileText className="w-4 h-4 mr-2" />
                    Download PDF Report
                  </>
                )}
              </Button>

              <Button
                onClick={downloadJSONReport}
                variant="outline"
                className="px-4"
                title="Download raw data as JSON"
              >
                <Download className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  /** ----------------------------
   * Page
   * ----------------------------- */
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm shadow-sm border-b border-white/20">
        <div className="max-w-6xl mx-auto px-6 py-5">
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
                <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                  Smart Career SG
                </h1>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Hero */}
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="text-center mb-12">
          <h2 className="text-5xl font-bold mb-6 bg-gradient-to-r from-gray-900 via-purple-900 to-blue-900 bg-clip-text text-transparent">
            AI Career Assistants
          </h2>
          <p className="text-xl text-gray-700 max-w-3xl mx-auto leading-relaxed">
            Choose from our specialized AI assistants to get targeted career support and
            guidance
          </p>
        </div>

        {/* Assistant cards */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200">
            <CardContent className="p-6 text-center">
              <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <Search className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Job Information Assistant
              </h3>
              <p className="text-gray-700 mb-4">
                Get detailed information about specific jobs, careers, and industry insights
              </p>
              <div className="space-y-2">
                <Badge className="bg-blue-100 text-blue-800 mr-2">Job Requirements</Badge>
                <Badge className="bg-blue-100 text-blue-800 mr-2">Career Paths</Badge>
                <Badge className="bg-blue-100 text-blue-800">Industry Insights</Badge>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-emerald-50 to-teal-50 border-2 border-emerald-200">
            <CardContent className="p-6 text-center">
              <div className="w-16 h-16 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <MessageCircle className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">General Job Support</h3>
              <p className="text-gray-700 mb-4">
                Get help with workplace questions, career development, and professional growth
              </p>
              <div className="space-y-2">
                <Badge className="bg-emerald-100 text-emerald-800 mr-2">Career Advice</Badge>
                <Badge className="bg-emerald-100 text-emerald-800 mr-2">Workplace Help</Badge>
                <Badge className="bg-emerald-100 text-emerald-800">Professional Growth</Badge>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Two-column chat layout */}
        <div className="grid lg:grid-cols-2 gap-8 mb-12">
          {/* Job Info Chat (left) */}
          <Card className="bg-white/80 backdrop-blur-sm border-2 border-blue-200 shadow-2xl">
            <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-blue-100">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg flex items-center justify-center">
                  <Search className="w-5 h-5 text-white" />
                </div>
                <CardTitle className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  Job Information Assistant
                </CardTitle>
              </div>
              <p className="text-sm text-gray-600 mt-2">
                Learn about specific jobs, career requirements, and industry insights
              </p>
            </CardHeader>
            <CardContent>
              {renderAnalysisProgress()}
              {renderAnalysisResult()}

              <div className="h-80 overflow-y-auto mb-4 p-4 bg-gray-50 rounded-lg space-y-4">
                {jobInfoMessages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        message.type === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-white border border-blue-200 text-gray-900'
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      {message.suggestions && (
                        <div className="mt-2 space-y-1">
                          {message.suggestions.map((suggestion, idx) => (
                            <button
                              key={idx}
                              onClick={() => handleJobInfoSuggestionClick(suggestion)}
                              className="block w-full text-left text-xs bg-white/20 hover:bg-white/30 rounded px-2 py-1 transition-colors"
                            >
                              {suggestion}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {jobInfoLoading && (
                  <div className="flex justify-start">
                    <div className="bg-white border border-blue-200 text-gray-900 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span className="text-sm">Analyzing your request...</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <form onSubmit={handleJobInfoSubmit} className="flex gap-2">
                <Input
                  value={jobInfoQuery}
                  onChange={(e) => setJobInfoQuery(e.target.value)}
                  placeholder="What job would you like to know about?"
                  className="flex-1 border-blue-200 focus:border-blue-400"
                  disabled={jobInfoLoading}
                />
                <Button
                  type="submit"
                  disabled={!jobInfoQuery.trim() || jobInfoLoading}
                  className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* General Support Chat (right) */}
          <Card className="bg-white/80 backdrop-blur-sm border-2 border-emerald-200 shadow-2xl">
            <CardHeader className="bg-gradient-to-r from-emerald-50 to-teal-50 border-b border-emerald-100">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-lg flex items-center justify-center">
                  <MessageCircle className="w-5 h-5 text-white" />
                </div>
                <CardTitle className="text-xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
                  General Job Support
                </CardTitle>
              </div>
              <p className="text-sm text-gray-600 mt-2">
                Get help with workplace challenges and career development
              </p>
            </CardHeader>
            <CardContent>
              <div className="h-80 overflow-y-auto mb-4 p-4 bg-gray-50 rounded-lg space-y-4">
                {generalMessages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        message.type === 'user'
                          ? 'bg-emerald-600 text-white'
                          : 'bg-white border border-emerald-200 text-gray-900'
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      {message.suggestions && (
                        <div className="mt-2 space-y-1">
                          {message.suggestions.map((suggestion, idx) => (
                            <button
                              key={idx}
                              onClick={() => handleGeneralSuggestionClick(suggestion)}
                              className="block w-full text-left text-xs bg-white/20 hover:bg-white/30 rounded px-2 py-1 transition-colors"
                            >
                              {suggestion}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {generalLoading && (
                  <div className="flex justify-start">
                    <div className="bg-white border border-emerald-200 text-gray-900 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span className="text-sm">Thinking about your question...</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <form onSubmit={handleGeneralSubmit} className="flex gap-2">
                <Input
                  value={generalQuery}
                  onChange={(e) => setGeneralQuery(e.target.value)}
                  placeholder="Ask about your career or workplace..."
                  className="flex-1 border-emerald-200 focus:border-emerald-400"
                  disabled={generalLoading}
                />
                <Button
                  type="submit"
                  disabled={!generalQuery.trim() || generalLoading}
                  className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Usage guide */}
        <Card className="bg-gradient-to-r from-gray-50 to-blue-50 border-2 border-gray-200">
          <CardContent className="p-8">
            <div className="text-center mb-6">
              <Sparkles className="w-12 h-12 text-blue-600 mx-auto mb-4" />
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                How to Use Our AI Assistants
              </h3>
              <p className="text-gray-700">
                Get the most out of your conversations with our specialized career chatbots
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h4 className="text-lg font-semibold text-blue-700 mb-4 flex items-center gap-2">
                  <Search className="w-5 h-5" />
                  Job Information Assistant
                </h4>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li className="flex items-start gap-2">
                    <span className="text-blue-500 mt-1">•</span>
                    <span>Ask about specific job titles (e.g., "Software Engineer")</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-500 mt-1">•</span>
                    <span>Learn about job requirements, qualifications, and skills</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-500 mt-1">•</span>
                    <span>Explore career progression paths and advancement opportunities</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-500 mt-1">•</span>
                    <span>Get salary insights and industry trends for specific roles</span>
                  </li>
                </ul>
              </div>

              <div>
                <h4 className="text-lg font-semibold text-emerald-700 mb-4 flex items-center gap-2">
                  <MessageCircle className="w-5 h-5" />
                  General Job Support
                </h4>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-500 mt-1">•</span>
                    <span>Ask about workplace challenges and how to handle them</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-500 mt-1">•</span>
                    <span>Get advice on career development and professional growth</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-500 mt-1">•</span>
                    <span>Discuss work-life balance and productivity strategies</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-500 mt-1">•</span>
                    <span>Seek guidance on job interviews and networking</span>
                  </li>
                </ul>
              </div>
            </div>

            <div className="mt-8 p-4 bg-white rounded-lg border border-gray-200">
              <div className="flex items-start gap-3">
                <Info className="w-5 h-5 text-blue-600 mt-1 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-gray-900 mb-1">Pro Tip:</p>
                  <p className="text-sm text-gray-700">
                    Use the <strong>Job Information Assistant</strong> to explore new career
                    options, and <strong>General Job Support</strong> for help with your
                    current job situation.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
