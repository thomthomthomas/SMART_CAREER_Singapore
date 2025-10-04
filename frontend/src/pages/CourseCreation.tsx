import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { 
  ArrowLeft, 
  TreePine, 
  Loader2, 
  CheckCircle, 
  Download,
  Search,
  Plus,
  Minus
} from 'lucide-react';

interface Skill {
  id: string;
  name: string;
  category: string;
  difficulty: string;
  description: string;
}

interface SkillsTreeData {
  topic: string;
  skills: Skill[];
}

type Step = 'input' | 'skills-tree' | 'modules' | 'summary';

export default function CourseCreation() {
  const [currentStep, setCurrentStep] = useState<Step>('input');
  const [topic, setTopic] = useState('');
  const [description, setDescription] = useState('');
  const [skillsTree, setSkillsTree] = useState<SkillsTreeData | null>(null);
  const [selectedSkills, setSelectedSkills] = useState<Skill[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [courseSummary, setCourseSummary] = useState('');
  const [estimatedDuration, setEstimatedDuration] = useState('');

  const handleGenerateSkillsTree = async () => {
    if (!topic.trim()) return;
    
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/generate-skills-tree', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: topic.trim(),
          description: description.trim()
        }),
      });

      const data = await response.json();
      if (data.success) {
        setSkillsTree(data.skills_tree);
        setCurrentStep('skills-tree');
      } else {
        alert('Failed to generate skills tree: ' + data.error);
      }
    } catch (error) {
      console.error('Error generating skills tree:', error);
      alert('Failed to generate skills tree. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSkillToggle = (skill: Skill) => {
    setSelectedSkills(prev => {
      const isSelected = prev.some(s => s.id === skill.id);
      if (isSelected) {
        return prev.filter(s => s.id !== skill.id);
      } else {
        if (prev.length >= 10) {
          alert('You can select a maximum of 10 skills.');
          return prev;
        }
        return [...prev, skill];
      }
    });
  };

  const handleCreateCourse = async () => {
    if (selectedSkills.length === 0) {
      alert('Please select at least one skill.');
      return;
    }

    setIsLoading(true);
    setCurrentStep('modules');

    try {
      // First, get the course summary
      const summaryResponse = await fetch('http://localhost:5000/api/course-summary', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic,
          selected_skills: selectedSkills
        }),
      });

      const summaryData = await summaryResponse.json();
      if (summaryData.success) {
        setCourseSummary(summaryData.summary);
        setEstimatedDuration(summaryData.estimated_duration);
      }

      // Then, generate the PDF
      const pdfResponse = await fetch('http://localhost:5000/api/create-course', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic,
          selected_skills: selectedSkills
        }),
      });

      if (pdfResponse.ok) {
        const blob = await pdfResponse.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `${topic.toLowerCase().replace(/\s+/g, '_')}_learning_course.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        setCurrentStep('summary');
      } else {
        alert('Failed to generate course PDF. Please try again.');
      }
    } catch (error) {
      console.error('Error creating course:', error);
      alert('Failed to create course. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const getStepNumber = (step: Step): number => {
    const steps: Step[] = ['input', 'skills-tree', 'modules', 'summary'];
    return steps.indexOf(step) + 1;
  };

  const getStepTitle = (step: Step): string => {
    switch (step) {
      case 'input': return 'Input';
      case 'skills-tree': return 'Skills Tree';
      case 'modules': return 'Modules';
      case 'summary': return 'Summary';
    }
  };

  const groupSkillsByCategory = (skills: Skill[]) => {
    return skills.reduce((acc, skill) => {
      if (!acc[skill.category]) {
        acc[skill.category] = [];
      }
      acc[skill.category].push(skill);
      return acc;
    }, {} as Record<string, Skill[]>);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50">
      {/* Header */}
      <header className="w-full py-6 px-4 bg-white/80 backdrop-blur-sm border-b border-orange-200">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link to="/" className="flex items-center gap-2 text-orange-600 hover:text-orange-700 transition-colors">
              <ArrowLeft className="w-5 h-5" />
              <span>Back to Home</span>
            </Link>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-amber-500 rounded-xl flex items-center justify-center">
                <TreePine className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900">Course Creation</h1>
            </div>
          </div>
          
          {/* Progress Steps */}
          <div className="flex items-center gap-4">
            {(['input', 'skills-tree', 'modules', 'summary'] as Step[]).map((step, index) => (
              <div key={step} className="flex items-center gap-2">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                  getStepNumber(currentStep) > index + 1 
                    ? 'bg-green-500 text-white' 
                    : getStepNumber(currentStep) === index + 1
                    ? 'bg-orange-500 text-white'
                    : 'bg-gray-200 text-gray-500'
                }`}>
                  {getStepNumber(currentStep) > index + 1 ? <CheckCircle className="w-4 h-4" /> : index + 1}
                </div>
                <span className={`text-sm font-medium ${
                  getStepNumber(currentStep) >= index + 1 ? 'text-gray-900' : 'text-gray-500'
                }`}>
                  {getStepTitle(step)}
                </span>
                {index < 3 && <div className="w-8 h-px bg-gray-300" />}
              </div>
            ))}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-12">
        {/* Step 1: Input */}
        {currentStep === 'input' && (
          <div className="max-w-2xl mx-auto">
            <div className="text-center mb-12">
              <div className="w-20 h-20 bg-gradient-to-r from-orange-500 to-amber-500 rounded-3xl flex items-center justify-center mx-auto mb-6">
                <TreePine className="w-10 h-10 text-white" />
              </div>
              <h2 className="text-4xl font-bold mb-4 text-gray-900">Start Your Learning Journey</h2>
              <p className="text-lg text-gray-600">
                Enter a skill or course topic you'd like to explore. Our AI will generate 
                an interactive skills tree to help you build a comprehensive learning path.
              </p>
            </div>

            <Card className="bg-white/80 backdrop-blur-sm border-2 border-orange-200">
              <CardHeader>
                <CardTitle className="text-center text-orange-600">What Would You Like to Learn?</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="topic" className="text-sm font-medium text-gray-700">
                    Enter a skill, topic, or field of study:
                  </Label>
                  <Input
                    id="topic"
                    placeholder="e.g., Web Development, Data Science, Digital Marketing..."
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    className="text-lg py-3"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description" className="text-sm font-medium text-gray-700">
                    Additional context (optional):
                  </Label>
                  <Input
                    id="description"
                    placeholder="e.g., I want to focus on business applications, beginner level..."
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    className="py-3"
                  />
                </div>

                <Button 
                  onClick={handleGenerateSkillsTree}
                  disabled={!topic.trim() || isLoading}
                  className="w-full py-4 text-lg font-semibold bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700 transition-all duration-300"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Generating Skills Tree...
                    </>
                  ) : (
                    <>
                      <Search className="w-5 h-5 mr-2" />
                      Generate Skills Tree
                    </>
                  )}
                </Button>

                {/* Popular Topics */}
                <div className="pt-6">
                  <h3 className="text-sm font-medium text-gray-700 mb-3">Popular Topics</h3>
                  <div className="flex flex-wrap gap-2">
                    {[
                      'Web Development', 'Data Science', 'Digital Marketing', 
                      'UX/UI Design', 'Machine Learning', 'Mobile Development',
                      'Cybersecurity', 'Cloud Computing'
                    ].map((popularTopic) => (
                      <Badge 
                        key={popularTopic}
                        variant="secondary" 
                        className="cursor-pointer hover:bg-orange-100 hover:text-orange-700 transition-colors"
                        onClick={() => setTopic(popularTopic)}
                      >
                        {popularTopic}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Tips */}
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                  <h4 className="font-medium text-orange-800 mb-2">💡 Tips for Best Results</h4>
                  <ul className="text-sm text-orange-700 space-y-1">
                    <li>• Be specific but not too narrow (e.g., "React Development" vs "Programming")</li>
                    <li>• Include your intended application (e.g., "Web Development for E-commerce")</li>
                    <li>• Combine related fields for comprehensive learning (e.g., "Data Science and Machine Learning")</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Step 2: Skills Tree */}
        {currentStep === 'skills-tree' && skillsTree && (
          <div>
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold mb-4 text-gray-900">
                Skills Tree for "{skillsTree.topic}"
              </h2>
              <p className="text-lg text-gray-600">
                Click on skills to add them to your learning path. Drag to pan and use controls to zoom.
              </p>
            </div>

            {/* Skills Grid */}
            <div className="grid gap-6 mb-8">
              {Object.entries(groupSkillsByCategory(skillsTree.skills)).map(([category, skills]) => (
                <Card key={category} className="bg-white/80 backdrop-blur-sm border-2 border-orange-200">
                  <CardHeader>
                    <CardTitle className="text-xl text-orange-600">{category}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
                      {skills.map((skill) => {
                        const isSelected = selectedSkills.some(s => s.id === skill.id);
                        return (
                          <div
                            key={skill.id}
                            onClick={() => handleSkillToggle(skill)}
                            className={`p-4 rounded-lg border-2 cursor-pointer transition-all duration-200 ${
                              isSelected
                                ? 'border-orange-500 bg-orange-50 shadow-md'
                                : 'border-gray-200 bg-white hover:border-orange-300 hover:shadow-sm'
                            }`}
                          >
                            <div className="flex items-start justify-between mb-2">
                              <h4 className="font-semibold text-gray-900">{skill.name}</h4>
                              {isSelected ? (
                                <Minus className="w-5 h-5 text-orange-600 flex-shrink-0" />
                              ) : (
                                <Plus className="w-5 h-5 text-gray-400 flex-shrink-0" />
                              )}
                            </div>
                            <Badge variant="outline" className="mb-2">
                              {skill.difficulty}
                            </Badge>
                            <p className="text-sm text-gray-600">{skill.description}</p>
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Selected Skills */}
            <Card className="bg-white/80 backdrop-blur-sm border-2 border-orange-200 mb-8">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Selected Skills ({selectedSkills.length})</span>
                  <span className="text-sm font-normal text-gray-600">
                    Maximum 10 skills
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {selectedSkills.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">
                    Click on skills in the tree to add them to your learning path.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {selectedSkills.map((skill, index) => (
                      <div key={skill.id} className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                        <div>
                          <span className="font-medium text-gray-900">{index + 1}. {skill.name}</span>
                          <span className="text-sm text-gray-600 ml-2">({skill.category})</span>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleSkillToggle(skill)}
                          className="text-orange-600 hover:text-orange-700"
                        >
                          <Minus className="w-4 h-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Action Buttons */}
            <div className="flex justify-between">
              <Button
                variant="outline"
                onClick={() => setCurrentStep('input')}
                className="border-orange-300 text-orange-600 hover:bg-orange-50"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Input
              </Button>
              <Button
                onClick={handleCreateCourse}
                disabled={selectedSkills.length === 0 || isLoading}
                className="bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Creating Course...
                  </>
                ) : (
                  <>
                    Create Modules
                    <ArrowLeft className="w-4 h-4 ml-2 rotate-180" />
                  </>
                )}
              </Button>
            </div>
          </div>
        )}

        {/* Step 3: Modules (Loading) */}
        {currentStep === 'modules' && (
          <div className="max-w-2xl mx-auto text-center">
            <div className="mb-8">
              <div className="w-20 h-20 bg-gradient-to-r from-orange-500 to-amber-500 rounded-3xl flex items-center justify-center mx-auto mb-6">
                <Loader2 className="w-10 h-10 text-white animate-spin" />
              </div>
              <h2 className="text-3xl font-bold mb-4 text-gray-900">Generating Your Course</h2>
              <p className="text-lg text-gray-600 mb-8">
                Please wait while we create your personalized learning modules...
              </p>
            </div>

            {courseSummary && (
              <Card className="bg-white/80 backdrop-blur-sm border-2 border-orange-200 text-left">
                <CardHeader>
                  <CardTitle className="text-orange-600">Course Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 mb-4">{courseSummary}</p>
                  <div className="flex justify-between text-sm text-gray-600">
                    <span><strong>Skills:</strong> {selectedSkills.length}</span>
                    <span><strong>Estimated Duration:</strong> {estimatedDuration}</span>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Step 4: Summary */}
        {currentStep === 'summary' && (
          <div className="max-w-2xl mx-auto text-center">
            <div className="mb-8">
              <div className="w-20 h-20 bg-gradient-to-r from-green-500 to-emerald-500 rounded-3xl flex items-center justify-center mx-auto mb-6">
                <CheckCircle className="w-10 h-10 text-white" />
              </div>
              <h2 className="text-3xl font-bold mb-4 text-gray-900">Course Created Successfully!</h2>
              <p className="text-lg text-gray-600">
                Your personalized learning course has been generated and downloaded.
              </p>
            </div>

            <Card className="bg-white/80 backdrop-blur-sm border-2 border-green-200 mb-8">
              <CardHeader>
                <CardTitle className="text-green-600">What's Next?</CardTitle>
              </CardHeader>
              <CardContent className="text-left space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-semibold text-green-600">1</span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">Review Your Course PDF</h4>
                    <p className="text-sm text-gray-600">
                      The downloaded PDF contains detailed modules for your top 2 selected skills with practical exercises.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-semibold text-green-600">2</span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">Follow the Learning Pathway</h4>
                    <p className="text-sm text-gray-600">
                      Start with the recommended learning sequence outlined in your course guide.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-semibold text-green-600">3</span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">Practice and Apply</h4>
                    <p className="text-sm text-gray-600">
                      Complete the practice exercises and build projects to reinforce your learning.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <div className="flex gap-4 justify-center">
              <Button
                onClick={() => {
                  setCurrentStep('input');
                  setTopic('');
                  setDescription('');
                  setSkillsTree(null);
                  setSelectedSkills([]);
                  setCourseSummary('');
                  setEstimatedDuration('');
                }}
                variant="outline"
                className="border-orange-300 text-orange-600 hover:bg-orange-50"
              >
                Create Another Course
              </Button>
              <Link to="/">
                <Button className="bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700">
                  Return to Home
                </Button>
              </Link>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

