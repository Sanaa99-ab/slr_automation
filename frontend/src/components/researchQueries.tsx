// researchqueries.tsx
import React from 'react';
import './researchQueries.css';

interface ResearchQueriesProps {
  data: string[];
}

const ResearchQueries: React.FC<ResearchQueriesProps> = ({ data }) => {
  return (
    <div className="research-queries">
      {data.map((query, index) => (
        <div key={index} className="query-item">
          {query}
        </div>
      ))}
    </div>
  );
};

export default ResearchQueries;
