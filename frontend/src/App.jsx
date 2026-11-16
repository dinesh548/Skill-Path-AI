import React, { useState } from 'react';
import { Layout } from './components/Layout';
import { OverviewPage } from './pages/OverviewPage';
import { EmployeesPage } from './pages/EmployeesPage';
import { SkillGapPage } from './pages/SkillGapPage';
import { CoursesPage } from './pages/CoursesPage';
import { RecommendationsPage } from './pages/RecommendationsPage';
import { EnrollmentsPage } from './pages/EnrollmentsPage';
import { BudgetsPage } from './pages/BudgetsPage';
import { ExceptionsPage } from './pages/ExceptionsPage';
import { CareerPathwaysPage } from './pages/CareerPathwaysPage';
import { ReportsPage } from './pages/ReportsPage';

export function App() {
  const [activePage, setActivePage] = useState('overview');
  const [targetEmployeeId, setTargetEmployeeId] = useState(null);

  const handleNavigateToRecommendations = (empId) => {
    setTargetEmployeeId(empId);
    setActivePage('recommendations');
  };

  const handleNavigateToCareer = (empId) => {
    setTargetEmployeeId(empId);
    setActivePage('career-pathways');
  };

  const handleNavigateToEnrollments = () => {
    setActivePage('enrollments');
  };

  const renderPage = () => {
    switch (activePage) {
      case 'overview':
        return <OverviewPage />;
      case 'employees':
        return (
          <EmployeesPage
            onNavigateToRecommendations={handleNavigateToRecommendations}
            onNavigateToCareer={handleNavigateToCareer}
          />
        );
      case 'skill-gaps':
        return <SkillGapPage />;
      case 'courses':
        return <CoursesPage />;
      case 'recommendations':
        return (
          <RecommendationsPage
            initialEmployeeId={targetEmployeeId}
            onNavigateToEnrollments={handleNavigateToEnrollments}
          />
        );
      case 'enrollments':
        return <EnrollmentsPage />;
      case 'budgets':
        return <BudgetsPage />;
      case 'exceptions':
        return <ExceptionsPage />;
      case 'career-pathways':
        return (
          <CareerPathwaysPage
            initialEmployeeId={targetEmployeeId}
            onNavigateToRecommendations={handleNavigateToRecommendations}
          />
        );
      case 'reports':
        return <ReportsPage />;
      default:
        return <OverviewPage />;
    }
  };

  return (
    <Layout activePage={activePage} setActivePage={setActivePage}>
      {renderPage()}
    </Layout>
  );
}

export default App;
