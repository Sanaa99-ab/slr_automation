// researchquestions.tsx
import React from 'react';
import './researchQuestions.css';

interface ResearchQuestionsProps {
  data: string[];
}

const ResearchQuestions: React.FC<ResearchQuestionsProps> = ({ data }) => {
  return (
    <div className="research-questions">
      {data.map((question, index) => (
        <div key={index} className="question-item">
          {question}
        </div>
      ))}
    </div>
  );
};

export default ResearchQuestions;
