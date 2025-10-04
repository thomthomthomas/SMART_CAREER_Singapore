import { Routes, Route, Navigate } from 'react-router-dom';
import { HomePage } from './components/HomePage';
import { ExistingPage } from './components/ExistingPage';
import { NewPage } from './components/NewPage';

// Careers pages
import CareerHub from './pages/CareerHub';
import RoleDetails from './pages/RoleDetails';

// Course Creation page
import CourseCreation from './pages/CourseCreation';

export default function App() {
  return (
    <div className="min-h-screen bg-background">
      <Routes>
        {/* Existing routes */}
        <Route path="/" element={<HomePage />} />
        <Route path="/existing" element={<ExistingPage />} />
        <Route path="/new" element={<NewPage />} />

        {/* Career Information Hub */}
        <Route path="/careers" element={<CareerHub />} />
        <Route path="/careers/:slug" element={<RoleDetails />} />

        {/* Course Creation */}
        <Route path="/course-creation" element={<CourseCreation />} />

        {/* Catch-all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}
